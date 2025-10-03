"""Privacy Filter Service - Sanitizes and protects user data."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Set, Any
import re
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

from backend.shared.models import SMSMessage, ServiceHealth
from backend.shared.config import settings
from backend.shared.logging import setup_logger

logger = setup_logger("privacy-filter")


class ConsentStatus(str, Enum):
    """Consent status levels."""
    GRANTED = "granted"
    DENIED = "denied"
    UNKNOWN = "unknown"
    EXPIRED = "expired"


class DataCategory(str, Enum):
    """Data categories for classification."""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    FINANCIAL = "financial"
    MEDICAL = "medical"
    LOCATION = "location"
    CONTACT = "contact"
    IDENTIFIER = "identifier"


class PrivacyFilter:
    """Manages privacy filtering and data sanitization."""
    
    def __init__(self):
        # Data directory for persistent storage
        self.data_dir = Path("/data/privacy_filter")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Patterns for sensitive information with categories
        self.patterns = {
            "phone": {
                "pattern": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
                "category": DataCategory.CONTACT,
                "sensitivity": "medium"
            },
            "email": {
                "pattern": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                "category": DataCategory.CONTACT,
                "sensitivity": "medium"
            },
            "ssn": {
                "pattern": re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
                "category": DataCategory.IDENTIFIER,
                "sensitivity": "high"
            },
            "credit_card": {
                "pattern": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
                "category": DataCategory.FINANCIAL,
                "sensitivity": "high"
            },
            "address": {
                "pattern": re.compile(r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln)\b', re.IGNORECASE),
                "category": DataCategory.LOCATION,
                "sensitivity": "medium"
            },
            "bank_account": {
                "pattern": re.compile(r'\b\d{8,12}\b'),
                "category": DataCategory.FINANCIAL,
                "sensitivity": "high"
            },
            "medical_id": {
                "pattern": re.compile(r'\b(?:patient|medical|hospital|clinic)\s*#?\s*\d{4,8}\b', re.IGNORECASE),
                "category": DataCategory.MEDICAL,
                "sensitivity": "high"
            },
            "passport": {
                "pattern": re.compile(r'\b[A-Z]{2}\d{6,9}\b'),
                "category": DataCategory.IDENTIFIER,
                "sensitivity": "high"
            }
        }
        
        # Rate limiting tracking
        self.message_counts: Dict[str, List[datetime]] = {}
        
        # Consent management
        self.consent_records: Dict[str, Dict[str, Any]] = {}
        self.consent_file = self.data_dir / "consent_records.json"
        
        # Audit log
        self.audit_log: List[Dict[str, Any]] = []
        self.audit_file = self.data_dir / "audit_log.json"
        
        # Blocked patterns and users
        self.blocked_patterns: Set[str] = set()
        self.blocked_users: Set[str] = set()
        self.blocklist_file = self.data_dir / "blocklist.json"
        
        # Statistics
        self.stats = {
            "total_validations": 0,
            "blocked_messages": 0,
            "sanitized_messages": 0,
            "consent_checks": 0,
            "rate_limited_users": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Load persistent data
        self._load_data()
    
    def _load_data(self):
        """Load persistent data from files."""
        try:
            # Load consent records
            if self.consent_file.exists():
                with open(self.consent_file, 'r') as f:
                    self.consent_records = json.load(f)
                logger.info(f"Loaded {len(self.consent_records)} consent records")
            
            # Load audit log (keep last 1000 entries)
            if self.audit_file.exists():
                with open(self.audit_file, 'r') as f:
                    audit_data = json.load(f)
                    self.audit_log = audit_data[-1000:]  # Keep last 1000 entries
                logger.info(f"Loaded {len(self.audit_log)} audit log entries")
            
            # Load blocklist
            if self.blocklist_file.exists():
                with open(self.blocklist_file, 'r') as f:
                    blocklist_data = json.load(f)
                    self.blocked_patterns = set(blocklist_data.get('patterns', []))
                    self.blocked_users = set(blocklist_data.get('users', []))
                logger.info(f"Loaded blocklist: {len(self.blocked_patterns)} patterns, {len(self.blocked_users)} users")
            
        except Exception as e:
            logger.error(f"Failed to load persistent data: {e}")
    
    def _save_data(self):
        """Save persistent data to files."""
        try:
            # Save consent records
            with open(self.consent_file, 'w') as f:
                json.dump(self.consent_records, f, indent=2, default=str)
            
            # Save audit log
            with open(self.audit_file, 'w') as f:
                json.dump(self.audit_log, f, indent=2, default=str)
            
            # Save blocklist
            blocklist_data = {
                'patterns': list(self.blocked_patterns),
                'users': list(self.blocked_users),
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(self.blocklist_file, 'w') as f:
                json.dump(blocklist_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save persistent data: {e}")
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log an audit event."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.audit_log.append(audit_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
        
        # Save periodically
        if len(self.audit_log) % 10 == 0:
            self._save_data()
    
    def sanitize_text(self, text: str, redact: bool = True) -> Dict[str, Any]:
        """Sanitize text by detecting and optionally redacting sensitive information."""
        detected = []
        sanitized_text = text
        risk_score = 0
        
        for pattern_name, pattern_info in self.patterns.items():
            pattern = pattern_info["pattern"]
            category = pattern_info["category"]
            sensitivity = pattern_info["sensitivity"]
            
            matches = pattern.findall(text)
            if matches:
                # Calculate risk score
                match_count = len(matches)
                if sensitivity == "high":
                    risk_score += match_count * 10
                elif sensitivity == "medium":
                    risk_score += match_count * 5
                else:
                    risk_score += match_count * 2
                
                detected.append({
                    "type": pattern_name,
                    "category": category.value,
                    "sensitivity": sensitivity,
                    "count": match_count,
                    "matches": matches[:3]  # Show first 3 matches for debugging
                })
                
                if redact:
                    # Replace with redacted placeholder
                    sanitized_text = pattern.sub(f"[{pattern_name.upper()}_REDACTED]", sanitized_text)
        
        # Log audit event if sensitive data detected
        if detected:
            self._log_audit_event("sensitive_data_detected", {
                "patterns_found": len(detected),
                "risk_score": risk_score,
                "text_length": len(text),
                "redacted": redact
            })
        
        return {
            "original_length": len(text),
            "sanitized_text": sanitized_text,
            "detected_patterns": detected,
            "has_sensitive_data": len(detected) > 0,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 20 else "medium" if risk_score > 10 else "low"
        }
    
    def check_rate_limit(self, phone_number: str) -> Dict[str, any]:
        """Check if user has exceeded rate limits."""
        now = datetime.utcnow()
        
        # Get user's message history
        if phone_number not in self.message_counts:
            self.message_counts[phone_number] = []
        
        user_messages = self.message_counts[phone_number]
        
        # Clean old messages (older than 1 hour)
        user_messages = [
            msg_time for msg_time in user_messages
            if (now - msg_time).total_seconds() < 3600
        ]
        self.message_counts[phone_number] = user_messages
        
        # Count messages in last minute and hour
        messages_last_minute = sum(
            1 for msg_time in user_messages
            if (now - msg_time).total_seconds() < 60
        )
        messages_last_hour = len(user_messages)
        
        # Check limits
        within_minute_limit = messages_last_minute < settings.max_sms_per_minute
        within_hour_limit = messages_last_hour < settings.max_sms_per_hour
        
        return {
            "phone_number": phone_number,
            "messages_last_minute": messages_last_minute,
            "messages_last_hour": messages_last_hour,
            "within_limits": within_minute_limit and within_hour_limit,
            "limit_minute": settings.max_sms_per_minute,
            "limit_hour": settings.max_sms_per_hour
        }
    
    def record_message(self, phone_number: str) -> None:
        """Record a message for rate limiting."""
        if phone_number not in self.message_counts:
            self.message_counts[phone_number] = []
        
        self.message_counts[phone_number].append(datetime.utcnow())
    
    def manage_consent(self, phone_number: str, data_categories: List[str], consent_status: ConsentStatus, expiry_days: int = 365) -> Dict[str, Any]:
        """Manage user consent for data processing."""
        try:
            consent_id = hashlib.md5(f"{phone_number}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
            expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
            
            consent_record = {
                "consent_id": consent_id,
                "phone_number": phone_number,
                "data_categories": data_categories,
                "consent_status": consent_status.value,
                "granted_at": datetime.utcnow().isoformat(),
                "expires_at": expiry_date.isoformat(),
                "is_active": consent_status == ConsentStatus.GRANTED
            }
            
            self.consent_records[consent_id] = consent_record
            self._save_data()
            
            self._log_audit_event("consent_managed", {
                "phone_number": phone_number,
                "consent_status": consent_status.value,
                "data_categories": data_categories,
                "expiry_days": expiry_days
            })
            
            return {
                "success": True,
                "consent_id": consent_id,
                "consent_status": consent_status.value,
                "expires_at": expiry_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to manage consent: {e}")
            return {"success": False, "error": str(e)}
    
    def check_consent(self, phone_number: str, data_categories: List[str]) -> Dict[str, Any]:
        """Check user consent for specific data categories."""
        self.stats["consent_checks"] += 1
        
        # Look for active consent records for this user
        active_consents = []
        for consent_id, record in self.consent_records.items():
            if (record["phone_number"] == phone_number and 
                record["is_active"] and
                datetime.fromisoformat(record["expires_at"]) > datetime.utcnow()):
                
                # Check if consent covers the requested categories
                if any(category in record["data_categories"] for category in data_categories):
                    active_consents.append(record)
        
        if active_consents:
            return {
                "has_consent": True,
                "consent_status": ConsentStatus.GRANTED.value,
                "consent_records": active_consents,
                "covers_categories": data_categories
            }
        else:
            return {
                "has_consent": False,
                "consent_status": ConsentStatus.UNKNOWN.value,
                "required_categories": data_categories
            }
    
    def block_user(self, phone_number: str, reason: str = "Policy violation") -> bool:
        """Block a user from using the service."""
        try:
            self.blocked_users.add(phone_number)
            self._save_data()
            
            self._log_audit_event("user_blocked", {
                "phone_number": phone_number,
                "reason": reason,
                "blocked_by": "system"
            })
            
            logger.warning(f"User {phone_number} blocked: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to block user: {e}")
            return False
    
    def unblock_user(self, phone_number: str, reason: str = "Appeal approved") -> bool:
        """Unblock a user."""
        try:
            if phone_number in self.blocked_users:
                self.blocked_users.remove(phone_number)
                self._save_data()
                
                self._log_audit_event("user_unblocked", {
                    "phone_number": phone_number,
                    "reason": reason,
                    "unblocked_by": "system"
                })
                
                logger.info(f"User {phone_number} unblocked: {reason}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unblock user: {e}")
            return False
    
    def is_user_blocked(self, phone_number: str) -> bool:
        """Check if a user is blocked."""
        return phone_number in self.blocked_users
    
    def validate_message(self, message: SMSMessage) -> Dict[str, Any]:
        """Comprehensive message validation."""
        self.stats["total_validations"] += 1
        
        # Check if user is blocked
        if self.is_user_blocked(message.sender):
            self.stats["blocked_messages"] += 1
            self._log_audit_event("blocked_message_rejected", {
                "phone_number": message.sender,
                "message_length": len(message.content)
            })
            return {
                "valid": False,
                "reason": "user_blocked",
                "details": "User has been blocked from using the service"
            }
        
        # Check rate limits
        rate_check = self.check_rate_limit(message.sender)
        
        if not rate_check["within_limits"]:
            self.stats["rate_limited_users"] += 1
            self._log_audit_event("rate_limit_exceeded", {
                "phone_number": message.sender,
                "messages_last_minute": rate_check["messages_last_minute"],
                "messages_last_hour": rate_check["messages_last_hour"]
            })
            return {
                "valid": False,
                "reason": "rate_limit_exceeded",
                "rate_check": rate_check
            }
        
        # Sanitize content
        sanitized = self.sanitize_text(message.content, redact=False)
        
        # Check for high-risk content
        if sanitized["risk_level"] == "high":
            self.stats["blocked_messages"] += 1
            self._log_audit_event("high_risk_message_blocked", {
                "phone_number": message.sender,
                "risk_score": sanitized["risk_score"],
                "detected_patterns": sanitized["detected_patterns"]
            })
            return {
                "valid": False,
                "reason": "high_risk_content",
                "risk_score": sanitized["risk_score"],
                "detected_patterns": sanitized["detected_patterns"]
            }
        
        # Record message
        self.record_message(message.sender)
        
        # Log successful validation
        self._log_audit_event("message_validated", {
            "phone_number": message.sender,
            "message_length": len(message.content),
            "risk_level": sanitized["risk_level"]
        })
        
        return {
            "valid": True,
            "sanitized": sanitized,
            "rate_check": rate_check,
            "validation_timestamp": datetime.utcnow().isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        self.stats["last_updated"] = datetime.utcnow().isoformat()
        
        return {
            **self.stats,
            "active_users": len(self.message_counts),
            "blocked_users_count": len(self.blocked_users),
            "consent_records_count": len(self.consent_records),
            "audit_log_entries": len(self.audit_log),
            "detection_patterns": len(self.patterns),
            "blocked_patterns_count": len(self.blocked_patterns)
        }
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:] if limit > 0 else self.audit_log
    
    def get_user_consent_records(self, phone_number: str) -> List[Dict[str, Any]]:
        """Get consent records for a specific user."""
        user_consents = []
        for consent_id, record in self.consent_records.items():
            if record["phone_number"] == phone_number:
                user_consents.append(record)
        return sorted(user_consents, key=lambda x: x["granted_at"], reverse=True)
    
    def cleanup_expired_consents(self) -> int:
        """Remove expired consent records."""
        expired_count = 0
        current_time = datetime.utcnow()
        
        consent_ids_to_remove = []
        for consent_id, record in self.consent_records.items():
            try:
                expires_at = datetime.fromisoformat(record["expires_at"])
                if expires_at < current_time:
                    consent_ids_to_remove.append(consent_id)
            except ValueError:
                # Invalid date format, mark for removal
                consent_ids_to_remove.append(consent_id)
        
        for consent_id in consent_ids_to_remove:
            del self.consent_records[consent_id]
            expired_count += 1
        
        if expired_count > 0:
            self._save_data()
            logger.info(f"Cleaned up {expired_count} expired consent records")
        
        return expired_count


# Global filter instance
privacy_filter = PrivacyFilter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the service."""
    logger.info("Privacy Filter Service starting up...")
    
    # Cleanup expired consents on startup
    expired_count = privacy_filter.cleanup_expired_consents()
    if expired_count > 0:
        logger.info(f"Cleaned up {expired_count} expired consent records on startup")
    
    yield
    logger.info("Privacy Filter Service shutting down...")
    
    # Save all data on shutdown
    privacy_filter._save_data()


# Create FastAPI app
app = FastAPI(
    title="EVY Privacy Filter Service",
    description="Privacy filtering and data sanitization for EVY system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Health check endpoint."""
    stats = privacy_filter.get_statistics()
    return ServiceHealth(
        service_name="privacy-filter",
        status="healthy",
        version="1.0.0",
        details=stats
    )


@app.post("/validate")
async def validate_message(message: SMSMessage):
    """Validate and sanitize a message."""
    try:
        result = privacy_filter.validate_message(message)
        return result
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sanitize")
async def sanitize_text(text: str, redact: bool = True):
    """Sanitize text content."""
    try:
        result = privacy_filter.sanitize_text(text, redact)
        return result
    except Exception as e:
        logger.error(f"Sanitization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rate-limit/{phone_number}")
async def check_rate_limit(phone_number: str):
    """Check rate limit for a phone number."""
    try:
        result = privacy_filter.check_rate_limit(phone_number)
        return result
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get comprehensive statistics."""
    return privacy_filter.get_statistics()


@app.get("/audit-log")
async def get_audit_log(limit: int = 100):
    """Get recent audit log entries."""
    try:
        entries = privacy_filter.get_audit_log(limit)
        return {"entries": entries, "total": len(privacy_filter.audit_log)}
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consent/manage")
async def manage_consent(
    phone_number: str,
    data_categories: List[str],
    consent_status: ConsentStatus,
    expiry_days: int = 365
):
    """Manage user consent for data processing."""
    try:
        result = privacy_filter.manage_consent(
            phone_number=phone_number,
            data_categories=data_categories,
            consent_status=consent_status,
            expiry_days=expiry_days
        )
        return result
    except Exception as e:
        logger.error(f"Failed to manage consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consent/{phone_number}")
async def check_user_consent(phone_number: str, data_categories: List[str]):
    """Check user consent for specific data categories."""
    try:
        result = privacy_filter.check_consent(phone_number, data_categories)
        return result
    except Exception as e:
        logger.error(f"Failed to check consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consent/records/{phone_number}")
async def get_user_consent_records(phone_number: str):
    """Get all consent records for a user."""
    try:
        records = privacy_filter.get_user_consent_records(phone_number)
        return {"phone_number": phone_number, "consent_records": records}
    except Exception as e:
        logger.error(f"Failed to get user consent records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/block/{phone_number}")
async def block_user(phone_number: str, reason: str = "Policy violation"):
    """Block a user from using the service."""
    try:
        success = privacy_filter.block_user(phone_number, reason)
        if success:
            return {"status": "blocked", "phone_number": phone_number, "reason": reason}
        else:
            raise HTTPException(status_code=500, detail="Failed to block user")
    except Exception as e:
        logger.error(f"Failed to block user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/block/{phone_number}")
async def unblock_user(phone_number: str, reason: str = "Appeal approved"):
    """Unblock a user."""
    try:
        success = privacy_filter.unblock_user(phone_number, reason)
        if success:
            return {"status": "unblocked", "phone_number": phone_number, "reason": reason}
        else:
            return {"status": "not_found", "phone_number": phone_number}
    except Exception as e:
        logger.error(f"Failed to unblock user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/blocklist")
async def get_blocklist():
    """Get current blocklist."""
    try:
        return {
            "blocked_users": list(privacy_filter.blocked_users),
            "blocked_patterns": list(privacy_filter.blocked_patterns),
            "count": {
                "users": len(privacy_filter.blocked_users),
                "patterns": len(privacy_filter.blocked_patterns)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get blocklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cleanup/consents")
async def cleanup_expired_consents():
    """Cleanup expired consent records."""
    try:
        expired_count = privacy_filter.cleanup_expired_consents()
        return {"status": "cleaned", "expired_count": expired_count}
    except Exception as e:
        logger.error(f"Failed to cleanup consents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/sanitize")
async def test_sanitization(text: str, redact: bool = True):
    """Test text sanitization with detailed results."""
    try:
        result = privacy_filter.sanitize_text(text, redact)
        return result
    except Exception as e:
        logger.error(f"Failed to test sanitization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.privacy_filter_port,
        log_level="info"
    )


