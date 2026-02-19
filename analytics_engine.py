"""
Advanced Analytics Engine - Historical Data Analysis & Trending
Provides insights, predictions, and performance metrics
"""

import json
from collections import deque
from datetime import datetime, timedelta
import logging
import numpy as np

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Advanced analytics and historical data analysis"""
    
    def __init__(self, max_history=10000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.risk_timeline = deque(maxlen=1000)
        self.performance_scores = {}
        self.node_health_history = {}
    
    def record_metrics(self, node_id, metrics, risk_score):
        """Record node metrics for historical analysis"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'node_id': node_id,
            'metrics': metrics,
            'risk_score': risk_score
        }
        self.metrics_history.append(entry)
        
        # Track health history per node
        if node_id not in self.node_health_history:
            self.node_health_history[node_id] = deque(maxlen=500)
        
        self.node_health_history[node_id].append({
            'timestamp': entry['timestamp'],
            'risk_score': risk_score
        })
    
    def record_risk_event(self, node_id, risk_score, risk_factors):
        """Record risk detection events"""
        self.risk_timeline.append({
            'timestamp': datetime.now().isoformat(),
            'node_id': node_id,
            'risk_score': risk_score,
            'factors': risk_factors
        })
    
    def get_node_health_trend(self, node_id, hours=24):
        """Get health trend for a node over time"""
        if node_id not in self.node_health_history:
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        trend = [
            entry for entry in self.node_health_history[node_id]
            if datetime.fromisoformat(entry['timestamp']) > cutoff
        ]
        return trend
    
    def get_risk_statistics(self):
        """Get risk statistics across the cluster"""
        if not self.metrics_history:
            return {
                'average_risk': 0,
                'max_risk': 0,
                'min_risk': 0,
                'std_dev': 0,
                'critical_events': 0,
                'total_events': 0
            }
        
        risk_scores = [entry['risk_score'] for entry in self.metrics_history]
        
        return {
            'average_risk': float(np.mean(risk_scores)),
            'max_risk': float(np.max(risk_scores)),
            'min_risk': float(np.min(risk_scores)),
            'std_dev': float(np.std(risk_scores)),
            'critical_events': len([s for s in risk_scores if s > 0.75]),
            'total_events': len(risk_scores)
        }
    
    def calculate_node_health_score(self, node_id):
        """Calculate overall health score for a node (0-100)"""
        if node_id not in self.node_health_history or not self.node_health_history[node_id]:
            return 100
        
        recent = list(self.node_health_history[node_id])[-50:]
        avg_risk = np.mean([entry['risk_score'] for entry in recent])
        
        # Convert risk to health score
        health_score = max(0, min(100, 100 - (avg_risk * 100)))
        return float(health_score)
    
    def get_top_risk_nodes(self, limit=5):
        """Get nodes with highest risk scores"""
        node_risks = {}
        
        for node_id, history in self.node_health_history.items():
            if history:
                recent = list(history)[-10:]
                avg_risk = np.mean([e['risk_score'] for e in recent])
                node_risks[node_id] = avg_risk
        
        sorted_nodes = sorted(node_risks.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:limit]
    
    def get_cluster_health(self):
        """Get overall cluster health metrics based on real node data"""
        try:
            # Get current node data
            from kubernetes_manager import KubernetesManager
            from health_scorer import HealthScorer
            
            k8s_mgr = KubernetesManager()
            
            if k8s_mgr.available:
                nodes = k8s_mgr.get_nodes_metrics()
            else:
                # Import demo nodes if available
                try:
                    from app import demo_nodes
                    nodes = list(demo_nodes.values()) if demo_nodes else []
                except:
                    nodes = []
            
            if not nodes:
                return {
                    'cluster_health_score': 100,
                    'average_node_health': 100,
                    'nodes_at_risk': 0,
                    'cluster_health_trend': 'stable',
                    'healthy_nodes': 0,
                    'degraded_nodes': 0,
                    'critical_nodes': 0
                }
            
            # Calculate health metrics from actual nodes
            health_scores = []
            at_risk_count = 0
            healthy_count = 0
            degraded_count = 0
            critical_count = 0
            
            for node in nodes:
                health_info = HealthScorer.calculate_overall_health(node)
                score = health_info.get('overall_score', 100)
                status = health_info.get('status', 'healthy')
                
                health_scores.append(score)
                
                if status == 'critical':
                    at_risk_count += 1
                    critical_count += 1
                elif status == 'degraded':
                    degraded_count += 1
                else:
                    healthy_count += 1
            
            avg_health = np.mean(health_scores) if health_scores else 100
            cluster_health = max(0, avg_health)
            
            # Determine trend based on historical data
            trend = 'stable'
            if self.metrics_history:
                recent_scores = [e.get('risk_score', 0) for e in list(self.metrics_history)[-10:]]
                if len(recent_scores) >= 3:
                    # Calculate trend using linear regression
                    trend_slope = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
                    if trend_slope > 0.05:
                        trend = 'degrading'
                    elif trend_slope < -0.05:
                        trend = 'improving'
                    else:
                        trend = 'stable'
            
            return {
                'cluster_health_score': round(cluster_health, 1),
                'average_node_health': round(avg_health, 1),
                'nodes_at_risk': at_risk_count,
                'cluster_health_trend': trend,
                'healthy_nodes': healthy_count,
                'degraded_nodes': degraded_count,
                'critical_nodes': critical_count,
                'total_nodes': len(nodes)
            }
        except Exception as e:
            import logging
            logging.error(f"Error calculating cluster health: {e}")
            return {
                'cluster_health_score': 100,
                'average_node_health': 100,
                'nodes_at_risk': 0,
                'cluster_health_trend': 'stable',
                'healthy_nodes': 0,
                'degraded_nodes': 0,
                'critical_nodes': 0
            }
    
    def get_predictions(self, node_id):
        """Get predictive insights for a node"""
        if node_id not in self.node_health_history:
            return {'prediction': 'insufficient_data'}
        
        history = list(self.node_health_history[node_id])[-20:]
        if len(history) < 5:
            return {'prediction': 'insufficient_data'}
        
        risk_scores = [e['risk_score'] for e in history]
        trend = np.polyfit(range(len(risk_scores)), risk_scores, 1)[0]
        
        if trend > 0.05:
            return {
                'prediction': 'degrading',
                'confidence': min(100, abs(trend) * 500),
                'recommendation': 'Schedule maintenance'
            }
        elif trend < -0.05:
            return {
                'prediction': 'improving',
                'confidence': min(100, abs(trend) * 500),
                'recommendation': 'Monitor for stability'
            }
        else:
            return {
                'prediction': 'stable',
                'confidence': 90,
                'recommendation': 'Continue normal operations'
            }
    
    def export_metrics(self, format='json'):
        """Export historical metrics"""
        data = {
            'exported': datetime.now().isoformat(),
            'total_records': len(self.metrics_history),
            'nodes': len(self.node_health_history),
            'cluster_health': self.get_cluster_health(),
            'risk_statistics': self.get_risk_statistics(),
            'top_risk_nodes': self.get_top_risk_nodes(10)
        }
        
        if format == 'json':
            return json.dumps(data, indent=2)
        return data
