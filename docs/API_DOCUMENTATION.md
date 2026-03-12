# EVY API Documentation
## Complete API Reference for Edge Services

### Document Purpose
This document provides complete API documentation for all EVY services, including endpoints, request/response formats, error handling, and examples.

**Base URL**: `http://localhost:8000`
**API Version**: v1
**Last Updated**: [Date]

---

## 📋 **Table of Contents**

1. [Authentication](#authentication)
2. [SMS Gateway API](#sms-gateway-api)
3. [Message Router API](#message-router-api)
4. [LLM Service API](#llm-service-api)
5. [RAG Service API](#rag-service-api)
6. [Emergency Service API](#emergency-service-api)
7. [Compression API](#compression-api)
8. [Mesh Network API](#mesh-network-api)
9. [Monitoring API](#monitoring-api)
10. [Error Handling](#error-handling)

---

## 🔐 **Authentication**

### **API Key Authentication**

```http
GET /api/v1/health
Authorization: Bearer YOUR_API_KEY
```

**Note**: Currently, authentication is optional for edge deployment. Will be required in production.

---

## 📱 **SMS Gateway API**

### **Send SMS**

```http
POST /api/v1/sms/send
Content-Type: application/json

{
    "phone_number": "+1234567890",
    "content": "Hello, this is a test message",
    "priority": "normal"
}
```

**Response:**
```json
{
    "success": true,
    "message_id": "msg-123456",
    "timestamp": 1234567890
}
```

### **Receive SMS**

```http
GET /api/v1/sms/receive
```

**Response:**
```json
{
    "messages": [
        {
            "phone_number": "+1234567890",
            "content": "User message",
            "timestamp": 1234567890,
            "id": "msg-123456"
        }
    ]
}
```

### **SMS Statistics**

```http
GET /api/v1/sms/stats
```

**Response:**
```json
{
    "messages_sent": 100,
    "messages_received": 95,
    "messages_failed": 5,
    "average_latency_ms": 45,
    "success_rate": 0.95
}
```

---

## 🧭 **Message Router API**

### **Route Message**

```http
POST /api/v1/router/route
Content-Type: application/json

{
    "message": "What should I do during a hurricane?",
    "phone_number": "+1234567890"
}
```

**Response:**
```json
{
    "route": {
        "service": "local_llm",
        "priority": "normal",
        "estimated_latency_ms": 5000,
        "resource_cost": {
            "memory_mb": 200,
            "cpu_percent": 50.0,
            "power_w": 3.0
        }
    }
}
```

### **Classify Intent**

```http
POST /api/v1/router/classify
Content-Type: application/json

{
    "message": "Emergency! Help!"
}
```

**Response:**
```json
{
    "intent": {
        "category": "emergency",
        "confidence": 1.0,
        "keywords": ["emergency", "help"]
    }
}
```

---

## 🤖 **LLM Service API**

### **Generate Response**

```http
POST /api/v1/llm/generate
Content-Type: application/json

{
    "prompt": "What is the capital of France?",
    "max_tokens": 50,
    "temperature": 0.7
}
```

**Response:**
```json
{
    "response": "The capital of France is Paris.",
    "tokens_used": 8,
    "processing_time_ms": 8500,
    "model_used": "tinyllama-4bit"
}
```

### **LLM Statistics**

```http
GET /api/v1/llm/stats
```

**Response:**
```json
{
    "total_requests": 1000,
    "successful_requests": 950,
    "failed_requests": 50,
    "average_response_time_ms": 8500,
    "total_tokens_generated": 50000,
    "current_model": "tinyllama-4bit"
}
```

---

## 📚 **RAG Service API**

### **Search Knowledge Base**

```http
POST /api/v1/rag/search
Content-Type: application/json

{
    "query": "emergency procedures",
    "top_k": 3
}
```

**Response:**
```json
{
    "results": [
        {
            "content": "Emergency procedures for hurricanes...",
            "score": 0.95,
            "source": "emergency_procedures"
        }
    ],
    "search_time_ms": 450
}
```

---

## 🚨 **Emergency Service API**

### **Handle Emergency**

```http
POST /api/v1/emergency/handle
Content-Type: application/json

{
    "message": "Hurricane warning!",
    "phone_number": "+1234567890"
}
```

**Response:**
```json
{
    "is_emergency": true,
    "response": "URGENT: Hurricane warning. Evacuate now to shelters. Bring: water, food, meds, docs. Contact: 911.",
    "priority": "emergency",
    "response_time_ms": 120
}
```

---

## 🗜️ **Compression API**

### **Compress Text**

```http
POST /api/v1/compression/compress
Content-Type: application/json

{
    "text": "Long message that needs compression...",
    "target_length": 160
}
```

**Response:**
```json
{
    "compressed": "Compressed message...",
    "original_length": 250,
    "compressed_length": 158,
    "compression_ratio": 0.37,
    "compression_time_ms": 850
}
```

---

## 📡 **Mesh Network API**

### **Send Mesh Message**

```http
POST /api/v1/mesh/send
Content-Type: application/json

{
    "destination_node": "node-002",
    "content": "Message content",
    "priority": "normal"
}
```

**Response:**
```json
{
    "success": true,
    "message_id": "mesh-123456",
    "hop_count": 2,
    "transmission_time_ms": 2500
}
```

---

## 📊 **Monitoring API**

### **Health Check**

```http
GET /api/v1/health
```

**Response:**
```json
{
    "status": "healthy",
    "services": {
        "sms_gateway": "healthy",
        "message_router": "healthy",
        "llm_service": "healthy",
        "rag_service": "healthy"
    },
    "resources": {
        "memory_usage_percent": 75.5,
        "cpu_usage_percent": 45.2,
        "battery_level": 0.85,
        "power_consumption_w": 11.5
    }
}
```

### **Resource Status**

```http
GET /api/v1/monitoring/resources
```

**Response:**
```json
{
    "memory": {
        "total_mb": 8192,
        "available_mb": 2048,
        "used_mb": 6144,
        "percent": 75.0
    },
    "cpu": {
        "usage_percent": 45.2,
        "cores": 4
    },
    "power": {
        "battery_level": 0.85,
        "power_consumption_w": 11.5,
        "solar_charging": true
    },
    "storage": {
        "total_gb": 128,
        "used_gb": 18,
        "available_gb": 110,
        "percent": 14.0
    }
}
```

---

## ⚠️ **Error Handling**

### **Error Response Format**

```json
{
    "error": {
        "code": "LOW_MEMORY",
        "message": "Insufficient memory available",
        "details": {
            "available_mb": 50,
            "required_mb": 200
        }
    }
}
```

### **Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `LOW_MEMORY` | 503 | Insufficient memory |
| `LOW_BATTERY` | 503 | Battery level too low |
| `SERVICE_UNAVAILABLE` | 503 | Service not available |
| `INVALID_REQUEST` | 400 | Invalid request format |
| `MESSAGE_TOO_LONG` | 400 | Message exceeds limit |
| `RATE_LIMITED` | 429 | Rate limit exceeded |

---

**END OF API DOCUMENTATION**

---

*This document provides complete API reference. Use for integration and development.*

