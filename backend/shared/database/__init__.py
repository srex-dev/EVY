"""Edge-Optimized Database Module

Provides SQLite database integration optimized for edge deployment.
"""

from backend.shared.database.edge_db import (
    EdgeDatabase,
    MessageRecord,
    AnalyticsRecord,
    EmergencyLogRecord,
)

__all__ = [
    'EdgeDatabase',
    'MessageRecord',
    'AnalyticsRecord',
    'EmergencyLogRecord',
]

