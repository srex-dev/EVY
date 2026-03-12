# Edge-Optimized SQLite Database

## Overview

Lightweight SQLite database optimized for Raspberry Pi 4 edge constraints with WAL mode, batch operations, and data retention policies.

## Features

- **WAL Mode**: Write-Ahead Logging for faster writes and less microSD wear
- **Batch Operations**: Reduces write frequency to protect microSD
- **Memory-Mapped I/O**: 256MB memory-mapped I/O for faster access
- **Data Retention**: Automatic cleanup of old data
- **Minimal Schema**: Messages, analytics, emergency logs only
- **Edge Optimized**: 32MB cache, normal sync mode

## Architecture

```
EdgeDatabase
├── Messages Table (SMS messages)
├── Analytics Table (metrics)
├── Emergency Logs Table (emergency records)
└── Batch Commit System (background flushing)
```

## Schema

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    content TEXT NOT NULL,
    response TEXT,
    timestamp INTEGER NOT NULL,
    priority INTEGER DEFAULT 1,
    created_at INTEGER NOT NULL
);
```

### Analytics Table
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);
```

### Emergency Logs Table
```sql
CREATE TABLE emergency_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);
```

## Usage

### Basic Database Operations

```python
from backend.shared.database import EdgeDatabase

# Initialize database
db = EdgeDatabase(db_path='/data/evy.db')

# Start batch commits (background task)
await db.start_batch_commits()

# Insert message (batched)
db.insert_message(
    phone_number="+1234567890",
    content="Hello!",
    response="Hi there!",
    priority=1,
    batch=True  # Batched write
)

# Insert analytics (batched)
db.insert_analytics(
    metric="response_time",
    value=1.5,
    batch=True
)

# Insert emergency log (batched)
db.insert_emergency_log(
    phone_number="+1234567890",
    message="EMERGENCY!",
    response="Emergency response sent",
    batch=True
)

# Stop batch commits (flushes pending writes)
await db.stop_batch_commits()
```

### Query Operations

```python
# Get messages
messages = db.get_messages(limit=100)

# Get messages by phone number
user_messages = db.get_messages(phone_number="+1234567890", limit=50)

# Get analytics
analytics = db.get_analytics(metric="response_time", limit=1000)

# Get emergency logs
emergency_logs = db.get_emergency_logs(limit=100)
```

### Data Retention

```python
# Clean up old data (default: 90 days)
result = db.cleanup_old_data()

print(f"Deleted {result['messages_deleted']} messages")
print(f"Deleted {result['analytics_deleted']} analytics records")

# Custom retention period
result = db.cleanup_old_data(days=30)  # Keep 30 days
```

### Database Statistics

```python
stats = db.get_database_stats()

print(f"Messages: {stats['message_count']}")
print(f"Analytics: {stats['analytics_count']}")
print(f"Emergency logs: {stats['emergency_count']}")
print(f"Database size: {stats['database_size_mb']}MB")
print(f"Pending writes: {stats['pending_writes']}")
```

## Configuration

### Edge-Optimized Pragmas

```python
PRAGMA journal_mode = WAL;           # Write-Ahead Logging
PRAGMA synchronous = NORMAL;        # Balance safety/speed
PRAGMA cache_size = -32000;         # 32MB cache
PRAGMA temp_store = MEMORY;         # Use memory for temp tables
PRAGMA mmap_size = 268435456;       # 256MB memory-mapped I/O
PRAGMA page_size = 4096;            # 4KB pages
```

### Configuration Dictionary

```python
config = {
    'db_path': '/data/evy.db',
    'batch_size': 10,  # Flush after 10 writes
    'batch_timeout': 60,  # Or flush after 60 seconds
    'retention_days': 90,  # Keep data for 90 days
}

db = EdgeDatabase(config=config)
```

## Performance Targets

- **Database Size**: <2GB (with growth)
- **Write Latency**: <100ms (batch)
- **Memory Usage**: <500MB (cache + mmap)
- **WAL Mode**: Enabled for faster writes

## Edge Optimizations

1. **WAL Mode**: Faster writes, less microSD wear
2. **Batch Commits**: Reduces write frequency (every 10 writes or 60s)
3. **Memory-Mapped I/O**: 256MB for faster reads
4. **32MB Cache**: In-memory cache for frequently accessed data
5. **Normal Sync**: Faster than FULL sync (acceptable for edge)
6. **Data Retention**: Automatic cleanup prevents database growth

## Batch Operations

Batch operations reduce microSD wear by batching writes:

- **Batch Size**: 10 writes (configurable)
- **Batch Timeout**: 60 seconds (configurable)
- **Auto-Flush**: Flushes when batch size reached
- **Manual Flush**: Call `await db._flush_batch()`

## Data Retention

Automatic data retention policies:

- **Messages**: 90 days (configurable)
- **Analytics**: 90 days (configurable)
- **Emergency Logs**: Kept longer (important records)

Cleanup runs manually via `cleanup_old_data()` or can be scheduled.

## Testing

```bash
# Run database tests
pytest backend/tests/test_edge_database.py -v
```

## Troubleshooting

### High Write Latency

1. Check batch size (increase if needed)
2. Verify WAL mode is enabled
3. Check microSD write speed
4. Monitor pending writes count

### Database Size Growing

1. Run `cleanup_old_data()` regularly
2. Reduce `retention_days` if needed
3. Check for large message/analytics records
4. Run `VACUUM` after cleanup

### Memory Usage High

1. Reduce `mmap_size` if needed
2. Reduce `cache_size` if needed
3. Check for memory leaks
4. Monitor database statistics

### WAL Mode Not Working

1. Verify SQLite version supports WAL
2. Check file system permissions
3. Verify database directory is writable
4. Check for file system issues

