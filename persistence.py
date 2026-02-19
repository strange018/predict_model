"""
Persistence Layer - SQLite-based historical data storage
Stores metrics, events, and predictions for trend analysis
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv('DATABASE_PATH', 'metrics_history.db')


class Database:
    """SQLite database manager for metrics persistence"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self._initialize_database()
        logger.info(f"✓ Database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Node metrics history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS node_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    node_name TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    temperature REAL,
                    network_latency REAL,
                    disk_io REAL,
                    pod_count INTEGER,
                    risk_score REAL,
                    health_score REAL,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(node_id, timestamp)
                )
            ''')
            
            # Events history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    node_id TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    risk_score REAL,
                    is_at_risk INTEGER,
                    risk_factors TEXT,
                    confidence REAL,
                    recommendation TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Alerts history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    acknowledged INTEGER DEFAULT 0,
                    resolved INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved_at DATETIME
                )
            ''')
            
            # System metrics table (cluster-wide)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_nodes INTEGER,
                    healthy_nodes INTEGER,
                    degraded_nodes INTEGER,
                    critical_nodes INTEGER,
                    average_health REAL,
                    risks_detected INTEGER,
                    workloads_moved INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_node_time ON node_metrics(node_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_node_time ON predictions(node_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_node ON alerts(node_id, created_at)')
    
    def save_node_metrics(self, node_data: Dict[str, Any], risk_score: float = 0, health_score: float = 100):
        """Save node metrics to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO node_metrics 
                (node_id, node_name, cpu_usage, memory_usage, temperature, 
                 network_latency, disk_io, pod_count, risk_score, health_score, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                node_data.get('node_id'),
                node_data.get('node_name'),
                node_data.get('cpu_usage', 0),
                node_data.get('memory_usage', 0),
                node_data.get('temperature', 0),
                node_data.get('network_latency', 0),
                node_data.get('disk_io', 0),
                len(node_data.get('pods', [])),
                risk_score,
                health_score,
                node_data.get('status', 'unknown'),
                datetime.now().isoformat()
            ))
    
    def save_event(self, event: Dict[str, Any]):
        """Save event to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO events (id, type, title, description, node_id, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('id'),
                event.get('type'),
                event.get('title'),
                event.get('description'),
                event.get('nodeId'),
                json.dumps(event.get('details', {})),
                event.get('timestamp', datetime.now().isoformat())
            ))
    
    def save_prediction(self, node_id: str, prediction: Dict[str, Any]):
        """Save prediction to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions (node_id, risk_score, is_at_risk, risk_factors, confidence, recommendation, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                node_id,
                prediction.get('risk_score', 0),
                1 if prediction.get('is_at_risk') else 0,
                json.dumps(prediction.get('risk_factors', [])),
                prediction.get('confidence', 0),
                prediction.get('recommendation', ''),
                datetime.now().isoformat()
            ))
    
    def save_system_metrics(self, metrics: Dict[str, Any]):
        """Save system-wide metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics 
                (total_nodes, healthy_nodes, degraded_nodes, critical_nodes, 
                 average_health, risks_detected, workloads_moved, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('nodes_monitored', 0),
                metrics.get('nodes_healthy', 0),
                metrics.get('nodes_degraded', 0),
                metrics.get('critical_nodes', 0),
                metrics.get('average_health', 100),
                metrics.get('risks_detected', 0),
                metrics.get('workloads_moved', 0),
                datetime.now().isoformat()
            ))
    
    def create_alert(self, node_id: str, alert_type: str, severity: str, message: str) -> int:
        """Create a new alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (node_id, alert_type, severity, message, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (node_id, alert_type, severity, message, datetime.now().isoformat()))
            return cursor.lastrowid
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE alerts SET resolved = 1, resolved_at = ? WHERE id = ?
            ''', (datetime.now().isoformat(), alert_id))
    
    def get_node_metrics_history(self, node_id: str, hours: int = 24) -> List[Dict]:
        """Get historical metrics for a node"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM node_metrics 
                WHERE node_id = ? AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (node_id, cutoff))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_metrics_history(self, hours: int = 24) -> List[Dict]:
        """Get all historical metrics"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM node_metrics 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 1000
            ''', (cutoff,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_events_history(self, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get historical events"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if event_type:
                cursor.execute('''
                    SELECT * FROM events WHERE type = ? ORDER BY timestamp DESC LIMIT ?
                ''', (event_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM events ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                event['details'] = json.loads(event.get('details', '{}'))
                events.append(event)
            return events
    
    def get_active_alerts(self, node_id: str = None) -> List[Dict]:
        """Get unresolved alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if node_id:
                cursor.execute('''
                    SELECT * FROM alerts WHERE node_id = ? AND resolved = 0 ORDER BY created_at DESC
                ''', (node_id,))
            else:
                cursor.execute('''
                    SELECT * FROM alerts WHERE resolved = 0 ORDER BY created_at DESC
                ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_metrics_history(self, hours: int = 24) -> List[Dict]:
        """Get system metrics history"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_node_trend(self, node_id: str, metric: str = 'risk_score', hours: int = 6) -> List[Dict]:
        """Get trend data for a specific metric"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT timestamp, {metric} as value FROM node_metrics 
                WHERE node_id = ? AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (node_id, cutoff))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the cluster"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get latest metrics per node
            cursor.execute('''
                SELECT node_id, MAX(timestamp) as latest
                FROM node_metrics
                GROUP BY node_id
            ''')
            latest_times = {row['node_id']: row['latest'] for row in cursor.fetchall()}
            
            # Get aggregate stats
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT node_id) as total_nodes,
                    AVG(health_score) as avg_health,
                    AVG(risk_score) as avg_risk,
                    SUM(CASE WHEN risk_score > 0.65 THEN 1 ELSE 0 END) as at_risk_count
                FROM node_metrics
                WHERE timestamp > ?
            ''', ((datetime.now() - timedelta(minutes=5)).isoformat(),))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_nodes': row['total_nodes'] or 0,
                    'average_health': round(row['avg_health'] or 100, 1),
                    'average_risk': round((row['avg_risk'] or 0) * 100, 1),
                    'at_risk_count': row['at_risk_count'] or 0
                }
            return {'total_nodes': 0, 'average_health': 100, 'average_risk': 0, 'at_risk_count': 0}
    
    def cleanup_old_data(self, days: int = 7):
        """Remove data older than specified days"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM node_metrics WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM predictions WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM alerts WHERE resolved = 1 AND resolved_at < ?', (cutoff,))
            logger.info(f"Cleaned up data older than {days} days")


# Global database instance
db = Database()
