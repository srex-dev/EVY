# Emergency Response Service

## Overview

The Emergency Response Service provides fast, resource-aware emergency detection and response capabilities for EVY edge nodes.

## Features

- **Fast Detection**: Pattern-based emergency detection (<10ms)
- **Pre-loaded Templates**: In-memory templates for instant response (<1MB memory)
- **Resource-Aware**: Battery-aware compression (skip if battery <20%)
- **Disaster Protocols**: Specific protocols for tornado, hurricane, earthquake, flood
- **Emergency Contacts**: Pre-loaded emergency contact database
- **Priority Routing**: Automatic emergency priority handling

## Architecture

```
EmergencyResponseService
├── EmergencyDetector (pattern matching)
├── EmergencyTemplates (pre-loaded)
├── EmergencyContactsDB (in-memory)
└── RustCompressionService (resource-aware)
```

## Emergency Types

### Medical Emergencies
- **Critical**: Heart attack, stroke, chest pain, choking, unconscious
- **High**: Medical, hospital, ambulance, injured
- **Response**: Immediate 911 call instructions, first aid guidance

### Fire Emergencies
- **Critical**: Fire, burning, smoke, flames
- **High**: Fire alarm, smoke alarm, evacuation
- **Response**: Evacuation instructions, 911 call

### Police Emergencies
- **Critical**: Help, danger, threat, weapon, attack
- **High**: Police, 911, emergency, urgent
- **Response**: Safety instructions, 911 call

### Natural Disasters
- **Types**: Tornado, hurricane, earthquake, flood
- **Response**: Disaster-specific safety protocols

## Usage

### Basic Emergency Detection

```python
from backend.services.emergency_response.service import EmergencyResponseService
from backend.shared.models import SMSMessage, MessagePriority
from datetime import datetime

service = EmergencyResponseService()

# Check if message is emergency
is_emergency = service.is_emergency("EMERGENCY! Help needed!")
is_critical = service.is_critical_emergency("Heart attack!")

# Handle emergency message
message = SMSMessage(
    sender="+1234567890",
    receiver="+0987654321",
    content="My dad is having chest pain!",
    priority=MessagePriority.EMERGENCY,
    timestamp=datetime.utcnow()
)

result = await service.handle_emergency(message)
if result:
    print(f"Emergency Type: {result['emergency_type']}")
    print(f"Response: {result['response_text']}")
    print(f"Response Time: {result['response_time_ms']}ms")
```

### Resource-Aware Processing

```python
# Update resource levels
service.update_resources(battery_level=15, memory_mb=200)

# Low battery: uses truncation instead of compression
result = await service.handle_emergency(message)
```

### Local Emergency Contacts

```python
# Add local emergency contact
service.add_local_contact('local_police', '555-1234')
service.add_local_contact('local_fire', '555-5678')

# Contacts are automatically included in responses
```

## Performance Targets

- **Detection Time**: <10ms (pattern matching)
- **Response Time**: <5s (including compression and sending)
- **Template Lookup**: <10ms (in-memory)
- **Memory Usage**: <1MB (pre-loaded templates)

## Edge Optimizations

1. **Pre-loaded Templates**: All templates in memory (no database queries)
2. **Pattern Matching**: Fast regex patterns (no ML model)
3. **Resource-Aware**: Skip compression if battery <20%
4. **Direct Lookup**: O(1) template access
5. **No Network Calls**: All processing local

## Emergency Templates

Templates are pre-loaded and include:

- **Medical**: Critical, high, general severity levels
- **Fire**: Critical, high, general severity levels
- **Police**: Critical, high, general severity levels
- **Natural Disasters**: Tornado, hurricane, earthquake, flood protocols
- **General**: Default emergency response

## Emergency Contacts

Pre-loaded contacts:
- 911 (all emergencies)
- Poison Control: 1-800-222-1222
- Suicide Prevention: 988
- Disaster Relief: 1-800-RED-CROSS
- FEMA: 1-800-621-FEMA

Local contacts can be added via `add_local_contact()`.

## Integration

The Emergency Response Service integrates with:

1. **Message Router**: Automatic emergency detection and routing
2. **SMS Gateway**: Priority sending for emergency messages
3. **Compression Engine**: Resource-aware compression
4. **Service Discovery**: Health monitoring

## Testing

```bash
# Run emergency response tests
pytest backend/tests/test_emergency_response.py -v
```

## Configuration

```python
config = {
    'compression': {
        'target_length': 160,
        'battery_threshold': 20,  # Lower for emergencies
    }
}

service = EmergencyResponseService(config)
```

## Statistics

The service tracks:
- Total emergencies handled
- Critical emergencies
- Emergency types (medical, fire, police, natural disaster)
- Average response time
- Resource levels

```python
stats = service.get_statistics()
print(f"Total emergencies: {stats['total_emergencies']}")
print(f"Average response time: {stats['average_response_time_ms']}ms")
```

## Troubleshooting

### High Response Time

If response time is high:
1. Check resource levels (battery, memory)
2. Verify compression service is available
3. Check for network delays (should be minimal)

### Templates Not Loading

If templates fail to load:
1. Check memory availability
2. Verify template file structure
3. Check logs for errors

### Detection Not Working

If emergency detection fails:
1. Check message content (may not contain emergency keywords)
2. Verify detector patterns are correct
3. Check confidence threshold

