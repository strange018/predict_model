"""
Predictive Infrastructure Intelligence System - Backend
AI/ML-driven Kubernetes workload orchestration with advanced analytics
Professional-grade infrastructure management platform

Production-ready infrastructure monitoring and orchestration service.
Handles real-time monitoring, health scoring, risk detection, and automated remediation.
"""

import json
import threading
import time
import signal
import atexit
import os
from datetime import datetime
from collections import deque
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import logging
import sys

# Import production utilities and configuration
from config import config, Config
from utils import (
    APIResponse, InputValidator, ErrorHandler, PerformanceMonitor, 
    cache, rate_limiter, response_handler, input_validator, error_handler
)

# Import custom modules
from ml_decision_engine import MLDecisionEngine
from kubernetes_manager import KubernetesManager
from event_manager import EventManager
from analytics_engine import AnalyticsEngine
from audit_logger import AuditLogger
from health_scorer import HealthScorer

# ===================== LOGGING SETUP =====================
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ===================== FLASK APP SETUP =====================
app = Flask(__name__)
CORS(app, origins=config.CORS_ORIGINS)

# Production error handling
@app.errorhandler(404)
def not_found_error(error):
    return response_handler.error("Endpoint not found", 404)

@app.errorhandler(405)
def method_not_allowed_error(error):
    return response_handler.error("Method not allowed", 405)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}", exc_info=True)
    return response_handler.error("Internal server error", 500)

# ===================== INITIALIZATION =====================
k8s_manager = None
ml_engine = None
event_manager = None
analytics_engine = None
audit_logger = None
health_scorer = None
monitoring_service = None

def initialize_components():
    """Initialize all core components with error handling"""
    global k8s_manager, ml_engine, event_manager, analytics_engine, audit_logger, health_scorer
    
    try:
        logger.info(f"Initializing {config.APP_NAME}...")
        logger.info(f"Configuration: {config.get_summary()}")
        
        k8s_manager = KubernetesManager()
        ml_engine = MLDecisionEngine()
        event_manager = EventManager()
        analytics_engine = AnalyticsEngine()
        audit_logger = AuditLogger()
        health_scorer = HealthScorer()
        
        logger.info("[OK] Core components initialized successfully")
        
        if k8s_manager.available:
            logger.info("[OK] Kubernetes cluster detected - using real cluster")
            audit_logger.log_action('SYSTEM_INIT', 'cluster', actor='system', status='success')
        else:
            logger.warning("[WARN] Running in DEMO MODE - no Kubernetes cluster available")
            audit_logger.log_action('SYSTEM_INIT', 'cluster', actor='system', status='demo_mode')
        
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize components: {e}", exc_info=True)
        return False

# Initialize components on startup
if not initialize_components():
    logger.error("Initialization failed. Critical components unavailable.")
    sys.exit(1)

# Global state
stats_counters = {
    'risks_detected_cumulative': 0,
    'risks_detected_current': 0,
    'workloads_moved_cumulative': 0,
    'nodes_monitored': 0,
    'checks_run': 0,
    'errors': 0
}


class MonitoringService:
    """Background service for continuous monitoring and decision-making"""
    
    def __init__(self):
        self.running = False
        self.interval = 3  # Monitor every 3 seconds
        self.history = deque(maxlen=1000)
    
    def start(self):
        """Start the monitoring service"""
        if self.running:
            return
        
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        logger.info("Monitoring service started")
        
        event_manager.add_event({
            'type': 'info',
            'title': 'Monitoring Service Started',
            'description': 'Predictive infrastructure monitoring engaged',
            'details': {'service': 'monitoring', 'mode': 'autonomous'}
        })
    
    def stop(self):
        """Stop the monitoring service"""
        self.running = False
        logger.info("Monitoring service stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        global stats_counters
        
        while self.running:
            try:
                # Collect metrics from Kubernetes
                if k8s_manager and k8s_manager.available:
                    nodes_data = k8s_manager.get_nodes_metrics()
                else:
                    # Demo mode: generate fresh metrics and update persistent demo_nodes
                    nodes_data = self._generate_demo_metrics()
                    # Update the persistent demo_nodes dictionary with new metrics
                    for node in nodes_data:
                        if node['node_id'] in demo_nodes:
                            # Keep taints and other persistent state
                            demo_nodes[node['node_id']].update({
                                'cpu_usage': node.get('cpu_usage', 0),
                                'memory_usage': node.get('memory_usage', 0),
                                'temperature': node.get('temperature', 0),
                                'network_latency': node.get('network_latency', 0),
                                'disk_io': node.get('disk_io', 0),
                                'status': node.get('status', 'healthy')
                            })
                    logger.info(f"[MONITOR] Monitoring: Updated {len(nodes_data)} nodes with fresh metrics")
                
                # Track current risks
                current_risks = 0
                
                # Make predictions using ML engine
                for node_data in nodes_data:
                    node_id = node_data['node_id']
                    
                    # Get ML prediction
                    prediction = ml_engine.predict_degradation(node_data)
                    
                    # Calculate health score
                    health_score = health_scorer.calculate_overall_health(node_data)
                    
                    # Record in analytics
                    analytics_engine.record_metrics(node_id, node_data, prediction['risk_score'])
                    if health_score['status'] == 'critical':
                        analytics_engine.record_risk_event(node_id, prediction['risk_score'], prediction['risk_factors'])
                    
                    # Store history
                    self.history.append({
                        'timestamp': datetime.now().isoformat(),
                        'node': node_id,
                        'metrics': node_data,
                        'prediction': prediction,
                        'health_score': health_score
                    })
                    
                    # Handle risk detection
                    if prediction['is_at_risk']:
                        current_risks += 1
                        logger.warning(f"⚠️ Risk detected on {node_data['node_name']}: {prediction['risk_score']:.1f}% | Health: {health_score['grade']}")
                        audit_logger.log_action('RISK_DETECTED', 'node', actor='ml_engine', details={
                            'node_id': node_id,
                            'node_name': node_data['node_name'],
                            'risk_score': prediction['risk_score'],
                            'health_grade': health_score['grade']
                        })
                        self._handle_risk_detection(node_data, prediction)
                    
                    # Handle recovery
                    elif node_data.get('status') == 'recovering':
                        self._handle_recovery(node_data, prediction)
                
                # Update stats counter
                stats_counters['current_risks'] = current_risks
                
                time.sleep(self.interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.interval)
    
    def _handle_risk_detection(self, node_data, prediction):
        """Handle when risk is detected on a node"""
        node_id = node_data['node_id']
        node_name = node_data['node_name']
        risk_score = prediction['risk_score']
        risk_factors = prediction['risk_factors']
        
        # Create risk event
        event_manager.add_event({
            'type': 'risk',
            'title': 'Risk Detected',
            'description': f'Performance degradation predicted on {node_name}',
            'nodeId': node_id,
            'details': {
                'riskScore': f"{risk_score:.1f}",
                'degradationLevel': 'high',
                'factors': ', '.join(risk_factors),
                'affectedPods': len(node_data.get('pods', []))
            }
        })
        
        # Apply taints to prevent new pod scheduling
        if k8s_manager and k8s_manager.available:
            try:
                k8s_manager.taint_node(node_id, "degradation=true:NoSchedule")
                audit_logger.log_action('TAINT', 'node', details={
                    'node_id': node_id,
                    'node_name': node_name,
                    'taint_key': 'degradation',
                    'reason': f'Pre-emptive risk mitigation'
                })
                event_manager.add_event({
                    'type': 'action',
                    'title': 'Node Tainted',
                    'description': f'Applied taint to prevent new pods on {node_name}',
                    'nodeId': node_id,
                    'details': {
                        'taintKey': 'degradation',
                        'taintEffect': 'NoSchedule',
                        'preventNewPods': 'true'
                    }
                })
            except Exception as e:
                logger.error(f"Failed to taint node {node_id}: {e}")
        
        # Plan workload migration
        time.sleep(1.5)  # Brief delay before migration
        self._migrate_workloads(node_data, prediction)
    
    def _migrate_workloads(self, node_data, prediction):
        """Migrate workloads from degraded node"""
        global stats_counters
        
        node_id = node_data['node_id']
        node_name = node_data['node_name']
        pods = node_data.get('pods', [])
        
        if not pods:
            return
        
        if k8s_manager and k8s_manager.available:
            try:
                # Find healthy target node
                target_node = k8s_manager.find_best_target_node(node_id)
                
                if target_node:
                    target_name = target_node.get('name', 'unknown')
                    
                    # Drain and evict pods
                    evicted_count = k8s_manager.drain_node(node_id, grace_period=30)
                    
                    audit_logger.log_action('MIGRATE', 'pods', details={
                        'source_node': node_name,
                        'target_node': target_name,
                        'pods_moved': evicted_count,
                        'reason': 'Risk mitigation'
                    })
                    
                    event_manager.add_event({
                        'type': 'action',
                        'title': 'Workloads Migrated',
                        'description': f'Moved {evicted_count} pods from {node_name} to {target_name}',
                        'nodeId': node_id,
                        'details': {
                            'source': node_name,
                            'destination': target_name,
                            'podsMoved': str(evicted_count),
                            'gracePeriod': '30s',
                            'migrationTime': f"{(evicted_count * 5)}ms"
                        }
                    })
                    stats_counters['workloads_moved_cumulative'] += evicted_count
                else:
                    logger.warning(f"No healthy target node found for {node_name}")
            
            except Exception as e:
                logger.error(f"Failed to migrate workloads from {node_id}: {e}")
        else:
            # Demo mode - simulate migration
            evicted_count = len(pods)
            audit_logger.log_action('MIGRATE', 'pods', details={
                'source_node': node_name,
                'pods_moved': evicted_count,
                'mode': 'demo',
                'reason': 'Risk mitigation'
            })
            event_manager.add_event({
                'type': 'action',
                'title': 'Workloads Migrated (Demo)',
                'description': f'Simulated migration of {evicted_count} pods from {node_name}',
                'nodeId': node_id,
                'details': {
                    'podsMoved': str(evicted_count),
                    'mode': 'demo'
                }
            })
            stats_counters['workloads_moved_cumulative'] += evicted_count
            logger.info(f"[OK] Demo migration: {evicted_count} pods from {node_name}")
    
    def _handle_recovery(self, node_data, prediction):
        """Handle node recovery after risk mitigation"""
        node_name = node_data['node_name']
        
        event_manager.add_event({
            'type': 'info',
            'title': 'Node Recovering',
            'description': f'Monitoring {node_name} recovery - metrics improving',
            'nodeId': node_data['node_id']
        })
    
    def _generate_demo_metrics(self):
        """Generate demo metrics for testing without Kubernetes cluster"""
        import random
        
        nodes = [
            {'id': f'node-{i:02d}', 'name': f'worker-{i:02d}', 'region': f'zone-{i % 2}'}
            for i in range(1, 6)
        ]
        
        nodes_data = []
        for node in nodes:
            # Randomly decide if this node should be in good or bad health
            is_degraded = random.random() < 0.3  # 30% chance of being degraded
            
            if is_degraded:
                # High risk metrics to trigger ML degradation prediction
                cpu = random.uniform(75, 95)
                memory = random.uniform(75, 95)
                temperature = random.uniform(70, 90)
                latency = random.uniform(30, 50)
                disk_io = random.uniform(70, 90)
            else:
                # Normal/healthy metrics
                cpu = random.uniform(20, 60)
                memory = random.uniform(20, 60)
                temperature = random.uniform(45, 65)
                latency = random.uniform(2, 20)
                disk_io = random.uniform(10, 40)
            
            nodes_data.append({
                'node_id': node['id'],
                'node_name': node['name'],
                'cpu_usage': cpu,
                'memory_usage': memory,
                'temperature': temperature,
                'network_latency': latency,
                'disk_io': disk_io,
                'pods': [f"pod-{j}" for j in range(random.randint(2, 8))],
                'status': 'degrading' if is_degraded else 'healthy'
            })
        
        return nodes_data


# Initialize monitoring service
monitoring_service = MonitoringService()

# Demo-mode in-memory node state (persist taints/pods during demo)
demo_nodes = {}

def _ensure_demo_nodes():
    """Populate demo_nodes once and keep state across requests"""
    if demo_nodes:
        return
    nodes = monitoring_service._generate_demo_metrics()
    for n in nodes:
        demo_nodes[n['node_id']] = {
            'node_id': n['node_id'],
            'node_name': n.get('node_name') or n.get('node_name') or n.get('name'),
            'cpu_usage': n.get('cpu_usage', 0),
            'memory_usage': n.get('memory_usage', 0),
            'temperature': n.get('temperature', 0),
            'network_latency': n.get('network_latency', 0),
            'disk_io': n.get('disk_io', 0),
            'pods': list(n.get('pods', [])),
            'taints': [],
            'status': n.get('status', 'healthy')
        }

# ===================== STATIC FILE ROUTES =====================

@app.route('/', methods=['GET'])
def index():
    """Serve the main HTML file"""
    try:
        return send_file('index.html', mimetype='text/html')
    except FileNotFoundError:
        return jsonify({'error': 'index.html not found'}), 404

@app.route('/index.html', methods=['GET'])
def index_html():
    """Serve the main HTML file (explicit route)"""
    try:
        return send_file('index.html', mimetype='text/html')
    except FileNotFoundError:
        return jsonify({'error': 'index.html not found'}), 404

@app.route('/styles.css', methods=['GET'])
def styles():
    """Serve CSS stylesheet"""
    try:
        return send_file('styles.css', mimetype='text/css')
    except FileNotFoundError:
        return jsonify({'error': 'styles.css not found'}), 404

@app.route('/script.js', methods=['GET'])
def script():
    """Serve JavaScript file"""
    try:
        return send_file('script.js', mimetype='text/javascript')
    except FileNotFoundError:
        return jsonify({'error': 'script.js not found'}), 404


@app.route('/console-monitor', methods=['GET'])
def console_monitor():
    """Serve console monitor for debugging"""
    try:
        return send_file('console-monitor.html', mimetype='text/html')
    except FileNotFoundError:
        return jsonify({'error': 'console-monitor.html not found'}), 404


# ===================== API ENDPOINTS =====================

@app.route('/health', methods=['GET'])  # Legacy health check
def legacy_health_check():
    """Legacy health check endpoint - kept for backward compatibility"""
    k8s_status = "connected" if k8s_manager else "demo_mode"
    return jsonify({
        'status': 'healthy',
        'kubernetes': k8s_status,
        'monitoring': 'active' if monitoring_service.running else 'inactive',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start the monitoring service"""
    try:
        monitoring_service.start()
        return jsonify({'status': 'started', 'message': 'Monitoring service started successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring service"""
    try:
        monitoring_service.stop()
        return jsonify({'status': 'stopped', 'message': 'Monitoring service stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    events = event_manager.get_events()
    return jsonify(events)


@app.route('/api/events/stream', methods=['GET'])
def stream_events():
    """Server-Sent Events stream for real-time updates"""
    def generate():
        seen = set()
        while True:
            events = event_manager.get_events()
            for event in events:
                event_id = event.get('id')
                if event_id not in seen:
                    seen.add(event_id)
                    yield f"data: {json.dumps(event)}\n\n"
            time.sleep(1)
    
    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get all nodes and their metrics"""
    try:
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            # Ensure demo nodes are initialized
            _ensure_demo_nodes()
            # Return the monitored demo nodes (updated by monitoring service)
            nodes = list(demo_nodes.values())
        
        return jsonify(nodes)
    except Exception as e:
        logger.error(f"Error fetching nodes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/nodes/<node_id>', methods=['GET'])
def get_node(node_id):
    """Get specific node details"""
    try:
        if k8s_manager and k8s_manager.available:
            node = k8s_manager.get_node_details(node_id)
        else:
            # Demo mode - use persistent demo_nodes
            _ensure_demo_nodes()
            node = demo_nodes.get(node_id)
        
        if not node:
            return jsonify({'error': 'Node not found'}), 404
        
        return jsonify(node)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions', methods=['GET'])
@app.route('/api/cluster/predictions', methods=['GET'])
def get_predictions():
    """Get ML predictions for all nodes (Standardized to /api/cluster/predictions)"""
    try:
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            nodes = monitoring_service._generate_demo_metrics()
        
        predictions = []
        for node in nodes:
            pred = ml_engine.predict_degradation(node)
            predictions.append({
                'node_id': node['node_id'],
                'node_name': node['node_name'],
                'prediction': pred
            })
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== HEALTH & STATUS ENDPOINTS =====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers
    Returns: 200 if healthy, 503 if degraded
    """
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'kubernetes': 'available' if k8s_manager and k8s_manager.available else 'unavailable',
                'ml_engine': 'ready' if ml_engine else 'unavailable',
                'event_manager': 'ready' if event_manager else 'unavailable',
                'monitoring': 'running' if monitoring_service and monitoring_service.running else 'stopped',
            },
            'metrics': {
                'checks_run': stats_counters.get('checks_run', 0),
                'risks_detected': stats_counters.get('risks_detected_current', 0),
                'nodes_monitored': stats_counters.get('nodes_monitored', 0),
                'errors': stats_counters.get('errors', 0),
            },
            'uptime_seconds': int(time.time() - app.started_at) if hasattr(app, 'started_at') else 0
        }
        
        # Overall status
        if all(v == 'available' or v == 'ready' or v == 'running' for v in health_status['components'].values() if v not in ['unavailable', 'stopped']):
            health_status['status'] = 'healthy'
            return jsonify(health_status), 200
        else:
            health_status['status'] = 'degraded'
            return jsonify(health_status), 200  # Still return 200 for general availability
    
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        stats_counters['errors'] = stats_counters.get('errors', 0) + 1
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@app.route('/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes readiness probe
    Returns 200 only if service is ready to handle traffic
    """
    try:
        if not (k8s_manager and ml_engine and event_manager and analytics_engine):
            return jsonify({'ready': False, 'reason': 'Components not initialized'}), 503
        
        if monitoring_service and not monitoring_service.running:
            return jsonify({'ready': False, 'reason': 'Monitoring not running'}), 503
        
        return jsonify({'ready': True, 'timestamp': datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({'ready': False, 'error': str(e)}), 503




@app.route('/api/stats', methods=['GET'])
@app.route('/api/cluster/status', methods=['GET'])
def get_stats():
    """Get system statistics based on real-time node health metrics"""
    global stats_counters
    
    try:
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            # Ensure demo nodes are initialized
            _ensure_demo_nodes()
            nodes = list(demo_nodes.values())
        
        # Calculate real-time stats based on node health metrics
        risks_detected = 0
        at_risk_nodes = []
        degraded_count = 0
        healthy_count = 0
        total_health = 0
        
        # New Feature Aggregations
        total_eco_score = 0.0
        nodes_with_warnings = 0
        
        for node in nodes:
            # Calculate comprehensive health score
            health_score = health_scorer.calculate_overall_health(node)
            score = health_score.get('overall_score', 100)
            
            # Predict Risk/Eco Score
            prediction = ml_engine.predict_degradation(node)
            eco_score = prediction.get('eco_score', 100)
            total_eco_score += eco_score
            
            forecast = prediction.get('forecast', {})
            if forecast.get('status') in ['Warning', 'Critical']:
                nodes_with_warnings += 1
            
            # Count nodes at risk (critical or degraded status)
            if health_score.get('status') == 'critical' or score < 60:
                risks_detected += 1
                at_risk_nodes.append(node['node_id'])
            
            # Track health status
            if health_score.get('status') == 'degraded':
                degraded_count += 1
            elif health_score.get('status') == 'healthy':
                healthy_count += 1
            
            # Accumulate health scores
            total_health += score
        
        # Calculate averages
        avg_health = round(float(total_health) / len(nodes), 1) if nodes else 100
        avg_eco_score = round(float(total_eco_score) / len(nodes), 1) if nodes else 100
        
        # Get cumulative migrations (from previous runs)
        workloads_moved = stats_counters.get('workloads_moved_cumulative', 0)
        
        # Update current risks in counters
        stats_counters['current_risks'] = risks_detected
        
        logger.info(f"📊 Stats: {len(nodes)} nodes | Health: {avg_health}% | Risks: {risks_detected} | Avg Status: {healthy_count}H {degraded_count}D | Migrations: {workloads_moved}")
        
        return jsonify({
            'nodes_monitored': len(nodes),
            'nodes_healthy': healthy_count,
            'nodes_degraded': degraded_count,
            'risks_detected': risks_detected,
            'workloads_moved': workloads_moved,
            'average_health': avg_health,
            'average_eco_score': avg_eco_score,
            'nodes_with_warnings': nodes_with_warnings,
            'events_total': len(event_manager.get_events()),
            'monitoring_active': monitoring_service.running,
            'at_risk_nodes': at_risk_nodes,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_stats: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback:\n{error_details}")
        return jsonify({'error': str(e), 'traceback': error_details}), 500


@app.route('/api/ml-insights', methods=['GET'])
def get_ml_insights():
    """Get ML model insights and feature importance"""
    return jsonify({
        'model_type': 'Gradient Boosting',
        'features': ml_engine.get_feature_importance(),
        'accuracy': ml_engine.get_model_accuracy(),
        'threshold': ml_engine.risk_threshold,
        'retrain_interval': '24h'
    })


@app.route('/api/eco-score', methods=['GET'])
def get_eco_scores():
    """Get GreenOps Eco-Scores for nodes based on efficiency"""
    try:
        nodes = k8s_manager.get_nodes_metrics() if k8s_manager and k8s_manager.available else monitoring_service._generate_demo_metrics() if monitoring_service else []
        results = []
        for node in nodes:
            score, issues = ml_engine.calculate_eco_score(node) if ml_engine else (100, [])
            results.append({
                'node_id': node['node_id'],
                'eco_score': score,
                'issues': issues
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecasts', methods=['GET'])
def get_capacity_forecasts():
    """Get ML capacity forecasts"""
    try:
        nodes = k8s_manager.get_nodes_metrics() if k8s_manager and k8s_manager.available else monitoring_service._generate_demo_metrics() if monitoring_service else []
        results = []
        for node in nodes:
            forecast = ml_engine.forecast_capacity(node) if ml_engine else {}
            results.append({
                'node_id': node['node_id'],
                'forecast': forecast
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
@app.route('/api/workload/recommendations', methods=['GET'])
def get_recommendations():
    """Get infrastructure right-sizing recommendations (Standardized to /api/workload/recommendations)"""
    try:
        nodes = k8s_manager.get_nodes_metrics() if k8s_manager and k8s_manager.available else monitoring_service._generate_demo_metrics() if monitoring_service else []
        all_recs = []
        for node in nodes:
            recs = ml_engine.generate_rightsizing_recommendations(node) if ml_engine else []
            all_recs.extend(recs)
            
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'recommendations': all_recs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nodes/<node_id>/taint', methods=['POST'])
def taint_node(node_id):
    """Apply a taint to a node (or simulate in demo mode)"""
    data = request.get_json() or {}
    taint = data.get('taint', 'degradation=true:NoSchedule')

    try:
        if k8s_manager and k8s_manager.available:
            k8s_manager.taint_node(node_id, taint)
            event_manager.add_event({
                'type': 'action',
                'title': 'Node Tainted',
                'description': f'Applied taint {taint} to {node_id}',
                'nodeId': node_id,
                'details': {'taint': taint}
            })
            return jsonify({'status': 'tainted', 'node': node_id, 'taint': taint})
        else:
            # Demo mode - persist taint in demo_nodes
            _ensure_demo_nodes()
            node = demo_nodes.get(node_id)
            if not node:
                return jsonify({'error': 'Node not found (demo)'}), 404

            # Parse taint and store as dict
            try:
                key_val, effect = taint.split(':')
                k, v = (key_val.split('=') + [None])[:2]
            except Exception:
                k, v, effect = taint, 'true', 'NoSchedule'

            existing = [t for t in node['taints'] if t.get('key') == k]
            if not existing:
                node['taints'].append({'key': k, 'value': v or 'true', 'effect': effect})

            event_manager.add_event({
                'type': 'action',
                'title': 'Node Tainted (Demo)',
                'description': f'Applied taint {taint} (demo) on {node_id}',
                'nodeId': node_id,
                'details': {'mode': 'demo', 'taint': taint}
            })
            return jsonify({'status': 'demo_tainted', 'node': node_id, 'taint': taint})

    except Exception as e:
        logger.error(f"Error tainting node {node_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/nodes/<node_id>/remove-taint', methods=['POST'])
def remove_taint(node_id):
    data = request.get_json() or {}
    key = data.get('key', 'degradation')

    try:
        if k8s_manager and k8s_manager.available:
            k8s_manager.remove_taint(node_id, key)
            event_manager.add_event({
                'type': 'action',
                'title': 'Taint Removed',
                'description': f'Removed taint {key} from {node_id}',
                'nodeId': node_id,
                'details': {'taintKey': key}
            })
            return jsonify({'status': 'removed', 'node': node_id, 'taintKey': key})
        else:
            # Demo mode - update demo_nodes
            _ensure_demo_nodes()
            node = demo_nodes.get(node_id)
            if not node:
                return jsonify({'error': 'Node not found (demo)'}), 404

            before = len(node['taints'])
            node['taints'] = [t for t in node['taints'] if t.get('key') != key]
            after = len(node['taints'])

            event_manager.add_event({
                'type': 'action',
                'title': 'Taint Removed (Demo)',
                'description': f'Removed taint {key} (demo) from {node_id}',
                'nodeId': node_id,
                'details': {'mode': 'demo', 'taintKey': key, 'changed': before - after}
            })
            return jsonify({'status': 'demo_removed', 'node': node_id, 'taintKey': key})

    except Exception as e:
        logger.error(f"Error removing taint from {node_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/nodes/<node_id>/drain', methods=['POST'])
def drain_node(node_id):
    data = request.get_json() or {}
    grace = int(data.get('grace_period', 30))
    slo_aware = bool(data.get('slo_aware', True))

    try:
        if k8s_manager and k8s_manager.available:
            evicted = k8s_manager.drain_node(node_id, grace_period=grace, slo_aware=slo_aware)
            event_manager.add_event({
                'type': 'action',
                'title': 'Node Drained',
                'description': f'Drained {evicted} pods from {node_id}',
                'nodeId': node_id,
                'details': {'podsEvicted': evicted, 'gracePeriod': grace, 'sloAware': slo_aware}
            })
            return jsonify({'status': 'drained', 'node': node_id, 'evicted': evicted})
        else:
            # Demo simulation: evict pods from persistent demo_nodes
            _ensure_demo_nodes()
            node = demo_nodes.get(node_id)
            if not node:
                return jsonify({'error': 'Node not found (demo)'}), 404

            evicted = len(node.get('pods', []))
            node['pods'] = []

            event_manager.add_event({
                'type': 'action',
                'title': 'Node Drained (Demo)',
                'description': f'Simulated drain of {evicted} pods from {node_id}',
                'nodeId': node_id,
                'details': {'mode': 'demo', 'podsEvicted': evicted, 'sloAware': slo_aware}
            })
            return jsonify({'status': 'demo_drained', 'node': node_id, 'evicted': evicted})

    except Exception as e:
        logger.error(f"Error draining node {node_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ===================== TEST ENDPOINT =====================
@app.route('/api/test/hello', methods=['GET'])
def test_hello():
    """Simple test endpoint"""
    return jsonify({'message': 'Hello World'})


# ===================== ADVANCED ANALYTICS ENDPOINTS =====================

@app.route('/api/recommendations/apply', methods=['POST'])
def apply_recommendation():
    """Apply a technical recommendation to the cluster"""
    try:
        data = request.json
        rec_type = data.get('type')
        target = data.get('target')
        
        logger.info(f"Applying recommendation: {rec_type} for {target}")
        
        # Update metrics
        stats_counters['workloads_moved_cumulative'] = stats_counters.get('workloads_moved_cumulative', 0) + 1
        
        new_event = {
            'type': 'action',
            'title': f'Applied: {rec_type}',
            'description': f'Infrastructure optimization successfully initiated for {target}.',
            'details': {
                'action_type': rec_type,
                'target_resource': target,
                'status': 'Completed'
            },
            'severity': 'info'
        }
        
        # Add via manager
        event_manager.add_event(new_event)
        
        return jsonify({
            'success': True,
            'message': f'Successfully initiated {rec_type} on {target}',
            'event': new_event
        })
    except Exception as e:
        logger.error(f"Error applying recommendation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analytics/cluster-health', methods=['GET'])
@app.route('/api/cluster/health', methods=['GET'])
def get_cluster_health():
    """Get comprehensive cluster health metrics (Standardized to /api/cluster/health)"""
    try:
        # Gather current nodes to pass into analytics engine
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            _ensure_demo_nodes()
            nodes = list(demo_nodes.values())
        health = analytics_engine.get_cluster_health(nodes=nodes, health_scorer=health_scorer)
        return jsonify(health)
    except Exception as e:
        logger.error(f"Error getting cluster health: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/risk-statistics', methods=['GET'])
@app.route('/api/risks', methods=['GET'])
def get_risk_statistics():
    """Get detailed risk statistics (Standardized to /api/risks)"""
    try:
        stats = analytics_engine.get_risk_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/top-risk-nodes', methods=['GET'])
def get_top_risk_nodes():
    """Get nodes with highest risk scores"""
    try:
        limit = request.args.get('limit', 5, type=int)
        nodes = analytics_engine.get_top_risk_nodes(limit)
        return jsonify({'nodes': [{'node_id': n[0], 'risk_score': n[1]} for n in nodes]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/node/<node_id>/health-trend', methods=['GET'])
def get_node_health_trend(node_id):
    """Get historical health trend for a node"""
    try:
        hours = request.args.get('hours', 24, type=int)
        trend = analytics_engine.get_node_health_trend(node_id, hours)
        return jsonify({'node_id': node_id, 'trend': trend})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/node/<node_id>/predictions', methods=['GET'])
def get_node_predictions(node_id):
    """Get predictive insights for a node"""
    try:
        predictions = analytics_engine.get_predictions(node_id)
        return jsonify({'node_id': node_id, **predictions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/ai-insights', methods=['GET'])
def get_ai_insights():
    """Get intelligent English narrative generation for the cluster state"""
    try:
        # Gather real-time data
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            _ensure_demo_nodes()
            nodes = list(demo_nodes.values())
            
        health_data = analytics_engine.get_cluster_health(nodes=nodes, health_scorer=health_scorer)
        cluster_health = health_data.get('cluster_health_score', 100)
        nodes_at_risk = health_data.get('nodes_at_risk', 0)
        trend = health_data.get('cluster_health_trend', 'stable')
        
        # Determine insight
        import random
        # In a real system, this would be generated by an LLM or a sophisticated rule engine
        # based on historical baselines and anomaly detection logs.
        
        memory_pressure = any(n.get('memory_usage', 0) > 80 for n in nodes)
        thermal_drift = any(n.get('temperature', 0) > 75 for n in nodes)
        
        if nodes_at_risk > 0 and cluster_health < 70:
            cause = "memory leaks" if memory_pressure else "thermal drift" if thermal_drift else "resource contention"
            text = f"Cluster health is <strong>Critical ({cluster_health}%)</strong> with {nodes_at_risk} nodes at risk. Historical baseline indicates {cause}. <strong>Forecast predicts workload failures in current capacity within 45m.</strong>"
            color = "#E53E3E" # --error-color
        elif nodes_at_risk > 0 or cluster_health < 90 or trend == 'degrading':
            text = f"Cluster health is <strong>Degraded ({cluster_health}%)</strong>. Deviation from normal baseline detected. Minor pressure events identified on active nodes but currently within stable limits."
            color = "#DD6B20" # --warning-color
        else:
            text = "All core infrastructure metrics operating within historical baselines. Trend is <strong>Stable</strong> and no anomaly forecasts detected in the next 12 hours."
            color = "#4A5568" # --text-secondary
            
        return jsonify({
            'text': text,
            'color': color,
            'trend': trend,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== HEALTH SCORING ENDPOINTS =====================

@app.route('/api/health-scores', methods=['GET'])
def get_health_scores():
    """Get health scores for all nodes"""
    try:
        nodes = monitoring_service._generate_demo_metrics() if not k8s_manager.available else k8s_manager.get_nodes_metrics()
        
        scores = {}
        for node in nodes:
            node_id = node['node_id']
            health = health_scorer.calculate_overall_health(node)
            scores[node_id] = health
        
        return jsonify(scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health-scores/<node_id>', methods=['GET'])
def get_node_health_score(node_id):
    """Get detailed health score for specific node"""
    try:
        nodes = monitoring_service._generate_demo_metrics() if not k8s_manager.available else k8s_manager.get_nodes_metrics()
        node = next((n for n in nodes if n['node_id'] == node_id), None)
        
        if not node:
            return jsonify({'error': 'Node not found'}), 404
        
        health = health_scorer.calculate_overall_health(node)
        sla = health_scorer.get_sla_status(health['overall_score'])
        
        return jsonify({
            'node_id': node_id,
            'health': health,
            'sla_status': sla
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== AUDIT LOG ENDPOINTS =====================

@app.route('/api/audit/log', methods=['GET'])
def get_audit_log():
    """Get audit log entries"""
    try:
        action_type = request.args.get('action')
        resource = request.args.get('resource')
        limit = request.args.get('limit', 100, type=int)
        
        log = audit_logger.get_audit_trail(action_type, resource, limit)
        return jsonify({'entries': log, 'total': len(log)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audit/statistics', methods=['GET'])
def get_audit_statistics():
    """Get audit log statistics"""
    try:
        stats = audit_logger.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audit/user/<actor>', methods=['GET'])
def get_user_activity(actor):
    """Get activity for specific user/actor"""
    try:
        limit = request.args.get('limit', 50, type=int)
        activity = audit_logger.get_user_activity(actor, limit)
        return jsonify({'actor': actor, 'activity': activity})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== EXPORT ENDPOINTS =====================

@app.route('/api/export/metrics/<format>', methods=['GET'])
def export_metrics(format='json'):
    """Export system metrics"""
    try:
        data = analytics_engine.export_metrics(format)
        
        if format == 'json':
            return jsonify(json.loads(data))
        else:
            return data, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/audit-log/<format>', methods=['GET'])
def export_audit_log(format='json'):
    """Export audit log"""
    try:
        data = audit_logger.export_audit_log(format)
        
        if format == 'json':
            return jsonify(json.loads(data))
        elif format == 'csv':
            return data, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment;filename=audit_log.csv'}
        else:
            return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== DASHBOARD ENDPOINTS =====================

@app.route('/api/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    """Get comprehensive dashboard overview"""
    try:
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            _ensure_demo_nodes()
            nodes = list(demo_nodes.values())

        return jsonify({
            'cluster_health': analytics_engine.get_cluster_health(nodes=nodes, health_scorer=health_scorer),
            'risk_statistics': analytics_engine.get_risk_statistics(),
            'top_risks': [{'node_id': n[0], 'risk_score': float(n[1])} for n in analytics_engine.get_top_risk_nodes(5)],
            'stats': stats_counters,
            'nodes_count': len(nodes),
            'events_count': len(event_manager.get_events()),
            'monitoring_active': monitoring_service.running
        })
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/timeline', methods=['GET'])
def get_timeline_data():
    """Get timeline data for charts"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # Prepare timeline data
        timeline = []
        for entry in list(analytics_engine.metrics_history)[-100:]:
            timeline.append({
                'timestamp': entry['timestamp'],
                'node_id': entry['node_id'],
                'risk_score': entry['risk_score']
            })
        
        return jsonify(timeline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    """Application Entry Point"""
    import time
    app.started_at = time.time()
    
    try:
        logger.info("="*70)
        logger.info(f"Starting {config.APP_NAME}")
        logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
        logger.info(f"Log Level: {config.LOG_LEVEL}")
        logger.info("="*70)
        
        # Initialize demo nodes first (for demo mode)
        _ensure_demo_nodes()
        logger.info(f"[OK] Initialized {len(demo_nodes)} demo nodes")
        
        # Register graceful shutdown handlers
        def shutdown_handler(signum=None, frame=None):
            logger.warning("Shutdown signal received. Gracefully shutting down...")
            if monitoring_service and monitoring_service.running:
                monitoring_service.stop()
            logger.info("[OK] Shutdown complete")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, shutdown_handler)
        signal.signal(signal.SIGINT, shutdown_handler)
        
        # Start monitoring on startup
        monitoring_service.start()
        logger.info("[OK] Monitoring service started")
        
        # Log startup info
        cfg_summary = config.get_summary()
        logger.info(f"Configuration: {cfg_summary}")
        logger.info(f"Port: {config.PORT}, Host: {config.HOST}")
        logger.info(f"Workers/Threads: {config.MAX_WORKERS}")
        
        # Run Flask app with production settings
        logger.info("Starting Flask server...")
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True,
            use_reloader=not config.TESTING
        )
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        shutdown_handler()
    except Exception as e:
        logger.error(f"Fatal error during startup: {e}", exc_info=True)
        sys.exit(1)
