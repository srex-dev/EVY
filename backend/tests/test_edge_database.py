"""Tests for Edge Database"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from backend.shared.database.edge_db import EdgeDatabase


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = EdgeDatabase(db_path=db_path)
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.mark.asyncio
async def test_database_initialization(temp_db):
    """Test database initialization"""
    # Database should be initialized
    stats = temp_db.get_database_stats()
    assert stats is not None
    assert 'message_count' in stats
    assert 'analytics_count' in stats


@pytest.mark.asyncio
async def test_insert_message(temp_db):
    """Test message insertion"""
    # Insert message
    message_id = temp_db.insert_message(
        phone_number="+1234567890",
        content="Test message",
        response="Test response",
        priority=1,
        batch=False  # Immediate insert for testing
    )
    
    assert message_id > 0
    
    # Retrieve message
    messages = temp_db.get_messages(limit=1)
    assert len(messages) == 1
    assert messages[0]['phone_number'] == "+1234567890"
    assert messages[0]['content'] == "Test message"


@pytest.mark.asyncio
async def test_batch_insert(temp_db):
    """Test batch message insertion"""
    # Start batch commits
    await temp_db.start_batch_commits()
    
    # Insert multiple messages (batched)
    for i in range(5):
        temp_db.insert_message(
            phone_number=f"+123456789{i}",
            content=f"Message {i}",
            batch=True
        )
    
    # Flush batch
    await temp_db._flush_batch()
    
    # Stop batch commits
    await temp_db.stop_batch_commits()
    
    # Verify messages were inserted
    messages = temp_db.get_messages(limit=10)
    assert len(messages) >= 5


@pytest.mark.asyncio
async def test_insert_analytics(temp_db):
    """Test analytics insertion"""
    # Insert analytics
    analytics_id = temp_db.insert_analytics(
        metric="response_time",
        value=1.5,
        batch=False
    )
    
    assert analytics_id > 0
    
    # Retrieve analytics
    analytics = temp_db.get_analytics(metric="response_time", limit=1)
    assert len(analytics) == 1
    assert analytics[0]['metric'] == "response_time"
    assert analytics[0]['value'] == 1.5


@pytest.mark.asyncio
async def test_insert_emergency_log(temp_db):
    """Test emergency log insertion"""
    # Insert emergency log
    log_id = temp_db.insert_emergency_log(
        phone_number="+1234567890",
        message="EMERGENCY! Help!",
        response="Emergency response sent",
        batch=False
    )
    
    assert log_id > 0
    
    # Retrieve emergency logs
    logs = temp_db.get_emergency_logs(limit=1)
    assert len(logs) == 1
    assert logs[0]['phone_number'] == "+1234567890"
    assert "EMERGENCY" in logs[0]['message']


@pytest.mark.asyncio
async def test_get_messages_by_phone(temp_db):
    """Test getting messages by phone number"""
    # Insert messages from different numbers
    temp_db.insert_message("+1111111111", "Message 1", batch=False)
    temp_db.insert_message("+2222222222", "Message 2", batch=False)
    temp_db.insert_message("+1111111111", "Message 3", batch=False)
    
    # Get messages for specific number
    messages = temp_db.get_messages(phone_number="+1111111111")
    assert len(messages) == 2
    assert all(msg['phone_number'] == "+1111111111" for msg in messages)


@pytest.mark.asyncio
async def test_data_retention(temp_db):
    """Test data retention cleanup"""
    # Insert old message (simulated)
    old_timestamp = int((datetime.utcnow() - timedelta(days=100)).timestamp())
    
    # Insert directly with old timestamp
    with temp_db._get_connection() as conn:
        conn.execute("""
            INSERT INTO messages (phone_number, content, timestamp)
            VALUES (?, ?, ?)
        """, ("+1234567890", "Old message", old_timestamp))
        conn.commit()
    
    # Cleanup old data (90 days retention)
    result = temp_db.cleanup_old_data(days=90)
    
    assert result['messages_deleted'] >= 1
    
    # Verify message was deleted
    messages = temp_db.get_messages()
    assert len(messages) == 0 or all(msg['timestamp'] > old_timestamp for msg in messages)


@pytest.mark.asyncio
async def test_database_stats(temp_db):
    """Test database statistics"""
    # Insert some data
    temp_db.insert_message("+1234567890", "Test", batch=False)
    temp_db.insert_analytics("test_metric", 1.0, batch=False)
    
    # Get stats
    stats = temp_db.get_database_stats()
    
    assert stats['message_count'] >= 1
    assert stats['analytics_count'] >= 1
    assert 'database_size_mb' in stats
    assert 'pending_writes' in stats


@pytest.mark.asyncio
async def test_batch_commit_loop(temp_db):
    """Test batch commit background loop"""
    # Start batch commits
    await temp_db.start_batch_commits()
    
    # Insert messages (batched)
    for i in range(3):
        temp_db.insert_message(f"+123456789{i}", f"Message {i}", batch=True)
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Stop batch commits (will flush)
    await temp_db.stop_batch_commits()
    
    # Verify messages were committed
    messages = temp_db.get_messages(limit=10)
    assert len(messages) >= 3


def test_wal_mode(temp_db):
    """Test WAL mode is enabled"""
    with temp_db._get_connection() as conn:
        cursor = conn.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        assert journal_mode.upper() == 'WAL'


def test_memory_mapped_io(temp_db):
    """Test memory-mapped I/O is configured"""
    with temp_db._get_connection() as conn:
        cursor = conn.execute("PRAGMA mmap_size")
        mmap_size = cursor.fetchone()[0]
        assert mmap_size > 0  # Should be set to 256MB

