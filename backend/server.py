from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import logging
import uuid
import asyncio
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path
from dotenv import load_dotenv
import random
import threading
import time

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Smart Industrial Energy Monitoring System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str = "engineer"  # engineer, manager, admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    role: str = "engineer"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class Device(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # motor, compressor, hvac, conveyor
    location: str
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DeviceCreate(BaseModel):
    name: str
    type: str
    location: str

class SensorReading(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    power_kw: float
    temperature_c: float
    vibration: float
    runtime_hours: float

class SensorIngest(BaseModel):
    device_id: str
    power_kw: float
    temperature_c: float
    vibration: float
    runtime_hours: float

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    alert_type: str  # threshold_exceeded, anomaly_detected
    metric: str  # power_kw, temperature_c, vibration
    value: float
    threshold: float
    severity: str  # low, medium, high, critical
    message: str
    acknowledged: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AlertAck(BaseModel):
    alert_id: str

class ThresholdConfig(BaseModel):
    device_id: str
    metric: str
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return User(**user)

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Anomaly Detection Class
class AnomalyDetector:
    def __init__(self):
        self.models = {}
        self.thresholds = {
            'motor': {'power_kw': (0.5, 50), 'temperature_c': (20, 80), 'vibration': (0, 5)},
            'compressor': {'power_kw': (2, 100), 'temperature_c': (25, 90), 'vibration': (0, 8)},
            'hvac': {'power_kw': (1, 75), 'temperature_c': (18, 35), 'vibration': (0, 3)},
            'conveyor': {'power_kw': (0.2, 25), 'temperature_c': (20, 60), 'vibration': (0, 4)}
        }
    
    async def check_thresholds(self, reading: SensorReading, device_type: str):
        alerts = []
        device_thresholds = self.thresholds.get(device_type, {})
        
        for metric, (min_val, max_val) in device_thresholds.items():
            value = getattr(reading, metric)
            severity = "low"
            
            if value < min_val or value > max_val:
                # Determine severity based on how far from threshold
                if value < min_val:
                    deviation = (min_val - value) / min_val
                else:
                    deviation = (value - max_val) / max_val
                
                if deviation > 0.5:
                    severity = "critical"
                elif deviation > 0.3:
                    severity = "high"
                elif deviation > 0.1:
                    severity = "medium"
                
                threshold = max_val if value > max_val else min_val
                alert = Alert(
                    device_id=reading.device_id,
                    alert_type="threshold_exceeded",
                    metric=metric,
                    value=value,
                    threshold=threshold,
                    severity=severity,
                    message=f"{metric} {value:.2f} exceeded threshold {threshold:.2f}"
                )
                alerts.append(alert)
        
        return alerts

anomaly_detector = AnomalyDetector()

# Industrial Equipment Simulator
class EquipmentSimulator:
    def __init__(self):
        self.devices = []
        self.running = False
        
    async def initialize_devices(self):
        # Create default industrial devices if they don't exist
        device_configs = [
            {"name": "Motor-A1", "type": "motor", "location": "Production Line 1"},
            {"name": "Motor-B2", "type": "motor", "location": "Production Line 2"},
            {"name": "Compressor-C1", "type": "compressor", "location": "Air Supply Room"},
            {"name": "HVAC-H1", "type": "hvac", "location": "Main Building"},
            {"name": "HVAC-H2", "type": "hvac", "location": "Warehouse"},
            {"name": "Conveyor-CV1", "type": "conveyor", "location": "Packaging Area"},
            {"name": "Conveyor-CV2", "type": "conveyor", "location": "Shipping Area"},
        ]
        
        for config in device_configs:
            existing = await db.devices.find_one({"name": config["name"]})
            if not existing:
                device = Device(**config)
                await db.devices.insert_one(device.dict())
                self.devices.append(device)
        
        # Load existing devices
        devices = await db.devices.find().to_list(1000)
        self.devices = [Device(**device) for device in devices]
    
    def generate_reading(self, device: Device):
        base_values = {
            'motor': {'power_kw': 25, 'temperature_c': 65, 'vibration': 2.5, 'runtime_hours': 8},
            'compressor': {'power_kw': 45, 'temperature_c': 75, 'vibration': 4, 'runtime_hours': 12},
            'hvac': {'power_kw': 35, 'temperature_c': 22, 'vibration': 1.5, 'runtime_hours': 16},
            'conveyor': {'power_kw': 12, 'temperature_c': 45, 'vibration': 2, 'runtime_hours': 10}
        }
        
        base = base_values.get(device.type, base_values['motor'])
        
        # Add realistic variations and occasional anomalies
        anomaly_chance = 0.05  # 5% chance of anomaly
        
        if random.random() < anomaly_chance:
            # Generate anomaly
            anomaly_factor = random.uniform(1.5, 3.0)
            power_kw = base['power_kw'] * anomaly_factor
            temperature_c = base['temperature_c'] * random.uniform(1.2, 1.8)
            vibration = base['vibration'] * random.uniform(2.0, 4.0)
        else:
            # Normal operation with small variations
            power_kw = base['power_kw'] * random.uniform(0.8, 1.2)
            temperature_c = base['temperature_c'] * random.uniform(0.9, 1.1)
            vibration = base['vibration'] * random.uniform(0.7, 1.3)
        
        runtime_hours = base['runtime_hours'] * random.uniform(0.95, 1.05)
        
        return SensorReading(
            device_id=device.id,
            power_kw=round(power_kw, 2),
            temperature_c=round(temperature_c, 1),
            vibration=round(vibration, 2),
            runtime_hours=round(runtime_hours, 1)
        )
    
    async def simulate_data(self):
        while self.running:
            try:
                for device in self.devices:
                    reading = self.generate_reading(device)
                    
                    # Store reading
                    await db.sensor_readings.insert_one(reading.dict())
                    
                    # Check for anomalies
                    alerts = await anomaly_detector.check_thresholds(reading, device.type)
                    
                    # Store alerts
                    for alert in alerts:
                        await db.alerts.insert_one(alert.dict())
                    
                    # Broadcast real-time data
                    await manager.broadcast({
                        "type": "sensor_reading",
                        "data": reading.dict(),
                        "device_name": device.name
                    })
                    
                    if alerts:
                        await manager.broadcast({
                            "type": "alert",
                            "data": [alert.dict() for alert in alerts]
                        })
                
                await asyncio.sleep(5)  # Generate data every 5 seconds
                
            except Exception as e:
                logging.error(f"Simulation error: {e}")
                await asyncio.sleep(1)

simulator = EquipmentSimulator()

# API Routes
@api_router.post("/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict['password']
    user_dict['hashed_password'] = hashed_password
    
    user = User(**user_dict)
    await db.users.insert_one({**user.dict(), 'hashed_password': hashed_password})
    return user

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user['role'],
        username=user['username']
    )

@api_router.get("/devices", response_model=List[Device])
async def get_devices(current_user: User = Depends(get_current_user)):
    devices = await db.devices.find().to_list(1000)
    return [Device(**device) for device in devices]

@api_router.post("/devices", response_model=Device)
async def create_device(device_data: DeviceCreate, current_user: User = Depends(require_role(["admin", "manager"]))):
    device = Device(**device_data.dict())
    await db.devices.insert_one(device.dict())
    return device

@api_router.post("/sensor-ingest")
async def ingest_sensor_data(readings: List[SensorIngest], current_user: User = Depends(get_current_user)):
    for reading_data in readings:
        reading = SensorReading(**reading_data.dict())
        await db.sensor_readings.insert_one(reading.dict())
        
        # Get device type for anomaly detection
        device = await db.devices.find_one({"id": reading.device_id})
        if device:
            alerts = await anomaly_detector.check_thresholds(reading, device['type'])
            for alert in alerts:
                await db.alerts.insert_one(alert.dict())
    
    return {"message": f"Ingested {len(readings)} sensor readings"}

@api_router.get("/metrics")
async def get_metrics(
    device_id: Optional[str] = None,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if device_id:
        query["device_id"] = device_id
    if from_time:
        query["timestamp"] = {"$gte": from_time}
    if to_time:
        query.setdefault("timestamp", {})["$lte"] = to_time
    
    readings = await db.sensor_readings.find(query).sort("timestamp", -1).limit(1000).to_list(1000)
    return [SensorReading(**reading) for reading in readings]

@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    device_id: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if device_id:
        query["device_id"] = device_id
    if acknowledged is not None:
        query["acknowledged"] = acknowledged
    
    alerts = await db.alerts.find(query).sort("timestamp", -1).limit(100).to_list(100)
    return [Alert(**alert) for alert in alerts]

@api_router.post("/alerts/acknowledge")
async def acknowledge_alert(alert_ack: AlertAck, current_user: User = Depends(get_current_user)):
    result = await db.alerts.update_one(
        {"id": alert_ack.alert_id},
        {"$set": {"acknowledged": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert acknowledged"}

@api_router.get("/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    # Get device count
    device_count = await db.devices.count_documents({})
    
    # Get active alerts
    active_alerts = await db.alerts.count_documents({"acknowledged": False})
    
    # Get latest readings
    latest_readings = await db.sensor_readings.find().sort("timestamp", -1).limit(10).to_list(10)
    
    # Calculate average power consumption
    if latest_readings:
        avg_power = sum(reading['power_kw'] for reading in latest_readings) / len(latest_readings)
    else:
        avg_power = 0
    
    return {
        "device_count": device_count,
        "active_alerts": active_alerts,
        "avg_power_kw": round(avg_power, 2),
        "system_status": "operational"
    }

@api_router.post("/simulation/start")
async def start_simulation(current_user: User = Depends(require_role(["admin", "manager"]))):
    if not simulator.running:
        await simulator.initialize_devices()
        simulator.running = True
        # Start simulation in background
        asyncio.create_task(simulator.simulate_data())
        return {"message": "Simulation started"}
    return {"message": "Simulation already running"}

@api_router.post("/simulation/stop")
async def stop_simulation(current_user: User = Depends(require_role(["admin", "manager"]))):
    simulator.running = False
    return {"message": "Simulation stopped"}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle websocket messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Smart Industrial Energy Monitoring System starting up...")
    # Create default admin user if not exists
    admin_user = await db.users.find_one({"username": "admin"})
    if not admin_user:
        admin_data = UserCreate(
            username="admin",
            password="admin123",
            email="admin@company.com",
            role="admin"
        )
        hashed_password = get_password_hash(admin_data.password)
        user_dict = admin_data.dict()
        del user_dict['password']
        user_dict['hashed_password'] = hashed_password
        user = User(**user_dict)
        await db.users.insert_one({**user.dict(), 'hashed_password': hashed_password})
        logger.info("Default admin user created (admin/admin123)")

@app.on_event("shutdown")
async def shutdown_db_client():
    simulator.running = False
    client.close()