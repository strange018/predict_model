"""
Audit Logger - Comprehensive action tracking and compliance logging
"""

import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """Professional audit logging for compliance and tracking"""
    
    def __init__(self, max_records=100000):
        self.max_records = max_records
        self.audit_log = []
    
    def log_action(self, action_type, resource, actor='system', status='success', details=None):
        """
        Log an action with full context
        
        Args:
            action_type: 'CREATE', 'UPDATE', 'DELETE', 'MIGRATE', 'TAINT', 'DRAIN', etc.
            resource: 'node', 'pod', 'cluster', etc.
            actor: Who performed the action
            status: 'success', 'failure', 'pending'
            details: Additional context
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action_type,
            'resource': resource,
            'actor': actor,
            'status': status,
            'details': details or {},
            'unix_timestamp': datetime.now().timestamp()
        }
        
        self.audit_log.append(entry)
        
        # Keep only recent records
        if len(self.audit_log) > self.max_records:
            self.audit_log = self.audit_log[-self.max_records:]
        
        # Log to file
        logger.info(f"AUDIT: {action_type}:{resource} by {actor} - {status}")
        
        return entry
    
    def get_audit_trail(self, action_type=None, resource=None, limit=100):
        """Get filtered audit log"""
        results = self.audit_log
        
        if action_type:
            results = [r for r in results if r['action'] == action_type]
        if resource:
            results = [r for r in results if r['resource'] == resource]
        
        return results[-limit:]
    
    def get_user_activity(self, actor, limit=50):
        """Get all actions by a specific actor"""
        return [r for r in self.audit_log if r['actor'] == actor][-limit:]
    
    def get_statistics(self):
        """Get audit statistics"""
        if not self.audit_log:
            return {}
        
        actions = {}
        failures = 0
        
        for entry in self.audit_log:
            action = entry['action']
            actions[action] = actions.get(action, 0) + 1
            if entry['status'] == 'failure':
                failures += 1
        
        return {
            'total_actions': len(self.audit_log),
            'action_breakdown': actions,
            'total_failures': failures,
            'failure_rate': (failures / len(self.audit_log)) * 100 if self.audit_log else 0
        }
    
    def export_audit_log(self, format='json'):
        """Export audit log"""
        if format == 'json':
            return json.dumps(self.audit_log, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if self.audit_log:
                writer = csv.DictWriter(output, fieldnames=self.audit_log[0].keys())
                writer.writeheader()
                writer.writerows(self.audit_log)
            
            return output.getvalue()
        
        return self.audit_log
