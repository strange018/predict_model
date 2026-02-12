"""
Predictive Infrastructure Intelligence System - Backend
AI/ML-driven Kubernetes workload orchestration
"""

import json
import threading
import time
from datetime import datetime
from collections import deque
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import logging

# Import custom modules
from ml_decision_engine import MLDecisionEngine
from kubernetes_manager import KubernetesManager
from event_manager import EventManager

# Setup Flask
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize core components
try:
    k8s_manager = KubernetesManager()
    ml_engine = MLDecisionEngine()
    event_manager = EventManager()
    
    if k8s_manager.available:
        logger.info("✓ Kubernetes cluster detected - using real cluster")
    else:
        logger.info("✓ Running in DEMO MODE - no Kubernetes cluster available")
except Exception as e:
    logger.error(f"✗ Failed to initialize: {e}")
    # Even if init fails, try to continue
    try:
        k8s_manager = KubernetesManager()
        ml_engine = MLDecisionEngine()
        event_manager = EventManager()
    except:
        raise

# Global monitoring state
monitoring_active = False
monitoring_thread = None


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
                    logger.info(f"📊 Monitoring: Updated {len(nodes_data)} nodes with fresh metrics")
                
                # Make predictions using ML engine
                for node_data in nodes_data:
                    node_id = node_data['node_id']
                    
                    # Get ML prediction
                    prediction = ml_engine.predict_degradation(node_data)
                    
                    # Store history
                    self.history.append({
                        'timestamp': datetime.now().isoformat(),
                        'node': node_id,
                        'metrics': node_data,
                        'prediction': prediction
                    })
                    
                    # Handle risk detection
                    if prediction['is_at_risk']:
                        logger.warning(f"⚠️ Risk detected on {node_data['node_name']}: {prediction['risk_score']:.1f}%")
                        self._handle_risk_detection(node_data, prediction)
                    
                    # Handle recovery
                    elif node_data.get('status') == 'recovering':
                        self._handle_recovery(node_data, prediction)
                
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
                else:
                    logger.warning(f"No healthy target node found for {node_name}")
            
            except Exception as e:
                logger.error(f"Failed to migrate workloads from {node_id}: {e}")
        else:
            # Demo mode - simulate migration
            evicted_count = len(pods)
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
            nodes_data.append({
                'node_id': node['id'],
                'node_name': node['name'],
                'cpu_usage': random.uniform(20, 90),
                'memory_usage': random.uniform(25, 85),
                'temperature': random.uniform(45, 80),
                'network_latency': random.uniform(2, 45),
                'disk_io': random.uniform(10, 80),
                'pods': [f"pod-{j}" for j in range(random.randint(0, 10))],
                'status': 'healthy'
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
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
def get_predictions():
    """Get ML predictions for all nodes"""
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
        
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        if k8s_manager and k8s_manager.available:
            nodes = k8s_manager.get_nodes_metrics()
        else:
            nodes = monitoring_service._generate_demo_metrics()
        
        events = event_manager.get_events()
        
        risks_detected = len([e for e in events if e['type'] == 'risk'])
        workloads_moved = len([e for e in events if e['type'] == 'action' and 'Migrated' in e['title']])
        
        return jsonify({
            'nodes_monitored': len(nodes),
            'risks_detected': risks_detected,
            'workloads_moved': workloads_moved,
            'events_total': len(events),
            'monitoring_active': monitoring_service.running
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

    try:
        if k8s_manager and k8s_manager.available:
            evicted = k8s_manager.drain_node(node_id, grace_period=grace)
            event_manager.add_event({
                'type': 'action',
                'title': 'Node Drained',
                'description': f'Drained {evicted} pods from {node_id}',
                'nodeId': node_id,
                'details': {'podsEvicted': evicted, 'gracePeriod': grace}
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
                'details': {'mode': 'demo', 'podsEvicted': evicted}
            })
            return jsonify({'status': 'demo_drained', 'node': node_id, 'evicted': evicted})

    except Exception as e:
        logger.error(f"Error draining node {node_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize demo nodes first (for demo mode)
    _ensure_demo_nodes()
    logger.info(f"Initialized {len(demo_nodes)} demo nodes")
    
    # Start monitoring on startup
    monitoring_service.start()
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
