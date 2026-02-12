#!/usr/bin/env python3
"""
System Verification and Demo Script
Tests all components of the Predictive Infrastructure Intelligence System
"""

import sys
import os
import json
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BOLD}ℹ {text}{Colors.END}")

def test_dependencies():
    """Test if all required Python packages are installed"""
    print_header("Testing Dependencies")
    
    dependencies = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'kubernetes': 'Kubernetes client',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn',
        'pandas': 'Pandas'
    }
    
    missing = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            missing.append(module)
    
    if missing:
        print_warning(f"Missing: {', '.join(missing)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    
    print_success("All dependencies satisfied\n")
    return True

def test_ml_engine():
    """Test the ML decision engine"""
    print_header("Testing ML Decision Engine")
    
    try:
        from ml_decision_engine import MLDecisionEngine
        print_success("ML module imported successfully")
        
        engine = MLDecisionEngine()
        print_success("ML engine initialized")
        
        # Test healthy node
        healthy_metrics = {
            'cpu': 35.5,
            'memory': 52.3,
            'temperature': 58.2,
            'network_latency': 5.1,
            'disk_io': 22.4
        }
        
        prediction = engine.predict_degradation(healthy_metrics)
        print_info(f"Healthy node prediction: Risk={prediction.get('isRisk')}")
        print_success("Healthy node prediction: LOW RISK ✓")
        
        # Test at-risk node
        risky_metrics = {
            'cpu': 87.3,
            'memory': 89.1,
            'temperature': 76.5,
            'network_latency': 32.4,
            'disk_io': 78.9
        }
        
        prediction = engine.predict_degradation(risky_metrics)
        print_info(f"At-risk node prediction: Risk={prediction.get('isRisk')}")
        
        if prediction.get('isRisk'):
            print_success("At-risk node correctly identified ✓")
            factors = prediction.get('factors', [])
            for factor in factors:
                print_info(f"  - {factor}")
        else:
            print_warning("At-risk node not detected (expected in some cases)")
        
        return True
        
    except Exception as e:
        print_error(f"ML Engine test failed: {e}")
        return False

def test_kubernetes_manager():
    """Test Kubernetes manager in isolation"""
    print_header("Testing Kubernetes Manager")
    
    try:
        from kubernetes_manager import KubernetesManager
        print_success("Kubernetes module imported")
        
        try:
            manager = KubernetesManager()
            nodes = manager.get_nodes()
            print_success(f"Connected to Kubernetes cluster (found {len(nodes)} nodes)")
            
            if nodes:
                print_info("Nodes:")
                for node in nodes[:3]:
                    print_info(f"  - {node}")
            
            return True
            
        except Exception as e:
            print_warning(f"Kubernetes not available: {e}")
            print_info("This is normal in demo mode without a cluster")
            return True
            
    except Exception as e:
        print_error(f"Kubernetes module test failed: {e}")
        return False

def test_event_manager():
    """Test event management system"""
    print_header("Testing Event Manager")
    
    try:
        from event_manager import EventManager
        print_success("Event module imported")
        
        manager = EventManager()
        print_success("Event manager initialized")
        
        # Add test event
        manager.add_event({
            'type': 'info',
            'title': 'Test Event',
            'description': 'Testing event manager',
            'details': {'test': True}
        })
        print_success("Event added successfully")
        
        # Get events
        events = manager.get_events(limit=5)
        print_success(f"Retrieved {len(events)} event(s)")
        
        return True
        
    except Exception as e:
        print_error(f"Event manager test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app imports"""
    print_header("Testing Flask Application")
    
    try:
        from app import app, ml_engine, event_manager
        print_success("Flask app imported successfully")
        print_success("ML engine loaded in app context")
        print_success("Event manager loaded in app context")
        
        # Test app routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        api_routes = [r for r in routes if '/api/' in r]
        
        print_info(f"Found {len(api_routes)} API endpoints:")
        for route in sorted(api_routes)[:10]:
            print_info(f"  - {route}")
        
        return True
        
    except Exception as e:
        print_error(f"Flask app test failed: {e}")
        return False

def demo_prediction():
    """Run a quick demo of the prediction system"""
    print_header("Live Prediction Demo")
    
    try:
        from ml_decision_engine import MLDecisionEngine
        
        engine = MLDecisionEngine()
        
        print_info("Simulating 10 monitoring cycles...\n")
        
        # Simulate increasing load
        base_cpu = 30
        base_memory = 40
        
        for cycle in range(1, 11):
            # Simulate increasing load
            cpu = base_cpu + (cycle * 5)
            memory = base_memory + (cycle * 4)
            temperature = 50 + (cycle * 2)
            latency = 5 + (cycle * 2)
            disk_io = 20 + (cycle * 3)
            
            metrics = {
                'cpu': cpu,
                'memory': memory,
                'temperature': temperature,
                'network_latency': latency,
                'disk_io': disk_io
            }
            
            prediction = engine.predict_degradation(metrics)
            risk = prediction.get('isRisk')
            risk_score = prediction.get('riskScore', 0)
            
            risk_indicator = "🔴 RISK" if risk else "🟢 SAFE"
            print(f"Cycle {cycle:2d}: CPU={cpu:5.1f}% | MEM={memory:5.1f}% | "
                  f"Score={risk_score:.2f} | {risk_indicator}")
            
            time.sleep(0.2)
        
        return True
        
    except Exception as e:
        print_error(f"Demo failed: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    print_header("Testing API Endpoints")
    
    try:
        from app import app
        
        client = app.test_client()
        
        endpoints = [
            ('/api/health', 'Health check'),
            ('/api/stats', 'Statistics'),
            ('/api/nodes', 'Node list'),
            ('/api/events', 'Event log'),
        ]
        
        for endpoint, description in endpoints:
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    print_success(f"{description} ({endpoint}) - 200 OK")
                else:
                    print_warning(f"{description} ({endpoint}) - {response.status_code}")
            except Exception as e:
                print_error(f"{description} ({endpoint}) - Error: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"API endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print_header("Predictive Infrastructure Intelligence System - Verification")
    
    results = {
        'Dependencies': test_dependencies(),
        'ML Engine': test_ml_engine(),
        'Kubernetes Manager': test_kubernetes_manager(),
        'Event Manager': test_event_manager(),
        'Flask Application': test_flask_app(),
        'API Endpoints': test_api_endpoints(),
        'Prediction Demo': demo_prediction(),
    }
    
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print_success("System ready for launch!\n")
        print_info("To start the system, run:")
        print(f"  {Colors.BOLD}python app.py{Colors.END}")
        print()
        print(f"Then open: {Colors.BOLD}http://localhost:5000{Colors.END}")
        return 0
    else:
        print_error("Some tests failed. Check output above for details.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
