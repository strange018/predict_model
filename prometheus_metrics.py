"""
Prometheus Metrics Exporter
Exposes application metrics in Prometheus format
"""

import os
from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

# ========== Application Info ==========
app_info = Info('predictive_infrastructure', 'Application information')
app_info.info({
    'version': '2.0.0',
    'name': 'Predictive Infrastructure Intelligence',
    'mode': os.getenv('FLASK_ENV', 'development')
})

# ========== Node Metrics ==========
node_cpu_usage = Gauge(
    'node_cpu_usage_percent',
    'CPU usage percentage for each node',
    ['node_id', 'node_name']
)

node_memory_usage = Gauge(
    'node_memory_usage_percent',
    'Memory usage percentage for each node',
    ['node_id', 'node_name']
)

node_temperature = Gauge(
    'node_temperature_celsius',
    'Temperature in Celsius for each node',
    ['node_id', 'node_name']
)

node_network_latency = Gauge(
    'node_network_latency_ms',
    'Network latency in milliseconds for each node',
    ['node_id', 'node_name']
)

node_disk_io = Gauge(
    'node_disk_io_percent',
    'Disk I/O usage percentage for each node',
    ['node_id', 'node_name']
)

node_pod_count = Gauge(
    'node_pod_count',
    'Number of pods running on each node',
    ['node_id', 'node_name']
)

node_health_score = Gauge(
    'node_health_score',
    'Health score (0-100) for each node',
    ['node_id', 'node_name']
)

node_risk_score = Gauge(
    'node_risk_score',
    'Risk score (0-1) for each node',
    ['node_id', 'node_name']
)

# ========== Cluster Metrics ==========
cluster_total_nodes = Gauge(
    'cluster_total_nodes',
    'Total number of nodes in the cluster'
)

cluster_healthy_nodes = Gauge(
    'cluster_healthy_nodes',
    'Number of healthy nodes in the cluster'
)

cluster_degraded_nodes = Gauge(
    'cluster_degraded_nodes',
    'Number of degraded nodes in the cluster'
)

cluster_critical_nodes = Gauge(
    'cluster_critical_nodes',
    'Number of critical nodes in the cluster'
)

cluster_health_score = Gauge(
    'cluster_health_score',
    'Overall cluster health score (0-100)'
)

cluster_average_risk = Gauge(
    'cluster_average_risk_score',
    'Average risk score across all nodes'
)

# ========== Event Metrics ==========
events_total = Counter(
    'events_total',
    'Total number of events generated',
    ['event_type']
)

risks_detected_total = Counter(
    'risks_detected_total',
    'Total number of risks detected'
)

workloads_migrated_total = Counter(
    'workloads_migrated_total',
    'Total number of workloads migrated'
)

# ========== API Metrics ==========
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# ========== ML Metrics ==========
ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total number of ML predictions made'
)

ml_prediction_duration = Histogram(
    'ml_prediction_duration_seconds',
    'ML prediction duration in seconds',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25]
)

ml_high_risk_predictions = Counter(
    'ml_high_risk_predictions_total',
    'Total number of high risk predictions'
)

# ========== Monitoring Metrics ==========
monitoring_cycles_total = Counter(
    'monitoring_cycles_total',
    'Total number of monitoring cycles completed'
)

monitoring_cycle_duration = Histogram(
    'monitoring_cycle_duration_seconds',
    'Monitoring cycle duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

monitoring_active = Gauge(
    'monitoring_active',
    'Whether monitoring service is active (1=active, 0=inactive)'
)


class PrometheusMetrics:
    """Helper class to update Prometheus metrics"""
    
    @staticmethod
    def update_node_metrics(node_data: dict, risk_score: float = 0, health_score: float = 100):
        """Update all metrics for a single node"""
        node_id = node_data.get('node_id', 'unknown')
        node_name = node_data.get('node_name', node_id)
        
        labels = {'node_id': node_id, 'node_name': node_name}
        
        node_cpu_usage.labels(**labels).set(node_data.get('cpu_usage', 0))
        node_memory_usage.labels(**labels).set(node_data.get('memory_usage', 0))
        node_temperature.labels(**labels).set(node_data.get('temperature', 0))
        node_network_latency.labels(**labels).set(node_data.get('network_latency', 0))
        node_disk_io.labels(**labels).set(node_data.get('disk_io', 0))
        node_pod_count.labels(**labels).set(len(node_data.get('pods', [])))
        node_health_score.labels(**labels).set(health_score)
        node_risk_score.labels(**labels).set(risk_score)
    
    @staticmethod
    def update_cluster_metrics(stats: dict):
        """Update cluster-wide metrics"""
        cluster_total_nodes.set(stats.get('nodes_monitored', 0))
        cluster_healthy_nodes.set(stats.get('nodes_healthy', 0))
        cluster_degraded_nodes.set(stats.get('nodes_degraded', 0))
        cluster_critical_nodes.set(stats.get('risks_detected', 0))
        cluster_health_score.set(stats.get('average_health', 100))
    
    @staticmethod
    def record_event(event_type: str):
        """Record an event"""
        events_total.labels(event_type=event_type).inc()
    
    @staticmethod
    def record_risk_detected():
        """Record a risk detection"""
        risks_detected_total.inc()
    
    @staticmethod
    def record_workload_migration(count: int = 1):
        """Record workload migrations"""
        workloads_migrated_total.inc(count)
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status: int, duration: float):
        """Record an API request"""
        api_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_ml_prediction(duration: float, is_high_risk: bool = False):
        """Record an ML prediction"""
        ml_predictions_total.inc()
        ml_prediction_duration.observe(duration)
        if is_high_risk:
            ml_high_risk_predictions.inc()
    
    @staticmethod
    def record_monitoring_cycle(duration: float):
        """Record a monitoring cycle"""
        monitoring_cycles_total.inc()
        monitoring_cycle_duration.observe(duration)
    
    @staticmethod
    def set_monitoring_active(active: bool):
        """Set monitoring status"""
        monitoring_active.set(1 if active else 0)


def get_metrics():
    """Generate Prometheus metrics output"""
    return generate_latest()


def get_content_type():
    """Get the content type for Prometheus metrics"""
    return CONTENT_TYPE_LATEST


# Create global instance
prometheus = PrometheusMetrics()
