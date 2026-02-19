"""
Health Scoring System - Comprehensive node health evaluation
Provides detailed health grades and recommendations
"""

import logging

logger = logging.getLogger(__name__)


class HealthScorer:
    """Calculate comprehensive health scores for nodes"""
    
    # Weight factors for different metrics
    WEIGHTS = {
        'cpu': 0.25,
        'memory': 0.25,
        'temperature': 0.20,
        'latency': 0.15,
        'disk_io': 0.15
    }
    
    # Threshold ranges for different metrics (0-100 scale)
    THRESHOLDS = {
        'cpu': {'critical': 90, 'warning': 75, 'ok': 50},
        'memory': {'critical': 90, 'warning': 80, 'ok': 60},
        'temperature': {'critical': 85, 'warning': 70, 'ok': 50},
        'latency': {'critical': 50, 'warning': 30, 'ok': 10},
        'disk_io': {'critical': 85, 'warning': 70, 'ok': 40}
    }
    
    @classmethod
    def calculate_component_health(cls, metric_name, value):
        """Calculate health score for a single metric (0-100)"""
        thresholds = cls.THRESHOLDS.get(metric_name, {'critical': 100, 'warning': 75, 'ok': 50})
        
        if value >= thresholds['critical']:
            return 0
        elif value >= thresholds['warning']:
            return 25
        elif value >= thresholds['ok']:
            return 50
        else:
            return 100
    
    @classmethod
    def calculate_overall_health(cls, node_data):
        """
        Calculate comprehensive health score
        
        Returns:
            {
                'overall_score': 0-100,
                'grade': 'A+' to 'F',
                'status': 'healthy', 'degraded', 'critical',
                'component_scores': dict,
                'issues': list,
                'recommendations': list
            }
        """
        scores = {}
        issues = []
        recommendations = []
        
        # CPU score
        cpu = node_data.get('cpu_usage', 0)
        scores['cpu'] = cls.calculate_component_health('cpu', cpu)
        if cpu > 80:
            issues.append(f'High CPU usage: {cpu:.1f}%')
            recommendations.append('Check running processes and consider scaling')
        
        # Memory score
        memory = node_data.get('memory_usage', 0)
        scores['memory'] = cls.calculate_component_health('memory', memory)
        if memory > 85:
            issues.append(f'High memory usage: {memory:.1f}%')
            recommendations.append('Review container limits and optimize applications')
        
        # Temperature score
        temp = node_data.get('temperature', 50)
        scores['temperature'] = cls.calculate_component_health('temperature', temp)
        if temp > 75:
            issues.append(f'High temperature: {temp:.1f}°C')
            recommendations.append('Improve cooling or check for thermal issues')
        
        # Network latency score
        latency = node_data.get('network_latency', 0)
        scores['latency'] = cls.calculate_component_health('latency', latency)
        if latency > 30:
            issues.append(f'High network latency: {latency:.1f}ms')
            recommendations.append('Check network connectivity and bandwidth')
        
        # Disk I/O score
        disk = node_data.get('disk_io', 0)
        scores['disk_io'] = cls.calculate_component_health('disk_io', disk)
        if disk > 75:
            issues.append(f'High disk I/O: {disk:.1f}%')
            recommendations.append('Monitor disk operations and consider SSD upgrade')
        
        # Calculate weighted overall score
        overall = sum(scores[key] * cls.WEIGHTS[key] for key in scores)
        
        # Determine grade
        grade = cls._score_to_grade(overall)
        
        # Determine status
        if overall >= 80:
            status = 'healthy'
        elif overall >= 50:
            status = 'degraded'
        else:
            status = 'critical'
        
        return {
            'overall_score': round(overall, 1),
            'grade': grade,
            'status': status,
            'component_scores': scores,
            'issues': issues,
            'recommendations': recommendations,
            'pod_count': len(node_data.get('pods', [])),
            'taints': len(node_data.get('taints', []))
        }
    
    @staticmethod
    def _score_to_grade(score):
        """Convert numeric score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    @staticmethod
    def get_sla_status(overall_score):
        """Determine SLA compliance status"""
        if overall_score >= 95:
            return {'status': 'compliant', 'sla_level': '99.99%', 'margin': overall_score - 95}
        elif overall_score >= 90:
            return {'status': 'compliant', 'sla_level': '99.9%', 'margin': overall_score - 90}
        elif overall_score >= 80:
            return {'status': 'compliant', 'sla_level': '99%', 'margin': overall_score - 80}
        else:
            return {'status': 'non-compliant', 'sla_level': '<99%', 'margin': 0}
