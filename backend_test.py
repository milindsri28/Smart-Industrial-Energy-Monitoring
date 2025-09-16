#!/usr/bin/env python3
"""
Smart Industrial Energy Monitoring System - Backend API Tests
Tests all core backend functionality including authentication, device management,
sensor data simulation, alerts, and dashboard summary.
"""

import requests
import json
import time
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class BackendTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self.get_backend_url()
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        
    def get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        return f"{url}/api"
            return "http://localhost:8001/api"  # fallback
        except Exception as e:
            print(f"Warning: Could not read frontend .env file: {e}")
            return "http://localhost:8001/api"  # fallback
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, use_auth: bool = False) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if use_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_authentication(self):
        """Test authentication system"""
        print("\n=== Testing Authentication System ===")
        
        # Test 1: Login with default admin credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                if "access_token" in token_data and "role" in token_data:
                    self.token = token_data["access_token"]
                    self.log_test(
                        "Admin Login", 
                        True, 
                        f"Successfully logged in as admin with role: {token_data['role']}", 
                        token_data
                    )
                else:
                    self.log_test("Admin Login", False, "Token response missing required fields", token_data)
            else:
                self.log_test("Admin Login", False, f"Login failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Login request failed: {str(e)}")
        
        # Test 2: Test user registration
        test_user_data = {
            "username": "test_engineer",
            "password": "testpass123",
            "email": "engineer@company.com",
            "role": "engineer"
        }
        
        try:
            response = self.make_request("POST", "/auth/register", test_user_data)
            
            if response.status_code == 200:
                user_data = response.json()
                self.log_test(
                    "User Registration", 
                    True, 
                    f"Successfully registered user: {user_data.get('username')}", 
                    user_data
                )
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_test("User Registration", True, "User already exists (expected behavior)")
            else:
                self.log_test("User Registration", False, f"Registration failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", False, f"Registration request failed: {str(e)}")
    
    def test_device_management(self):
        """Test device management endpoints"""
        print("\n=== Testing Device Management ===")
        
        # Test 1: Get devices
        try:
            response = self.make_request("GET", "/devices", use_auth=True)
            
            if response.status_code == 200:
                devices = response.json()
                self.log_test(
                    "Get Devices", 
                    True, 
                    f"Retrieved {len(devices)} devices", 
                    {"device_count": len(devices)}
                )
            else:
                self.log_test("Get Devices", False, f"Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Devices", False, f"Request failed: {str(e)}")
        
        # Test 2: Create device (requires admin/manager role)
        new_device_data = {
            "name": "Test-Motor-X1",
            "type": "motor",
            "location": "Test Production Line"
        }
        
        try:
            response = self.make_request("POST", "/devices", new_device_data, use_auth=True)
            
            if response.status_code == 200:
                device_data = response.json()
                self.log_test(
                    "Create Device", 
                    True, 
                    f"Successfully created device: {device_data.get('name')}", 
                    device_data
                )
            else:
                self.log_test("Create Device", False, f"Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Create Device", False, f"Request failed: {str(e)}")
    
    def test_simulation_and_sensor_data(self):
        """Test simulation and sensor data endpoints"""
        print("\n=== Testing Simulation and Sensor Data ===")
        
        # Test 1: Start simulation
        try:
            response = self.make_request("POST", "/simulation/start", use_auth=True)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "Start Simulation", 
                    True, 
                    f"Simulation response: {result.get('message')}", 
                    result
                )
                # Wait a bit for simulation to generate data
                time.sleep(8)
            else:
                self.log_test("Start Simulation", False, f"Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Start Simulation", False, f"Request failed: {str(e)}")
        
        # Test 2: Test sensor data ingestion
        # First get a device ID
        try:
            devices_response = self.make_request("GET", "/devices", use_auth=True)
            if devices_response.status_code == 200:
                devices = devices_response.json()
                if devices:
                    device_id = devices[0]["id"]
                    
                    sensor_data = [{
                        "device_id": device_id,
                        "power_kw": 25.5,
                        "temperature_c": 68.2,
                        "vibration": 2.1,
                        "runtime_hours": 8.5
                    }]
                    
                    response = self.make_request("POST", "/sensor-ingest", sensor_data, use_auth=True)
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.log_test(
                            "Sensor Data Ingestion", 
                            True, 
                            f"Successfully ingested sensor data: {result.get('message')}", 
                            result
                        )
                    else:
                        self.log_test("Sensor Data Ingestion", False, f"Failed with status {response.status_code}: {response.text}")
                else:
                    self.log_test("Sensor Data Ingestion", False, "No devices available for testing")
            else:
                self.log_test("Sensor Data Ingestion", False, "Could not retrieve devices for testing")
                
        except Exception as e:
            self.log_test("Sensor Data Ingestion", False, f"Request failed: {str(e)}")
        
        # Test 3: Get metrics
        try:
            response = self.make_request("GET", "/metrics", use_auth=True)
            
            if response.status_code == 200:
                metrics = response.json()
                self.log_test(
                    "Get Metrics", 
                    True, 
                    f"Retrieved {len(metrics)} metric readings", 
                    {"metrics_count": len(metrics)}
                )
            else:
                self.log_test("Get Metrics", False, f"Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Metrics", False, f"Request failed: {str(e)}")
    
    def test_alert_system(self):
        """Test alert system endpoints"""
        print("\n=== Testing Alert System ===")
        
        # Test 1: Get alerts
        try:
            response = self.make_request("GET", "/alerts", use_auth=True)
            
            if response.status_code == 200:
                alerts = response.json()
                self.log_test(
                    "Get Alerts", 
                    True, 
                    f"Retrieved {len(alerts)} alerts", 
                    {"alerts_count": len(alerts)}
                )
                
                # Test 2: Acknowledge alert (if any alerts exist)
                if alerts:
                    alert_id = alerts[0]["id"]
                    ack_data = {"alert_id": alert_id}
                    
                    ack_response = self.make_request("POST", "/alerts/acknowledge", ack_data, use_auth=True)
                    
                    if ack_response.status_code == 200:
                        result = ack_response.json()
                        self.log_test(
                            "Acknowledge Alert", 
                            True, 
                            f"Successfully acknowledged alert: {result.get('message')}", 
                            result
                        )
                    else:
                        self.log_test("Acknowledge Alert", False, f"Failed with status {ack_response.status_code}: {ack_response.text}")
                else:
                    self.log_test("Acknowledge Alert", True, "No alerts available to acknowledge (expected if no anomalies detected)")
                    
            else:
                self.log_test("Get Alerts", False, f"Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Alerts", False, f"Request failed: {str(e)}")
    
    def test_dashboard_summary(self):
        """Test dashboard summary endpoint"""
        print("\n=== Testing Dashboard Summary ===")
        
        try:
            response = self.make_request("GET", "/dashboard/summary", use_auth=True)
            
            if response.status_code == 200:
                summary = response.json()
                required_fields = ["device_count", "active_alerts", "avg_power_kw", "system_status"]
                
                if all(field in summary for field in required_fields):
                    self.log_test(
                        "Dashboard Summary", 
                        True, 
                        f"Retrieved complete dashboard summary with {summary['device_count']} devices, {summary['active_alerts']} active alerts", 
                        summary
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in summary]
                    self.log_test("Dashboard Summary", False, f"Missing required fields: {missing_fields}", summary)
            else:
                self.log_test("Dashboard Summary", False, f"Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Dashboard Summary", False, f"Request failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print(f"Starting Smart Industrial Energy Monitoring System Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Run tests in logical sequence
        self.test_authentication()
        
        if self.token:  # Only proceed if authentication succeeded
            self.test_device_management()
            self.test_simulation_and_sensor_data()
            self.test_alert_system()
            self.test_dashboard_summary()
        else:
            print("\n❌ Authentication failed - skipping remaining tests")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\nFAILED TESTS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['details']}")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}: {result['details']}")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()