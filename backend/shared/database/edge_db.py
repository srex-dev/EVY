"""Edge-Optimized SQLite Database

Lightweight SQLite database optimized for Raspberry Pi 4 edge constraints:
- WAL mode for faster writes
- Batch operations to reduce microSD wear
- Memory-mapped I/O
- Data retention policies
"""

import sqlite3
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import contextmanager
import json

logger = logging.getLogger(__name__)


@dataclass
class MessageRecord:
    """Message record structure"""
    id: Optional[int] = None
    phone_number: str = ""
    content: str = ""
    response: Optional[str] = None
    timestamp: int = 0
    priority: int = 1  # 0=Low, 1=Normal, 2=High, 3=Emergency


@dataclass
class AnalyticsRecord:
    """Analytics record structure"""
    id: Optional[int] = None
    metric: str = ""
    value: float = 0.0
    timestamp: int = 0


@dataclass
class EmergencyLogRecord:
    """Emergency log record structure"""
    id: Optional[int] = None
    phone_number: str = ""
    message: str = ""
    response: str = ""
    timestamp: int = 0


class EdgeDatabase:
    """Edge-optimized SQLite database"""
    
    def __init__(self, db_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db_path = db_path or self.config.get('db_path', '/data/evy.db')
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Batch operation settings
        self.batch_size = self.config.get('batch_size', 10)
        self.batch_timeout = self.config.get('batch_timeout', 60)  # seconds
        self.pending_writes: List[Dict[str, Any]] = []
        self.last_commit = datetime.utcnow()
        
        # Data retention
        self.retention_days = self.config.get('retention_days', 90)  # Keep 90 days
        
        # Initialize database
        self._initialize_database()
        
        # Start batch commit task
        self._batch_task: Optional[asyncio.Task] = None
        self._running = False
    
    def _initialize_database(self) -> None:
        """Initialize database with edge-optimized settings"""
        with self._get_connection() as conn:
            # Set edge-optimized pragmas
            conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
            conn.execute("PRAGMA synchronous = NORMAL")  # Balance safety/speed
            conn.execute("PRAGMA cache_size = -32000")  # 32MB cache
            conn.execute("PRAGMA temp_store = MEMORY")  # Use memory for temp tables
            conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
            conn.execute("PRAGMA page_size = 4096")  # 4KB pages
            
            # Create schema
            self._create_schema(conn)
            
            conn.commit()
        
        logger.info(f"Database initialized at {self.db_path} with edge optimizations")
    
    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create database schema"""
        # Messages table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                content TEXT NOT NULL,
                response TEXT,
                timestamp INTEGER NOT NULL,
                priority INTEGER DEFAULT 1,
                created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Analytics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Emergency logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emergency_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone_number)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_priority ON messages(priority)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_emergency_timestamp ON emergency_logs(timestamp)")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
        try:
            yield conn
        finally:
            conn.close()
    
    async def start_batch_commits(self) -> None:
        """Start background task for batch commits"""
        if self._running:
            return
        
        self._running = True
        self._batch_task = asyncio.create_task(self._batch_commit_loop())
        logger.info("Started batch commit task")
    
    async def stop_batch_commits(self) -> None:
        """Stop batch commit task and flush pending writes"""
        self._running = False
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
        
        # Flush pending writes
        await self._flush_batch()
        logger.info("Stopped batch commit task")
    
    async def _batch_commit_loop(self) -> None:
        """Background loop for batch commits"""
        while self._running:
            try:
                await asyncio.sleep(self.batch_timeout)
                await self._flush_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch commit error: {e}")
    
    async def _flush_batch(self) -> None:
        """Flush pending batch writes"""
        if not self.pending_writes:
            return
        
        writes = self.pending_writes.copy()
        self.pending_writes.clear()
        
        try:
            with self._get_connection() as conn:
                for write in writes:
                    if write['type'] == 'message':
                        self._insert_message_direct(conn, write['data'])
                    elif write['type'] == 'analytics':
                        self._insert_analytics_direct(conn, write['data'])
                    elif write['type'] == 'emergency':
                        self._insert_emergency_direct(conn, write['data'])
                
                conn.commit()
                self.last_commit = datetime.utcnow()
            
            logger.debug(f"Flushed {len(writes)} batch writes")
        except Exception as e:
            logger.error(f"Batch flush error: {e}")
            # Re-add failed writes
            self.pending_writes.extend(writes)
    
    def insert_message(
        self,
        phone_number: str,
        content: str,
        response: Optional[str] = None,
        priority: int = 1,
        batch: bool = True
    ) -> int:
        """Insert message record"""
        timestamp = int(datetime.utcnow().timestamp())
        
        if batch:
            self.pending_writes.append({
                'type': 'message',
                'data': {
                    'phone_number': phone_number,
                    'content': content,
                    'response': response,
                    'timestamp': timestamp,
                    'priority': priority,
                }
            })
            
            # Auto-flush if batch size reached
            if len(self.pending_writes) >= self.batch_size:
                asyncio.create_task(self._flush_batch())
            
            return 0  # ID will be assigned on commit
        else:
            with self._get_connection() as conn:
                row_id = self._insert_message_direct(conn, {
                    'phone_number': phone_number,
                    'content': content,
                    'response': response,
                    'timestamp': timestamp,
                    'priority': priority,
                })
                conn.commit()
                return row_id
    
    def _insert_message_direct(self, conn: sqlite3.Connection, data: Dict[str, Any]) -> int:
        """Direct message insert (for batch operations)"""
        cursor = conn.execute("""
            INSERT INTO messages (phone_number, content, response, timestamp, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['phone_number'],
            data['content'],
            data.get('response'),
            data['timestamp'],
            data.get('priority', 1),
        ))
        return cursor.lastrowid
    
    def insert_analytics(
        self,
        metric: str,
        value: float,
        batch: bool = True
    ) -> int:
        """Insert analytics record"""
        timestamp = int(datetime.utcnow().timestamp())
        
        if batch:
            self.pending_writes.append({
                'type': 'analytics',
                'data': {
                    'metric': metric,
                    'value': value,
                    'timestamp': timestamp,
                }
            })
            
            if len(self.pending_writes) >= self.batch_size:
                asyncio.create_task(self._flush_batch())
            
            return 0
        else:
            with self._get_connection() as conn:
                row_id = self._insert_analytics_direct(conn, {
                    'metric': metric,
                    'value': value,
                    'timestamp': timestamp,
                })
                conn.commit()
                return row_id
    
    def _insert_analytics_direct(self, conn: sqlite3.Connection, data: Dict[str, Any]) -> int:
        """Direct analytics insert"""
        cursor = conn.execute("""
            INSERT INTO analytics (metric, value, timestamp)
            VALUES (?, ?, ?)
        """, (
            data['metric'],
            data['value'],
            data['timestamp'],
        ))
        return cursor.lastrowid
    
    def insert_emergency_log(
        self,
        phone_number: str,
        message: str,
        response: str,
        batch: bool = True
    ) -> int:
        """Insert emergency log record"""
        timestamp = int(datetime.utcnow().timestamp())
        
        if batch:
            self.pending_writes.append({
                'type': 'emergency',
                'data': {
                    'phone_number': phone_number,
                    'message': message,
                    'response': response,
                    'timestamp': timestamp,
                }
            })
            
            # Emergency logs are higher priority, flush immediately if batch full
            if len(self.pending_writes) >= self.batch_size:
                asyncio.create_task(self._flush_batch())
            
            return 0
        else:
            with self._get_connection() as conn:
                row_id = self._insert_emergency_direct(conn, {
                    'phone_number': phone_number,
                    'message': message,
                    'response': response,
                    'timestamp': timestamp,
                })
                conn.commit()
                return row_id
    
    def _insert_emergency_direct(self, conn: sqlite3.Connection, data: Dict[str, Any]) -> int:
        """Direct emergency log insert"""
        cursor = conn.execute("""
            INSERT INTO emergency_logs (phone_number, message, response, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            data['phone_number'],
            data['message'],
            data['response'],
            data['timestamp'],
        ))
        return cursor.lastrowid
    
    def get_messages(
        self,
        phone_number: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages with optional filtering"""
        with self._get_connection() as conn:
            if phone_number:
                cursor = conn.execute("""
                    SELECT * FROM messages
                    WHERE phone_number = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (phone_number, limit, offset))
            else:
                cursor = conn.execute("""
                    SELECT * FROM messages
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_analytics(
        self,
        metric: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get analytics records"""
        with self._get_connection() as conn:
            query = "SELECT * FROM analytics WHERE 1=1"
            params = []
            
            if metric:
                query += " AND metric = ?"
                params.append(metric)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_emergency_logs(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get emergency logs"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM emergency_logs
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days: Optional[int] = None) -> Dict[str, int]:
        """Clean up old data based on retention policy"""
        days = days or self.retention_days
        cutoff_timestamp = int((datetime.utcnow() - timedelta(days=days)).timestamp())
        
        with self._get_connection() as conn:
            # Delete old messages
            cursor1 = conn.execute("""
                DELETE FROM messages
                WHERE timestamp < ?
            """, (cutoff_timestamp,))
            messages_deleted = cursor1.rowcount
            
            # Delete old analytics (keep longer, but still cleanup)
            cursor2 = conn.execute("""
                DELETE FROM analytics
                WHERE timestamp < ?
            """, (cutoff_timestamp,))
            analytics_deleted = cursor2.rowcount
            
            # Keep emergency logs longer (don't delete)
            emergency_deleted = 0
            
            conn.commit()
            
            # Vacuum database to reclaim space
            conn.execute("VACUUM")
            
            logger.info(f"Cleaned up {messages_deleted} messages, {analytics_deleted} analytics records")
            
            return {
                'messages_deleted': messages_deleted,
                'analytics_deleted': analytics_deleted,
                'emergency_deleted': emergency_deleted,
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._get_connection() as conn:
            # Get table sizes
            cursor = conn.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM messages) as message_count,
                    (SELECT COUNT(*) FROM analytics) as analytics_count,
                    (SELECT COUNT(*) FROM emergency_logs) as emergency_count
            """)
            row = cursor.fetchone()
            
            # Get database file size
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            
            return {
                'message_count': row['message_count'],
                'analytics_count': row['analytics_count'],
                'emergency_count': row['emergency_count'],
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'pending_writes': len(self.pending_writes),
                'last_commit': self.last_commit.isoformat() if self.last_commit else None,
            }

