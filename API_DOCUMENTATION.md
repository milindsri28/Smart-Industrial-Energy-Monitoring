# Smart Industrial Energy Monitoring System - API Documentation

## Base URL
```
Production: https://energymonitor-1.preview.emergentagent.com/api
Development: http://localhost:8001/api
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "engineer1",
  "password": "secure123",
  "email": "engineer@company.com",
  "role": "engineer"
}
```

**Response (200)**:
```json
{
  "id": "uuid-string",
  "username": "engineer1",
  "email": "engineer@company.com",
  "role": "engineer",
  "created_at": "2025-01-16T10:00:00Z"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "admin",
  "username": "admin"
}
```

## 🏭 Device Management

### List All Devices
```http
GET /devices
Authorization: Bearer <token>
```

**Response (200)**:
```json
[
  {
    "id": "device-uuid-1",
    "name": "Motor-A1",
    "type": "motor",
    "location": "Production Line 1",
    "status": "active",
    "created_at": "2025-01-16T09:00:00Z"
  },
  {
    "id": "device-uuid-2",
    "name": "Compressor-C1",
    "type": "compressor",
    "location": "Air Supply Room",
    "status": "active",
    "created_at": "2025-01-16T09:00:00Z"
  }
]
```

### Create Device
```http
POST /devices
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Motor-A3",
  "type": "motor",
  "location": "Production Line 3"
}
```

**Permissions**: Admin, Manager only

**Response (200)**:
```json
{
  "id": "new-device-uuid",
  "name": "Motor-A3",
  "type": "motor",
  "location": "Production Line 3",
  "status": "active",
  "created_at": "2025-01-16T10:00:00Z"
}
```

**Device Types**:
- `motor` - Industrial motors and drives
- `compressor` - Air compressors and pumps
- `hvac` - Heating, ventilation, and air conditioning
- `conveyor` - Conveyor belts and transport systems

## 📊 Sensor Data & Metrics

### Ingest Sensor Data
```http
POST /sensor-ingest
Authorization: Bearer <token>
Content-Type: application/json

[
  {
    "device_id": "device-uuid-1",
    "power_kw": 25.5,
    "temperature_c": 68.2,
    "vibration": 2.1,
    "runtime_hours": 8.5
  },
  {
    "device_id": "device-uuid-2",
    "power_kw": 45.8,
    "temperature_c": 75.3,
    "vibration": 3.8,
    "runtime_hours": 12.2
  }
]
```

**Response (200)**:
```json
{
  "message": "Ingested 2 sensor readings"
}
```

### Retrieve Metrics
```http
GET /metrics?device_id=device-uuid-1&from_time=2025-01-16T00:00:00Z&to_time=2025-01-16T23:59:59Z
Authorization: Bearer <token>
```

**Query Parameters**:
- `device_id` (optional): Filter by specific device
- `from_time` (optional): Start time (ISO 8601 format)
- `to_time` (optional): End time (ISO 8601 format)

**Response (200)**:
```json
[
  {
    "id": "reading-uuid-1",
    "device_id": "device-uuid-1",
    "timestamp": "2025-01-16T10:15:00Z",
    "power_kw": 25.5,
    "temperature_c": 68.2,
    "vibration": 2.1,
    "runtime_hours": 8.5
  },
  {
    "id": "reading-uuid-2",
    "device_id": "device-uuid-1",
    "timestamp": "2025-01-16T10:20:00Z", 
    "power_kw": 26.1,
    "temperature_c": 69.0,
    "vibration": 2.3,
    "runtime_hours": 8.6
  }
]
```

## 🚨 Alert Management

### Get Alerts
```http
GET /alerts?device_id=device-uuid-1&acknowledged=false
Authorization: Bearer <token>
```

**Query Parameters**:
- `device_id` (optional): Filter by specific device
- `acknowledged` (optional): Filter by acknowledgment status

**Response (200)**:
```json
[
  {
    "id": "alert-uuid-1",
    "device_id": "device-uuid-1",
    "alert_type": "threshold_exceeded",
    "metric": "power_kw",
    "value": 55.8,
    "threshold": 50.0,
    "severity": "high",
    "message": "power_kw 55.80 exceeded threshold 50.00",
    "acknowledged": false,
    "timestamp": "2025-01-16T10:15:00Z"
  }
]
```

**Alert Severity Levels**:
- `low` - Minor deviation from normal parameters
- `medium` - Moderate concern requiring attention
- `high` - Significant issue needing prompt action
- `critical` - Emergency situation requiring immediate response

### Acknowledge Alert
```http
POST /alerts/acknowledge
Authorization: Bearer <token>
Content-Type: application/json

{
  "alert_id": "alert-uuid-1"
}
```

**Response (200)**:
```json
{
  "message": "Alert acknowledged"
}
```

## 🎮 Simulation Control

### Start Simulation
```http
POST /simulation/start
Authorization: Bearer <token>
```

**Permissions**: Admin, Manager only

**Response (200)**:
```json
{
  "message": "Simulation started"
}
```

### Stop Simulation
```http
POST /simulation/stop
Authorization: Bearer <token>
```

**Permissions**: Admin, Manager only

**Response (200)**:
```json
{
  "message": "Simulation stopped"
}
```

## 📈 Dashboard & Analytics

### Dashboard Summary
```http
GET /dashboard/summary
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "device_count": 7,
  "active_alerts": 3,
  "avg_power_kw": 32.5,
  "system_status": "operational"
}
```

## 🔄 WebSocket Real-time Data

### WebSocket Connection
```
WSS: wss://energymonitor-1.preview.emergentagent.com/ws
WS (dev): ws://localhost:8001/ws
```

### Message Types

**Sensor Reading Update**:
```json
{
  "type": "sensor_reading",
  "data": {
    "id": "reading-uuid",
    "device_id": "device-uuid-1",
    "timestamp": "2025-01-16T10:15:00Z",
    "power_kw": 25.5,
    "temperature_c": 68.2,
    "vibration": 2.1,
    "runtime_hours": 8.5
  },
  "device_name": "Motor-A1"
}
```

**Alert Notification**:
```json
{
  "type": "alert",
  "data": [
    {
      "id": "alert-uuid",
      "device_id": "device-uuid-1",
      "alert_type": "threshold_exceeded",
      "metric": "temperature_c",
      "value": 85.2,
      "threshold": 80.0,
      "severity": "high",
      "message": "temperature_c 85.20 exceeded threshold 80.00",
      "acknowledged": false,
      "timestamp": "2025-01-16T10:15:00Z"
    }
  ]
}
```

## 🔧 Equipment Thresholds

### Default Threshold Configuration

| Equipment Type | Power (kW) | Temperature (°C) | Vibration |
|----------------|------------|------------------|-----------|
| **Motor** | 0.5 - 50 | 20 - 80 | 0 - 5 |
| **Compressor** | 2 - 100 | 25 - 90 | 0 - 8 |
| **HVAC** | 1 - 75 | 18 - 35 | 0 - 3 |
| **Conveyor** | 0.2 - 25 | 20 - 60 | 0 - 4 |

### Anomaly Detection Logic

1. **Threshold Check**: Values outside configured ranges trigger alerts
2. **Severity Calculation**: Based on deviation percentage from threshold
   - **Low**: 0-10% deviation
   - **Medium**: 10-30% deviation  
   - **High**: 30-50% deviation
   - **Critical**: >50% deviation
3. **Real-time Processing**: Alerts generated immediately upon threshold breach

## 📝 Error Responses

### Authentication Errors
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### Authorization Errors
```json
{
  "detail": "Not enough permissions",
  "status_code": 403
}
```

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "power_kw"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422
}
```

### Resource Not Found
```json
{
  "detail": "Alert not found",
  "status_code": 404
}
```

## 🔨 Testing Examples

### Using cURL

**Login:**
```bash
curl -X POST "https://energymonitor-1.preview.emergentagent.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Get Devices:**
```bash
curl -X GET "https://energymonitor-1.preview.emergentagent.com/api/devices" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Start Simulation:**
```bash
curl -X POST "https://energymonitor-1.preview.emergentagent.com/api/simulation/start" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Python requests

```python
import requests

# Login
response = requests.post(
    "https://energymonitor-1.preview.emergentagent.com/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Get devices
headers = {"Authorization": f"Bearer {token}"}
devices = requests.get(
    "https://energymonitor-1.preview.emergentagent.com/api/devices",
    headers=headers
).json()

print(f"Found {len(devices)} devices")
```

## 🚀 Rate Limits

- **Authentication**: 10 requests per minute per IP
- **Data Ingestion**: 1000 requests per minute per user
- **Dashboard APIs**: 100 requests per minute per user
- **WebSocket**: 1 connection per user session

## 📋 API Changelog

### Version 1.0.0 (Current)
- Initial release with core functionality
- Authentication and user management
- Device management and sensor data ingestion
- Real-time monitoring and alerts
- Dashboard analytics
- WebSocket real-time updates

### Planned Features (v1.1.0)
- Historical data export
- Custom threshold configuration
- Advanced ML model integration
- Batch data operations
- Enhanced reporting endpoints

---

**For additional support or questions about the API, please refer to the main README.md or contact the development team.**