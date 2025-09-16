import React, { useState, useEffect, useContext, createContext } from "react";
import "./App.css";
import axios from "axios";
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  BarElement 
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import io from 'socket.io-client';
import { 
  BellIcon, 
  CogIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  PlayIcon,
  StopIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Decode token to get user info
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({ 
          username: payload.sub, 
          role: localStorage.getItem('userRole') || 'engineer' 
        });
      } catch (e) {
        console.error('Token decode error:', e);
        logout();
      }
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });
      const { access_token, role, username: user_name } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      localStorage.setItem('userRole', role);
      setUser({ username: user_name, role });
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Login Component
const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const success = await login(username, password);
    if (!success) {
      setError('Invalid credentials');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md border border-white/20">
        <div className="text-center mb-8">
          <ChartBarIcon className="w-16 h-16 text-blue-400 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-white">Energy Monitor</h1>
          <p className="text-blue-200">Industrial Energy Management System</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter username"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter password"
              required
            />
          </div>
          
          {error && (
            <div className="text-red-400 text-sm text-center">{error}</div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-semibold py-3 px-4 rounded-lg transition duration-200"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-blue-200">
          <p>Demo Credentials:</p>
          <p><strong>Username:</strong> admin | <strong>Password:</strong> admin123</p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Components
const MetricCard = ({ title, value, unit, icon: Icon, trend, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-500/20 border-blue-500/30 text-blue-400",
    green: "bg-green-500/20 border-green-500/30 text-green-400",
    yellow: "bg-yellow-500/20 border-yellow-500/30 text-yellow-400",
    red: "bg-red-500/20 border-red-500/30 text-red-400"
  };

  return (
    <div className={`p-6 rounded-xl border backdrop-blur-sm ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm opacity-80">{title}</p>
          <p className="text-2xl font-bold mt-1">
            {value} <span className="text-sm font-normal">{unit}</span>
          </p>
          {trend && (
            <p className="text-xs mt-1 opacity-60">{trend}</p>
          )}
        </div>
        <Icon className="w-8 h-8 opacity-60" />
      </div>
    </div>
  );
};

const AlertCard = ({ alert, onAcknowledge }) => {
  const severityColors = {
    low: "bg-blue-500/20 border-blue-500/30",
    medium: "bg-yellow-500/20 border-yellow-500/30",
    high: "bg-orange-500/20 border-orange-500/30",
    critical: "bg-red-500/20 border-red-500/30"
  };

  return (
    <div className={`p-4 rounded-lg border ${severityColors[alert.severity]} mb-3`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-orange-400" />
            <span className="text-sm font-medium text-white capitalize">
              {alert.severity} Alert
            </span>
            <span className="text-xs text-gray-400">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm text-gray-200">{alert.message}</p>
          <p className="text-xs text-gray-400 mt-1">
            Device: {alert.device_id} | Metric: {alert.metric}
          </p>
        </div>
        {!alert.acknowledged && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className="ml-4 p-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
          >
            <CheckIcon className="w-4 h-4 text-white" />
          </button>
        )}
      </div>
    </div>
  );
};

const RealTimeChart = ({ data, title, metric }) => {
  const chartData = {
    labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: metric,
        data: data.map(d => d[metric]),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: title, color: '#fff' }
    },
    scales: {
      x: { 
        grid: { color: 'rgba(255,255,255,0.1)' },
        ticks: { color: '#9CA3AF' }
      },
      y: { 
        grid: { color: 'rgba(255,255,255,0.1)' },
        ticks: { color: '#9CA3AF' }
      }
    }
  };

  return (
    <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 backdrop-blur-sm">
      <div className="h-64">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

const DeviceGrid = ({ devices, readings }) => {
  const getLatestReading = (deviceId) => {
    return readings.find(r => r.device_id === deviceId);
  };

  const getDeviceStatus = (device) => {
    const reading = getLatestReading(device.id);
    if (!reading) return { status: 'offline', color: 'gray' };
    
    // Simple status logic based on power consumption
    if (reading.power_kw > 0) {
      return { status: 'active', color: 'green' };
    }
    return { status: 'idle', color: 'yellow' };
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {devices.map(device => {
        const reading = getLatestReading(device.id);
        const { status, color } = getDeviceStatus(device);
        
        return (
          <div key={device.id} className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-white">{device.name}</h3>
              <div className={`w-3 h-3 rounded-full bg-${color}-500`}></div>
            </div>
            <p className="text-sm text-gray-400 mb-2">Type: {device.type}</p>
            <p className="text-sm text-gray-400 mb-3">Location: {device.location}</p>
            
            {reading && (
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Power:</span>
                  <span className="text-white">{reading.power_kw} kW</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Temp:</span>
                  <span className="text-white">{reading.temperature_c}°C</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Vibration:</span>
                  <span className="text-white">{reading.vibration}</span>
                </div>
              </div>
            )}
            
            <div className="mt-3 pt-3 border-t border-slate-700">
              <span className={`text-xs px-2 py-1 rounded-full bg-${color}-500/20 text-${color}-400 capitalize`}>
                {status}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [readings, setReadings] = useState([]);
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [socket, setSocket] = useState(null);
  const [realtimeData, setRealtimeData] = useState([]);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchDashboardData();
    
    // Setup WebSocket connection
    const ws = io(BACKEND_URL);
    setSocket(ws);
    
    ws.on('connect', () => {
      console.log('Connected to WebSocket');
    });
    
    ws.on('sensor_reading', (data) => {
      setRealtimeData(prev => [...prev.slice(-49), data.data]);
      fetchSummary(); // Update summary with new data
    });
    
    ws.on('alert', (data) => {
      setAlerts(prev => [...data.data, ...prev]);
    });
    
    return () => {
      if (ws) ws.disconnect();
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      await Promise.all([
        fetchSummary(),
        fetchDevices(),
        fetchAlerts(),
        fetchReadings()
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/summary`);
      setSummary(response.data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API}/devices`);
      setDevices(response.data);
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API}/alerts?acknowledged=false`);
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const fetchReadings = async () => {
    try {
      const response = await axios.get(`${API}/metrics`);
      setReadings(response.data.slice(0, 50)); // Latest 50 readings
    } catch (error) {
      console.error('Error fetching readings:', error);
    }
  };

  const toggleSimulation = async () => {
    try {
      const endpoint = simulationRunning ? 'stop' : 'start';
      await axios.post(`${API}/simulation/${endpoint}`);
      setSimulationRunning(!simulationRunning);
    } catch (error) {
      console.error('Error toggling simulation:', error);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await axios.post(`${API}/alerts/acknowledge`, { alert_id: alertId });
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  if (!summary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-lg border-b border-slate-700/50">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <ChartBarIcon className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-xl font-bold text-white">Energy Monitor Pro</h1>
                <p className="text-sm text-gray-400">Industrial Energy Management System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-400">Welcome, {user.username}</span>
                <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full capitalize">
                  {user.role}
                </span>
              </div>
              
              {(user.role === 'admin' || user.role === 'manager') && (
                <button
                  onClick={toggleSimulation}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
                    simulationRunning 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {simulationRunning ? <StopIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
                  <span>{simulationRunning ? 'Stop' : 'Start'} Simulation</span>
                </button>
              )}
              
              <button
                onClick={logout}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Devices"
            value={summary.device_count}
            unit="units"
            icon={CogIcon}
            color="blue"
          />
          <MetricCard
            title="Active Alerts"
            value={summary.active_alerts}
            unit="alerts"
            icon={BellIcon}
            color={summary.active_alerts > 0 ? "red" : "green"}
          />
          <MetricCard
            title="Avg Power Consumption"
            value={summary.avg_power_kw}
            unit="kW"
            icon={ChartBarIcon}
            color="yellow"
          />
          <MetricCard
            title="System Status"
            value={summary.system_status}
            unit=""
            icon={CheckIcon}
            color="green"
          />
        </div>

        {/* Real-time Charts */}
        {realtimeData.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RealTimeChart
              data={realtimeData}
              title="Real-time Power Consumption"
              metric="power_kw"
            />
            <RealTimeChart
              data={realtimeData}
              title="Real-time Temperature"
              metric="temperature_c"
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Device Grid */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-semibold text-white mb-4">Equipment Status</h2>
            <DeviceGrid devices={devices} readings={readings} />
          </div>

          {/* Alerts Panel */}
          <div>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <BellIcon className="w-5 h-5 mr-2" />
              Active Alerts ({alerts.length})
            </h2>
            <div className="bg-slate-800/30 rounded-xl p-4 max-h-96 overflow-y-auto">
              {alerts.length > 0 ? (
                alerts.map(alert => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    onAcknowledge={acknowledgeAlert}
                  />
                ))
              ) : (
                <p className="text-center text-gray-400 py-8">No active alerts</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppContent />
      </div>
    </AuthProvider>
  );
}

const AppContent = () => {
  const { user } = useAuth();
  
  return user ? <Dashboard /> : <Login />;
};

export default App;