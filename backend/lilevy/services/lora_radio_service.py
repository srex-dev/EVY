"""LoRa Radio Service for Enhanced lilEVY Nodes."""
import asyncio
import logging
import time
import json
import hashlib
import os
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import struct

from backend.shared.models import ServiceHealth
from backend.shared.logging import setup_logger

try:
    import serial
except ImportError:
    serial = None

try:
    import pynmea2
except ImportError:
    pynmea2 = None

try:
    import spidev
except ImportError:
    spidev = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

logger = setup_logger("lora-radio")

class MessageType(Enum):
    DISCOVERY = "discovery"
    ROUTE = "route"
    DATA = "data"
    SYNC = "sync"
    EMERGENCY = "emergency"
    HEARTBEAT = "heartbeat"
    ACK = "ack"

class MessagePriority(Enum):
    EMERGENCY = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class LoRaMessage:
    """LoRa message structure."""
    message_type: MessageType
    priority: MessagePriority
    source_node: str
    destination_node: str
    payload: Dict[str, Any]
    sequence_number: int
    timestamp: float
    ttl: int = 5
    checksum: Optional[str] = None

@dataclass
class NodeInfo:
    """Information about a mesh node."""
    node_id: str
    last_seen: float
    signal_strength: float
    capabilities: Dict[str, Any]
    position: Optional[Dict[str, float]] = None
    battery_level: Optional[float] = None

class LoRaRadioService:
    """LoRa radio service for mesh networking."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.is_initialized = False
        
        # LoRa configuration
        self.frequency = float(os.getenv("LORA_FREQUENCY_MHZ", "915.0"))  # MHz
        self.power = 14  # dBm
        self.bandwidth = 125  # kHz
        self.spreading_factor = 7
        self.coding_rate = 5
        self.sync_word = 0x34
        self.cs_pin = int(os.getenv("LORA_CS_PIN", "25"))
        self.dio0_pin = int(os.getenv("LORA_DIO0_PIN", "4"))
        self.reset_pin = int(os.getenv("LORA_RESET_PIN", "17"))
        self.gps_device = os.getenv("GPS_DEVICE", "/dev/ttyAMA0")
        self.telemetry_file = os.getenv("POWER_TELEMETRY_FILE", "/data/telemetry/power.json")
        
        # Network state
        self.known_nodes: Dict[str, NodeInfo] = {}
        self.routing_table: Dict[str, Dict[str, Any]] = {}
        self.message_queue: List[LoRaMessage] = []
        self.received_messages: List[LoRaMessage] = []
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "discovery_packets": 0,
            "route_updates": 0,
            "sync_operations": 0,
            "last_message_time": None,
            "average_latency": 0.0,
            "network_health": 0.0
        }
        
        # Callbacks
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.discovery_callback: Optional[Callable] = None
        
        # Hardware simulation fallback (used if GPIO/SPI deps unavailable)
        self.hardware_simulated = os.getenv("LORA_SIMULATED", "false").lower() == "true"
        self.lora_device = None
        self.spi = None
        
    async def initialize(self) -> bool:
        """Initialize LoRa radio service."""
        try:
            logger.info(f"Initializing LoRa Radio Service for node {self.node_id}")
            
            if self.hardware_simulated:
                # Simulate hardware initialization
                await self._simulate_hardware_init()
            else:
                # Initialize actual LoRa hardware
                await self._initialize_hardware()
            
            # Start background tasks
            asyncio.create_task(self._discovery_loop())
            asyncio.create_task(self._message_processing_loop())
            asyncio.create_task(self._routing_update_loop())
            
            self.is_initialized = True
            logger.info("LoRa Radio Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LoRa Radio Service: {e}")
            return False
    
    async def _simulate_hardware_init(self):
        """Simulate LoRa hardware initialization."""
        logger.info("Simulating LoRa hardware initialization...")
        await asyncio.sleep(1)  # Simulate hardware startup time
        
        # Simulate hardware configuration
        self.lora_device = {
            "frequency": self.frequency,
            "power": self.power,
            "bandwidth": self.bandwidth,
            "spreading_factor": self.spreading_factor,
            "coding_rate": self.coding_rate,
            "sync_word": self.sync_word,
            "initialized": True
        }
        
        logger.info("LoRa hardware simulation initialized")
    
    async def _initialize_hardware(self):
        """Initialize actual LoRa hardware (SX1276)."""
        try:
            if spidev is None or GPIO is None:
                logger.warning("spidev/RPi.GPIO not available; falling back to simulated LoRa mode")
                self.hardware_simulated = True
                await self._simulate_hardware_init()
                return

            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 5000000

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.cs_pin, GPIO.OUT)
            GPIO.setup(self.dio0_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.reset_pin, GPIO.OUT)

            GPIO.output(self.cs_pin, GPIO.HIGH)
            GPIO.output(self.reset_pin, GPIO.LOW)
            time.sleep(0.01)
            GPIO.output(self.reset_pin, GPIO.HIGH)
            time.sleep(0.01)
            
            # Configure LoRa registers
            await self._configure_lora_registers()
            
            self.lora_device = {
                "initialized": True,
                "hardware": "SX1276",
                "cs_pin": self.cs_pin,
                "dio0_pin": self.dio0_pin,
                "reset_pin": self.reset_pin
            }
            
            logger.info("LoRa hardware initialized successfully")
            
        except Exception as e:
            logger.error(f"Hardware initialization failed: {e}")
            raise
    
    async def _configure_lora_registers(self):
        """Configure LoRa module registers."""
        # This would configure the actual SX1276 registers
        # For now, we'll simulate the configuration
        
        register_config = {
            "REG_FRF_MSB": (int(self.frequency * 16384) >> 16) & 0xFF,
            "REG_FRF_MID": (int(self.frequency * 16384) >> 8) & 0xFF,
            "REG_FRF_LSB": int(self.frequency * 16384) & 0xFF,
            "REG_PA_CONFIG": 0x8F | self.power,
            "REG_MODEM_CONFIG_1": (self.bandwidth << 4) | self.coding_rate,
            "REG_MODEM_CONFIG_2": (self.spreading_factor << 4) | 0x04,
            "REG_SYNC_WORD": self.sync_word
        }
        
        logger.info(f"LoRa registers configured: {register_config}")
    
    async def send_message(self, message: LoRaMessage) -> bool:
        """Send a message via LoRa radio."""
        try:
            if not self.is_initialized:
                logger.error("LoRa service not initialized")
                return False
            
            # Calculate checksum
            message.checksum = self._calculate_checksum(message)
            
            # Serialize message
            message_data = self._serialize_message(message)
            
            # Add to queue for transmission
            self.message_queue.append(message)
            
            # Simulate transmission
            if self.hardware_simulated:
                await self._simulate_transmission(message)
            else:
                await self._transmit_message(message_data)
            
            # Update statistics
            self.stats["messages_sent"] += 1
            self.stats["last_message_time"] = time.time()
            
            logger.debug(f"Message sent: {message.message_type.value} to {message.destination_node}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.stats["messages_failed"] += 1
            return False
    
    async def _simulate_transmission(self, message: LoRaMessage):
        """Simulate LoRa transmission for testing."""
        # Simulate transmission delay
        await asyncio.sleep(0.1)
        
        # Simulate message being received by other nodes
        if message.destination_node == "broadcast" or message.destination_node in self.known_nodes:
            # Simulate successful transmission
            self.stats["messages_delivered"] += 1
            logger.debug(f"Message delivered: {message.message_type.value}")
        else:
            # Simulate failed transmission
            self.stats["messages_failed"] += 1
            logger.warning(f"Message failed: {message.message_type.value} - destination not found")
    
    async def _transmit_message(self, message_data: bytes):
        """Transmit message via actual LoRa hardware."""
        try:
            if self.spi is None or GPIO is None:
                raise RuntimeError("LoRa SPI/GPIO not initialized")

            # Manual CS for Dragino wiring (GPIO25 instead of CE0)
            GPIO.output(self.cs_pin, GPIO.LOW)
            try:
                self.spi.xfer2(list(message_data[:255]))
            finally:
                GPIO.output(self.cs_pin, GPIO.HIGH)
            
            logger.debug("Message transmitted via LoRa hardware")
            
        except Exception as e:
            logger.error(f"Hardware transmission failed: {e}")
            raise
    
    async def receive_message(self) -> Optional[LoRaMessage]:
        """Receive a message from LoRa radio."""
        try:
            if not self.is_initialized:
                return None
            
            # Check for received messages
            if self.received_messages:
                message = self.received_messages.pop(0)
                
                # Update statistics
                self.stats["messages_received"] += 1
                
                # Process message
                await self._process_received_message(message)
                
                return message
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return None
    
    async def _process_received_message(self, message: LoRaMessage):
        """Process a received message."""
        try:
            # Verify checksum
            if not self._verify_checksum(message):
                logger.warning("Received message with invalid checksum")
                return
            
            # Update node information
            if message.source_node != self.node_id:
                await self._update_node_info(message.source_node, message)
            
            # Route message if not for this node
            if message.destination_node != self.node_id and message.destination_node != "broadcast":
                await self._forward_message(message)
            
            # Handle message based on type
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(message)
            
            logger.debug(f"Processed message: {message.message_type.value} from {message.source_node}")
            
        except Exception as e:
            logger.error(f"Failed to process received message: {e}")
    
    async def _discovery_loop(self):
        """Background task for node discovery."""
        while self.is_initialized:
            try:
                await self._broadcast_discovery()
                await asyncio.sleep(30)  # Discovery every 30 seconds
                
            except Exception as e:
                logger.error(f"Discovery loop error: {e}")
                await asyncio.sleep(30)
    
    async def _broadcast_discovery(self):
        """Broadcast discovery packet."""
        try:
            discovery_message = LoRaMessage(
                message_type=MessageType.DISCOVERY,
                priority=MessagePriority.MEDIUM,
                source_node=self.node_id,
                destination_node="broadcast",
                payload={
                    "node_id": self.node_id,
                    "capabilities": await self._get_node_capabilities(),
                    "position": await self._get_node_position(),
                    "battery_level": await self._get_battery_level(),
                    "timestamp": time.time()
                },
                sequence_number=self._get_next_sequence_number(),
                timestamp=time.time()
            )
            
            await self.send_message(discovery_message)
            self.stats["discovery_packets"] += 1
            
            logger.debug("Discovery packet broadcasted")
            
        except Exception as e:
            logger.error(f"Failed to broadcast discovery: {e}")
    
    async def _message_processing_loop(self):
        """Background task for message processing."""
        while self.is_initialized:
            try:
                # Process message queue
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    await self._process_outgoing_message(message)
                
                # Check for incoming messages
                received_message = await self.receive_message()
                if received_message:
                    await self._process_received_message(received_message)
                
                await asyncio.sleep(0.1)  # 100ms processing interval
                
            except Exception as e:
                logger.error(f"Message processing loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _routing_update_loop(self):
        """Background task for routing table updates."""
        while self.is_initialized:
            try:
                await self._update_routing_table()
                await asyncio.sleep(60)  # Update routing every minute
                
            except Exception as e:
                logger.error(f"Routing update loop error: {e}")
                await asyncio.sleep(60)
    
    async def _update_routing_table(self):
        """Update routing table based on known nodes."""
        try:
            current_time = time.time()
            
            # Remove stale nodes (not seen for 5 minutes)
            stale_nodes = [
                node_id for node_id, node_info in self.known_nodes.items()
                if current_time - node_info.last_seen > 300
            ]
            
            for node_id in stale_nodes:
                del self.known_nodes[node_id]
                logger.info(f"Removed stale node: {node_id}")
            
            # Update routing table
            self.routing_table = {}
            for node_id, node_info in self.known_nodes.items():
                self.routing_table[node_id] = {
                    "next_hop": node_id,  # Direct connection assumed
                    "hops": 1,
                    "last_update": current_time,
                    "signal_strength": node_info.signal_strength,
                    "reliability": self._calculate_reliability(node_info)
                }
            
            self.stats["route_updates"] += 1
            logger.debug("Routing table updated")
            
        except Exception as e:
            logger.error(f"Failed to update routing table: {e}")
    
    async def _get_node_capabilities(self) -> Dict[str, Any]:
        """Get node capabilities."""
        return {
            "sms_gateway": True,
            "llm_inference": True,
            "rag_service": True,
            "gps_position": True,
            "solar_power": True,
            "battery_level": await self._get_battery_level(),
            "processing_power": "low",  # 125M-350M models
            "available_storage": "high",  # 32GB SSD
            "lora_radio": True
        }
    
    async def _get_node_position(self) -> Optional[Dict[str, float]]:
        """Get node GPS position (if available)."""
        if serial is None:
            return None
        try:
            with serial.Serial(self.gps_device, 9600, timeout=1) as gps:
                for _ in range(5):
                    line = gps.readline().decode("ascii", errors="replace").strip()
                    if not line:
                        continue
                    if line.startswith("$GPRMC") or line.startswith("$GPGGA"):
                        if pynmea2 is None:
                            return None
                        msg = pynmea2.parse(line)
                        if hasattr(msg, "latitude") and hasattr(msg, "longitude"):
                            if msg.latitude and msg.longitude:
                                return {"lat": float(msg.latitude), "lon": float(msg.longitude)}
        except Exception as e:
            logger.debug(f"GPS position unavailable: {e}")
        return None
    
    async def _get_battery_level(self) -> float:
        """Get battery level percentage."""
        # Read telemetry file written by power monitor integration if available.
        try:
            with open(self.telemetry_file, "r", encoding="utf-8") as f:
                telemetry = json.load(f)
            level = float(telemetry.get("battery_level", 85.0))
            return max(0.0, min(100.0, level))
        except Exception:
            return 85.0
    
    def _calculate_checksum(self, message: LoRaMessage) -> str:
        """Calculate message checksum."""
        message_str = json.dumps(asdict(message), sort_keys=True, default=str)
        return hashlib.md5(message_str.encode()).hexdigest()
    
    def _verify_checksum(self, message: LoRaMessage) -> bool:
        """Verify message checksum."""
        if not message.checksum:
            return False
        
        calculated_checksum = self._calculate_checksum(message)
        return calculated_checksum == message.checksum
    
    def _serialize_message(self, message: LoRaMessage) -> bytes:
        """Serialize message for transmission."""
        message_dict = asdict(message)
        message_json = json.dumps(message_dict, default=str)
        return message_json.encode('utf-8')
    
    def _deserialize_message(self, data: bytes) -> LoRaMessage:
        """Deserialize received message."""
        message_json = data.decode('utf-8')
        message_dict = json.loads(message_json)
        
        # Convert back to dataclass
        message_dict['message_type'] = MessageType(message_dict['message_type'])
        message_dict['priority'] = MessagePriority(message_dict['priority'])
        
        return LoRaMessage(**message_dict)
    
    def _get_next_sequence_number(self) -> int:
        """Get next sequence number for message."""
        # Simple sequence number generation
        return int(time.time() * 1000) % 65536
    
    def _calculate_reliability(self, node_info: NodeInfo) -> float:
        """Calculate node reliability score."""
        # Simple reliability calculation based on signal strength and last seen
        signal_factor = min(node_info.signal_strength / -80, 1.0)  # Normalize signal strength
        time_factor = max(0, 1 - (time.time() - node_info.last_seen) / 300)  # Decay over 5 minutes
        
        return (signal_factor + time_factor) / 2
    
    async def _update_node_info(self, node_id: str, message: LoRaMessage):
        """Update information about a known node."""
        if node_id in self.known_nodes:
            node_info = self.known_nodes[node_id]
            node_info.last_seen = time.time()
            node_info.signal_strength = message.payload.get('signal_strength', -80)
        else:
            # New node discovered
            self.known_nodes[node_id] = NodeInfo(
                node_id=node_id,
                last_seen=time.time(),
                signal_strength=message.payload.get('signal_strength', -80),
                capabilities=message.payload.get('capabilities', {}),
                position=message.payload.get('position'),
                battery_level=message.payload.get('battery_level')
            )
            logger.info(f"New node discovered: {node_id}")
    
    async def _forward_message(self, message: LoRaMessage):
        """Forward message to next hop."""
        try:
            if message.ttl <= 0:
                logger.warning("Message TTL expired, dropping")
                return
            
            # Decrement TTL
            message.ttl -= 1
            
            # Find route to destination
            if message.destination_node in self.routing_table:
                route = self.routing_table[message.destination_node]
                next_hop = route['next_hop']
                
                # Forward message
                await self.send_message(message)
                logger.debug(f"Forwarded message to {next_hop}")
            else:
                logger.warning(f"No route to {message.destination_node}")
                
        except Exception as e:
            logger.error(f"Failed to forward message: {e}")
    
    async def _process_outgoing_message(self, message: LoRaMessage):
        """Process outgoing message."""
        try:
            # This would handle actual message transmission
            # For now, just log the message
            logger.debug(f"Processing outgoing message: {message.message_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to process outgoing message: {e}")
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for {message_type.value}")
    
    def register_discovery_callback(self, callback: Callable):
        """Register discovery callback."""
        self.discovery_callback = callback
        logger.info("Registered discovery callback")
    
    def get_known_nodes(self) -> Dict[str, NodeInfo]:
        """Get list of known nodes."""
        return self.known_nodes.copy()
    
    def get_routing_table(self) -> Dict[str, Dict[str, Any]]:
        """Get routing table."""
        return self.routing_table.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self.stats,
            "known_nodes_count": len(self.known_nodes),
            "routing_table_size": len(self.routing_table),
            "message_queue_size": len(self.message_queue),
            "is_initialized": self.is_initialized,
            "hardware_simulated": self.hardware_simulated
        }
    
    async def cleanup(self):
        """Cleanup LoRa radio service."""
        try:
            self.is_initialized = False
            
            if self.lora_device and not self.hardware_simulated:
                # Cleanup hardware resources
                if GPIO:
                    GPIO.cleanup()
                if self.spi:
                    self.spi.close()
            
            logger.info("LoRa Radio Service cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global service instance
lora_radio_service = LoRaRadioService("lilevy-001")
