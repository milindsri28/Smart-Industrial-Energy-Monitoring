# Smart Industrial Energy Monitoring & Optimization System

A comprehensive software solution that monitors, analyzes, and optimizes industrial energy usage across factories and buildings to improve efficiency, cut costs, and support sustainability initiatives.

![Energy Monitor Dashboard](https://via.placeholder.com/800x400/1e293b/3b82f6?text=Industrial+Energy+Dashboard)

## 🎯 Overview

The Smart Industrial Energy Monitoring & Optimization System provides real-time monitoring and intelligent analysis of industrial equipment energy consumption. Built with modern web technologies, it offers ML-based anomaly detection, predictive insights, and collaborative decision-making tools for engineering teams.

### Key Benefits
- **Reduce Energy Costs** by up to 30% through intelligent monitoring and optimization
- **Prevent Equipment Failures** with predictive maintenance alerts
- **Improve Sustainability** with detailed energy consumption analytics
- **Enable Data-Driven Decisions** with real-time dashboards and insights

## ✨ Core Features

### 🔍 Real-time Data Collection
- Continuous monitoring of industrial equipment sensors
- Support for multiple device types (Motors, Compressors, HVAC, Conveyors)
- Time-series data storage and processing
- RESTful API endpoints for IoT device integration

### 🤖 ML-Based Anomaly Detection
- **Threshold-based Detection**: Configurable limits for power, temperature, and vibration
- **Intelligent Alerts**: Multi-level severity system (Low, Medium, High, Critical)
- **Real-time Processing**: Instant notification of anomalous patterns
- **Future-ready**: Architecture supports advanced ML models (Isolation Forest, LSTM)

### 📊 Advanced Dashboard & Visualization
- **Real-time Metrics**: Live charts and graphs with Chart.js integration
- **Equipment Status**: Visual status indicators for all monitored devices
- **Interactive Charts**: Power consumption, temperature, and vibration trends
- **Responsive Design**: Optimized for desktop and mobile viewing

### 🔐 Authentication & Role-Based Access
- **JWT-based Security**: Secure token-based authentication
- **Multi-role Support**: Admin, Manager, and Engineer access levels
- **Permission Control**: Role-based feature access and data visibility

### 📈 Optimization Engine
- **Load Balancing Suggestions**: Optimize equipment usage patterns
- **Energy Source Switching**: Recommendations for cost-effective energy usage
- **Predictive Maintenance**: Schedule maintenance based on usage patterns
- **Performance Analytics**: Historical trend analysis and reporting

### 👥 Cross-functional Collaboration
- **Multi-user Support**: Collaborative analysis and decision-making
- **Alert Management**: Shared alert acknowledgment and resolution tracking
- **Data Sharing**: Export capabilities for reports and presentations

## 🏗️ Technical Architecture

### Backend Stack
- **FastAPI** (Python) - High-performance REST API framework
- **MongoDB** - Time-series data storage with optimized collections
- **WebSocket** - Real-time data streaming and notifications
- **Scikit-learn** - Machine learning for anomaly detection
- **JWT Authentication** - Secure user authentication and authorization

### Frontend Stack
- **React 19** - Modern, component-based user interface
- **Tailwind CSS** - Utility-first styling framework
- **Chart.js** - Interactive data visualization
- **Socket.io Client** - Real-time data synchronization
- **Heroicons** - Professional icon library

### Database Schema
```
├── users              # User accounts and authentication
├── devices            # Industrial equipment registry
├── sensor_readings    # Time-series sensor data
├── alerts             # Anomaly detection results
└── threshold_configs  # Configurable alert thresholds
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- Yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-energy-monitor
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   ```

4. **Environment Configuration**
   
   Backend (.env):
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=energy_monitor
   JWT_SECRET_KEY=your-secure-secret-key
   CORS_ORIGINS=*
   ```

   Frontend (.env):
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

5. **Start the Application**
   ```bash
   # Start backend
   uvicorn server:app --host 0.0.0.0 --port 8001

   # Start frontend (in new terminal)
   yarn start
   ```

6. **Access the Application**
   - Open http://localhost:3000 in your browser
   - Login with default credentials: `admin / admin123`

## 📖 Usage Guide

### Initial Setup

1. **Login**: Use the default admin credentials or create a new account
2. **Start Simulation**: Click "Start Simulation" to begin generating sample data
3. **Monitor Dashboard**: View real-time metrics and equipment status
4. **Manage Alerts**: Acknowledge and track anomaly alerts

### Equipment Management

**Adding New Equipment:**
```bash
POST /api/devices
{
  "name": "Motor-A3",
  "type": "motor",
  "location": "Production Line 3"
}
```

**Supported Equipment Types:**
- `motor` - Industrial motors and drives
- `compressor` - Air compressors and pumps
- `hvac` - Heating, ventilation, and air conditioning
- `conveyor` - Conveyor belts and transport systems

### Data Ingestion

**Real-time Sensor Data:**
```bash
POST /api/sensor-ingest
[{
  "device_id": "device-uuid",
  "power_kw": 25.5,
  "temperature_c": 68.2,
  "vibration": 2.1,
  "runtime_hours": 8.5
}]
```

### Alert Management

**Retrieve Active Alerts:**
```bash
GET /api/alerts?acknowledged=false
```

**Acknowledge Alert:**
```bash
POST /api/alerts/acknowledge
{
  "alert_id": "alert-uuid"
}
```

## 🔌 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user account |
| POST | `/api/auth/login` | Authenticate user and get JWT token |

### Device Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/devices` | List all devices | Yes |
| POST | `/api/devices` | Create new device | Admin/Manager |

### Data & Analytics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/sensor-ingest` | Ingest sensor readings | Yes |
| GET | `/api/metrics` | Retrieve time-series data | Yes |
| GET | `/api/dashboard/summary` | Get dashboard overview | Yes |

### Simulation Control

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/simulation/start` | Start data simulation | Admin/Manager |
| POST | `/api/simulation/stop` | Stop data simulation | Admin/Manager |

### Alert System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/alerts` | List alerts with filters | Yes |
| POST | `/api/alerts/acknowledge` | Acknowledge alert | Yes |

## 👤 User Roles & Permissions

### Admin Role
- Full system access and configuration
- User management and role assignment
- Simulation control and system settings
- All data access and export capabilities

### Manager Role
- Equipment management and configuration
- Simulation control and data analysis
- Alert management and reporting
- Team collaboration features

### Engineer Role
- Equipment monitoring and status viewing
- Alert acknowledgment and basic reporting
- Data visualization and trend analysis
- Limited configuration access

## 📊 Default Equipment Configuration

The system comes pre-configured with realistic industrial equipment:

| Device | Type | Location | Power Range | Temp Range |
|--------|------|----------|-------------|------------|
| Motor-A1 | motor | Production Line 1 | 0.5-50 kW | 20-80°C |
| Motor-B2 | motor | Production Line 2 | 0.5-50 kW | 20-80°C |
| Compressor-C1 | compressor | Air Supply Room | 2-100 kW | 25-90°C |
| HVAC-H1 | hvac | Main Building | 1-75 kW | 18-35°C |
| HVAC-H2 | hvac | Warehouse | 1-75 kW | 18-35°C |
| Conveyor-CV1 | conveyor | Packaging Area | 0.2-25 kW | 20-60°C |
| Conveyor-CV2 | conveyor | Shipping Area | 0.2-25 kW | 20-60°C |

## 🛠️ Development

### Project Structure
```
smart-energy-monitor/
├── backend/
│   ├── server.py              # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend configuration
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Application styles
│   │   └── index.js          # React entry point
│   ├── package.json          # Node.js dependencies
│   └── .env                  # Frontend configuration
└── README.md                 # Project documentation
```

### Key Components

**Backend Components:**
- `AnomalyDetector` - ML-based threshold detection
- `EquipmentSimulator` - Realistic data generation
- `ConnectionManager` - WebSocket management
- `Authentication` - JWT and role-based security

**Frontend Components:**
- `Dashboard` - Main application interface
- `MetricCard` - Reusable metric display
- `RealTimeChart` - Live data visualization
- `DeviceGrid` - Equipment status overview
- `AlertCard` - Alert management interface

### Running Tests

```bash
# Backend API testing
python backend_test.py

# Frontend testing (manual)
yarn test
```

## 🔮 Future Enhancements

### Phase 2 - Advanced ML Models
- **Isolation Forest** for unsupervised anomaly detection
- **LSTM Autoencoders** for temporal pattern analysis
- **Predictive Maintenance** modeling
- **Energy Optimization** algorithms

### Phase 3 - Enterprise Features
- **Multi-facility Support** with centralized monitoring
- **Advanced Reporting** with PDF generation
- **Integration APIs** for SCADA and ERP systems
- **Mobile Applications** for field technicians

### Phase 4 - AI-Powered Optimization
- **Reinforcement Learning** for automated optimization
- **Digital Twin** integration
- **Carbon Footprint** tracking and reporting
- **Sustainability Scoring** and recommendations

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- **Documentation**: Check this README and inline code comments
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Contact**: Reach out to the development team

## 🏆 Acknowledgments

- **Honeywell**: Inspiration for industrial automation and energy efficiency
- **React Community**: Excellent documentation and component ecosystem  
- **FastAPI**: Outstanding Python web framework for APIs
- **MongoDB**: Reliable time-series data storage solution

---

**Built with ❤️ for industrial energy efficiency and sustainability**
