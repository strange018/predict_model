"""
Event Management System
Tracks and manages all system events for frontend display and analysis
"""

import uuid
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)


class EventManager:
    """Manages system events with history and filtering"""
    
    def __init__(self, max_events=200):
        self.events = deque(maxlen=max_events)
        self.max_events = max_events
        self.event_stats = {
            'total': 0,
            'by_type': {'risk': 0, 'action': 0, 'info': 0}
        }
    
    def add_event(self, event_data):
        """
        Add an event to the manager
        
        Args:
            event_data: Dict with 'type', 'title', 'description', and optional 'details', 'nodeId'
        """
        try:
            event = {
                'id': str(uuid.uuid4()),
                'type': event_data.get('type', 'info'),  # 'risk', 'action', 'info'
                'title': event_data.get('title', 'Unknown Event'),
                'description': event_data.get('description', ''),
                'nodeId': event_data.get('nodeId', None),
                'details': event_data.get('details', {}),
                'timestamp': datetime.now().isoformat(),
                'timeString': self._format_time(datetime.now())
            }
            
            self.events.appendleft(event)
            
            # Update stats
            self.event_stats['total'] += 1
            event_type = event['type']
            if event_type in self.event_stats['by_type']:
                self.event_stats['by_type'][event_type] += 1
            
            logger.info(f"📝 Event: {event['type'].upper()} - {event['title']}")
            
            return event
        
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            return None
    
    def get_events(self, event_type=None, limit=None):
        """
        Get events with optional filtering
        
        Args:
            event_type: Filter by type ('risk', 'action', 'info', or None for all)
            limit: Limit number of events returned
        
        Returns:
            List of events (most recent first)
        """
        filtered_events = list(self.events)
        
        if event_type:
            filtered_events = [e for e in filtered_events if e['type'] == event_type]
        
        if limit:
            filtered_events = filtered_events[:limit]
        
        return filtered_events
    
    def get_events_by_node(self, node_id):
        """Get all events related to a specific node"""
        return [e for e in self.events if e.get('nodeId') == node_id]
    
    def get_recent_events(self, minutes=60):
        """Get events from the last N minutes"""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            e for e in self.events 
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
    
    def get_stats(self):
        """Get event statistics"""
        return self.event_stats.copy()
    
    def get_event_by_id(self, event_id):
        """Get a specific event by ID"""
        return next((e for e in self.events if e['id'] == event_id), None)
    
    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        logger.info("Event log cleared")
    
    def _format_time(self, dt):
        """Format datetime to HH:MM:SS"""
        return dt.strftime('%H:%M:%S')
    
    def export_events(self, format='json'):
        """
        Export events in various formats
        
        Args:
            format: 'json' or 'csv'
        
        Returns:
            Formatted event data
        """
        if format == 'json':
            import json
            return json.dumps(list(self.events), indent=2, default=str)
        
        elif format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['id', 'type', 'title', 'description', 'timestamp']
            )
            writer.writeheader()
            writer.writerows(self.events)
            return output.getvalue()
        
        else:
            raise ValueError(f"Unknown export format: {format}")
