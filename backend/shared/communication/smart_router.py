"""Smart Communication Router for Enhanced EVY Nodes."""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from backend.shared.models import LLMRequest, LLMResponse, RAGQuery, RAGResult, SMSMessage
from backend.shared.logging import setup_logger

logger = setup_logger("smart-router")

class CommunicationLayer(Enum):
    SMS = "sms"
    LORA = "lora"
    INTERNET = "internet"
    BLUETOOTH = "bluetooth"

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EMERGENCY = "emergency"

class QueryType(Enum):
    LLM_REQUEST = "llm_request"
    RAG_QUERY = "rag_query"
    KNOWLEDGE_SYNC = "knowledge_sync"
    SYSTEM_STATUS = "system_status"
    EMERGENCY_ALERT = "emergency_alert"

@dataclass
class RoutingDecision:
    """Routing decision for a query."""
    layer: CommunicationLayer
    target_node: Optional[str]
    priority: int
    estimated_latency: float
    estimated_reliability: float
    fallback_layers: List[CommunicationLayer]
    reason: str

@dataclass
class QueryContext:
    """Context information for routing decisions."""
    query_type: QueryType
    complexity: QueryComplexity
    priority: int
    user_location: Optional[Dict[str, float]]
    source_node: str
    timestamp: float
    size_estimate: int
    requires_response: bool
    emergency_level: int = 0

class SmartCommunicationRouter:
    """Intelligent router for multi-layer communication."""
    
    def __init__(self, local_node_id: str):
        self.local_node_id = local_node_id
        self.is_initialized = False
        
        # Communication layers
        self.communication_layers: Dict[CommunicationLayer, Any] = {}
        self.layer_status: Dict[CommunicationLayer, bool] = {}
        self.layer_capabilities: Dict[CommunicationLayer, Dict[str, Any]] = {}
        
        # Routing policies
        self.routing_policies: Dict[QueryType, Dict[str, Any]] = {}
        self.priority_weights = {
            QueryComplexity.EMERGENCY: 0,
            QueryComplexity.COMPLEX: 1,
            QueryComplexity.MEDIUM: 2,
            QueryComplexity.SIMPLE: 3
        }
        
        # Performance tracking
        self.stats = {
            "total_queries": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "layer_usage": {layer.value: 0 for layer in CommunicationLayer},
            "average_latency": {layer.value: 0.0 for layer in CommunicationLayer},
            "reliability_scores": {layer.value: 0.0 for layer in CommunicationLayer},
            "last_routing_decision": None
        }
        
        # Network topology
        self.known_nodes: Dict[str, Dict[str, Any]] = {}
        self.node_capabilities: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> bool:
        """Initialize smart communication router."""
        try:
            logger.info(f"Initializing Smart Communication Router for node {self.local_node_id}")
            
            # Initialize communication layers
            await self._initialize_communication_layers()
            
            # Setup routing policies
            await self._setup_routing_policies()
            
            # Start monitoring tasks
            asyncio.create_task(self._layer_monitoring_loop())
            asyncio.create_task(self._performance_tracking_loop())
            
            self.is_initialized = True
            logger.info("Smart Communication Router initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Smart Communication Router: {e}")
            return False
    
    async def _initialize_communication_layers(self):
        """Initialize all available communication layers."""
        # SMS Layer (always available for lilEVY)
        self.communication_layers[CommunicationLayer.SMS] = {
            "name": "SMS Gateway",
            "available": True,
            "latency": 5.0,  # seconds
            "reliability": 0.95,
            "bandwidth": 160,  # characters
            "range": "unlimited",
            "power_consumption": "medium"
        }
        
        # LoRa Layer (if LoRa radio is available)
        try:
            from backend.lilevy.services.lora_radio_service import lora_radio_service
            if lora_radio_service.is_initialized:
                self.communication_layers[CommunicationLayer.LORA] = {
                    "name": "LoRa Radio",
                    "available": True,
                    "latency": 2.0,  # seconds
                    "reliability": 0.90,
                    "bandwidth": 50000,  # bits per second
                    "range": "10-15 miles",
                    "power_consumption": "low"
                }
            else:
                self.communication_layers[CommunicationLayer.LORA] = {
                    "name": "LoRa Radio",
                    "available": False,
                    "latency": float('inf'),
                    "reliability": 0.0,
                    "bandwidth": 0,
                    "range": "0 miles",
                    "power_consumption": "low"
                }
        except ImportError:
            self.communication_layers[CommunicationLayer.LORA] = {
                "name": "LoRa Radio",
                "available": False,
                "latency": float('inf'),
                "reliability": 0.0,
                "bandwidth": 0,
                "range": "0 miles",
                "power_consumption": "low"
            }
        
        # Internet Layer (if internet is available)
        self.communication_layers[CommunicationLayer.INTERNET] = {
            "name": "Internet",
            "available": await self._check_internet_availability(),
            "latency": 1.0,  # seconds
            "reliability": 0.98,
            "bandwidth": 1000000,  # bits per second
            "range": "unlimited",
            "power_consumption": "medium"
        }
        
        # Bluetooth Layer (if available)
        self.communication_layers[CommunicationLayer.BLUETOOTH] = {
            "name": "Bluetooth",
            "available": False,  # Would need Bluetooth module
            "latency": 0.5,  # seconds
            "reliability": 0.85,
            "bandwidth": 1000000,  # bits per second
            "range": "10 meters",
            "power_consumption": "low"
        }
        
        # Initialize layer status
        for layer, config in self.communication_layers.items():
            self.layer_status[layer] = config["available"]
            self.layer_capabilities[layer] = config
    
    async def _check_internet_availability(self) -> bool:
        """Check if internet connection is available."""
        try:
            # Simple internet connectivity check
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://httpbin.org/status/200", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _setup_routing_policies(self):
        """Setup routing policies for different query types."""
        self.routing_policies = {
            QueryType.LLM_REQUEST: {
                "preferred_layers": [CommunicationLayer.INTERNET, CommunicationLayer.LORA, CommunicationLayer.SMS],
                "fallback_strategy": "cascade",
                "timeout": 30,
                "retry_count": 3,
                "complexity_routing": {
                    QueryComplexity.SIMPLE: [CommunicationLayer.SMS, CommunicationLayer.LORA],
                    QueryComplexity.MEDIUM: [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                    QueryComplexity.COMPLEX: [CommunicationLayer.INTERNET, CommunicationLayer.LORA],
                    QueryComplexity.EMERGENCY: [CommunicationLayer.SMS, CommunicationLayer.LORA]
                }
            },
            QueryType.RAG_QUERY: {
                "preferred_layers": [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                "fallback_strategy": "cascade",
                "timeout": 15,
                "retry_count": 2,
                "complexity_routing": {
                    QueryComplexity.SIMPLE: [CommunicationLayer.LORA, CommunicationLayer.SMS],
                    QueryComplexity.MEDIUM: [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                    QueryComplexity.COMPLEX: [CommunicationLayer.INTERNET, CommunicationLayer.LORA],
                    QueryComplexity.EMERGENCY: [CommunicationLayer.SMS, CommunicationLayer.LORA]
                }
            },
            QueryType.KNOWLEDGE_SYNC: {
                "preferred_layers": [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                "fallback_strategy": "parallel",
                "timeout": 60,
                "retry_count": 5,
                "complexity_routing": {
                    QueryComplexity.SIMPLE: [CommunicationLayer.LORA],
                    QueryComplexity.MEDIUM: [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                    QueryComplexity.COMPLEX: [CommunicationLayer.INTERNET, CommunicationLayer.LORA],
                    QueryComplexity.EMERGENCY: [CommunicationLayer.LORA, CommunicationLayer.SMS]
                }
            },
            QueryType.SYSTEM_STATUS: {
                "preferred_layers": [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                "fallback_strategy": "cascade",
                "timeout": 10,
                "retry_count": 2,
                "complexity_routing": {
                    QueryComplexity.SIMPLE: [CommunicationLayer.LORA],
                    QueryComplexity.MEDIUM: [CommunicationLayer.LORA, CommunicationLayer.INTERNET],
                    QueryComplexity.COMPLEX: [CommunicationLayer.INTERNET],
                    QueryComplexity.EMERGENCY: [CommunicationLayer.LORA, CommunicationLayer.SMS]
                }
            },
            QueryType.EMERGENCY_ALERT: {
                "preferred_layers": [CommunicationLayer.SMS, CommunicationLayer.LORA],
                "fallback_strategy": "broadcast",
                "timeout": 5,
                "retry_count": 5,
                "complexity_routing": {
                    QueryComplexity.EMERGENCY: [CommunicationLayer.SMS, CommunicationLayer.LORA, CommunicationLayer.INTERNET]
                }
            }
        }
    
    async def route_query(self, query: Any, context: QueryContext) -> RoutingDecision:
        """Route a query through the optimal communication layer."""
        try:
            self.stats["total_queries"] += 1
            
            # Analyze query and context
            query_analysis = await self._analyze_query(query, context)
            
            # Get available layers
            available_layers = await self._get_available_layers()
            
            # Apply routing policies
            routing_decision = await self._apply_routing_policy(
                query_analysis, context, available_layers
            )
            
            # Update statistics
            self.stats["successful_routes"] += 1
            self.stats["layer_usage"][routing_decision.layer.value] += 1
            self.stats["last_routing_decision"] = {
                "layer": routing_decision.layer.value,
                "reason": routing_decision.reason,
                "timestamp": time.time()
            }
            
            logger.info(f"Routed query via {routing_decision.layer.value}: {routing_decision.reason}")
            return routing_decision
            
        except Exception as e:
            logger.error(f"Failed to route query: {e}")
            self.stats["failed_routes"] += 1
            
            # Return emergency fallback
            return RoutingDecision(
                layer=CommunicationLayer.SMS,
                target_node=None,
                priority=0,
                estimated_latency=5.0,
                estimated_reliability=0.95,
                fallback_layers=[CommunicationLayer.LORA],
                reason=f"Emergency fallback due to error: {str(e)}"
            )
    
    async def _analyze_query(self, query: Any, context: QueryContext) -> Dict[str, Any]:
        """Analyze query to determine routing requirements."""
        analysis = {
            "size": context.size_estimate,
            "complexity": context.complexity,
            "priority": context.priority,
            "requires_response": context.requires_response,
            "emergency_level": context.emergency_level,
            "bandwidth_requirements": 0,
            "latency_tolerance": 30.0,
            "reliability_requirements": 0.8
        }
        
        # Determine bandwidth requirements based on query type
        if isinstance(query, LLMRequest):
            analysis["bandwidth_requirements"] = len(query.prompt) * 8  # bits
            analysis["latency_tolerance"] = 30.0
            analysis["reliability_requirements"] = 0.9
        elif isinstance(query, RAGQuery):
            analysis["bandwidth_requirements"] = len(query.query) * 8  # bits
            analysis["latency_tolerance"] = 15.0
            analysis["reliability_requirements"] = 0.85
        elif isinstance(query, SMSMessage):
            analysis["bandwidth_requirements"] = len(query.content) * 8  # bits
            analysis["latency_tolerance"] = 10.0
            analysis["reliability_requirements"] = 0.95
        
        # Adjust based on complexity
        if context.complexity == QueryComplexity.EMERGENCY:
            analysis["latency_tolerance"] = 5.0
            analysis["reliability_requirements"] = 0.99
        elif context.complexity == QueryComplexity.COMPLEX:
            analysis["latency_tolerance"] = 60.0
            analysis["reliability_requirements"] = 0.85
        
        return analysis
    
    async def _get_available_layers(self) -> List[CommunicationLayer]:
        """Get list of currently available communication layers."""
        available_layers = []
        
        for layer, status in self.layer_status.items():
            if status and self.communication_layers[layer]["available"]:
                available_layers.append(layer)
        
        return available_layers
    
    async def _apply_routing_policy(self, query_analysis: Dict[str, Any], 
                                   context: QueryContext, 
                                   available_layers: List[CommunicationLayer]) -> RoutingDecision:
        """Apply routing policy to determine optimal layer."""
        
        # Get policy for query type
        policy = self.routing_policies.get(context.query_type, self.routing_policies[QueryType.LLM_REQUEST])
        
        # Get complexity-specific routing
        complexity_routing = policy.get("complexity_routing", {})
        preferred_layers = complexity_routing.get(context.complexity, policy["preferred_layers"])
        
        # Filter to available layers
        available_preferred = [layer for layer in preferred_layers if layer in available_layers]
        
        if not available_preferred:
            # No preferred layers available, use any available layer
            available_preferred = available_layers
        
        # Select optimal layer based on requirements
        best_layer = await self._select_optimal_layer(
            available_preferred, query_analysis, context
        )
        
        # Calculate fallback layers
        fallback_layers = [
            layer for layer in available_preferred 
            if layer != best_layer and layer in available_layers
        ]
        
        # Get layer metrics
        layer_config = self.communication_layers[best_layer]
        estimated_latency = layer_config["latency"]
        estimated_reliability = layer_config["reliability"]
        
        # Determine target node
        target_node = await self._determine_target_node(context, best_layer)
        
        # Calculate priority
        priority = self.priority_weights.get(context.complexity, 3)
        if context.emergency_level > 0:
            priority = 0
        
        return RoutingDecision(
            layer=best_layer,
            target_node=target_node,
            priority=priority,
            estimated_latency=estimated_latency,
            estimated_reliability=estimated_reliability,
            fallback_layers=fallback_layers,
            reason=f"Optimal layer for {context.query_type.value} {context.complexity.value} query"
        )
    
    async def _select_optimal_layer(self, available_layers: List[CommunicationLayer],
                                   query_analysis: Dict[str, Any],
                                   context: QueryContext) -> CommunicationLayer:
        """Select the optimal communication layer."""
        
        best_layer = available_layers[0]  # Default to first available
        best_score = -1
        
        for layer in available_layers:
            layer_config = self.communication_layers[layer]
            
            # Calculate layer score
            score = await self._calculate_layer_score(layer, layer_config, query_analysis, context)
            
            if score > best_score:
                best_score = score
                best_layer = layer
        
        return best_layer
    
    async def _calculate_layer_score(self, layer: CommunicationLayer, 
                                    layer_config: Dict[str, Any],
                                    query_analysis: Dict[str, Any],
                                    context: QueryContext) -> float:
        """Calculate score for a communication layer."""
        
        score = 0.0
        
        # Latency score (lower is better)
        latency_score = max(0, 1 - (layer_config["latency"] / query_analysis["latency_tolerance"]))
        score += latency_score * 0.3
        
        # Reliability score
        reliability_score = layer_config["reliability"] / query_analysis["reliability_requirements"]
        score += min(reliability_score, 1.0) * 0.3
        
        # Bandwidth score
        if query_analysis["bandwidth_requirements"] > 0:
            bandwidth_score = min(1.0, layer_config["bandwidth"] / query_analysis["bandwidth_requirements"])
            score += bandwidth_score * 0.2
        
        # Emergency priority bonus
        if context.emergency_level > 0:
            if layer == CommunicationLayer.SMS:
                score += 0.2  # SMS is most reliable for emergencies
            elif layer == CommunicationLayer.LORA:
                score += 0.1  # LoRa is good for emergencies
        
        # Complexity-based scoring
        if context.complexity == QueryComplexity.SIMPLE:
            if layer == CommunicationLayer.SMS:
                score += 0.1  # SMS is good for simple queries
        elif context.complexity == QueryComplexity.COMPLEX:
            if layer == CommunicationLayer.INTERNET:
                score += 0.1  # Internet is good for complex queries
        
        return score
    
    async def _determine_target_node(self, context: QueryContext, 
                                   layer: CommunicationLayer) -> Optional[str]:
        """Determine target node for routing."""
        
        # For SMS, target is usually the user's phone
        if layer == CommunicationLayer.SMS:
            return None  # SMS gateway handles targeting
        
        # For LoRa, find best mesh node
        elif layer == CommunicationLayer.LORA:
            return await self._find_best_mesh_node(context)
        
        # For Internet, find best internet-connected node
        elif layer == CommunicationLayer.INTERNET:
            return await self._find_best_internet_node(context)
        
        return None
    
    async def _find_best_mesh_node(self, context: QueryContext) -> Optional[str]:
        """Find the best mesh node for routing."""
        try:
            from backend.lilevy.services.lora_radio_service import lora_radio_service
            
            if not lora_radio_service.is_initialized:
                return None
            
            known_nodes = lora_radio_service.get_known_nodes()
            if not known_nodes:
                return None
            
            # Find node with best signal strength and capabilities
            best_node = None
            best_score = -1
            
            for node_id, node_info in known_nodes.items():
                if node_id == self.local_node_id:
                    continue
                
                # Calculate node score
                signal_score = max(0, (node_info.signal_strength + 120) / 40)  # Normalize signal strength
                capability_score = self._calculate_capability_score(node_info.capabilities, context)
                
                total_score = signal_score * 0.6 + capability_score * 0.4
                
                if total_score > best_score:
                    best_score = total_score
                    best_node = node_id
            
            return best_node
            
        except Exception as e:
            logger.error(f"Failed to find best mesh node: {e}")
            return None
    
    async def _find_best_internet_node(self, context: QueryContext) -> Optional[str]:
        """Find the best internet-connected node for routing."""
        # For now, assume bigEVY is the internet-connected node
        # In a real implementation, this would query a node registry
        
        internet_nodes = [node_id for node_id, capabilities in self.node_capabilities.items()
                         if capabilities.get("internet_connected", False)]
        
        if internet_nodes:
            return internet_nodes[0]  # Return first internet node
        
        return None
    
    def _calculate_capability_score(self, capabilities: Dict[str, Any], 
                                   context: QueryContext) -> float:
        """Calculate capability score for a node."""
        score = 0.0
        
        # Check for required capabilities
        if context.query_type == QueryType.LLM_REQUEST:
            if capabilities.get("llm_inference", False):
                score += 0.5
            if capabilities.get("processing_power") in ["medium", "high"]:
                score += 0.3
        
        elif context.query_type == QueryType.RAG_QUERY:
            if capabilities.get("rag_service", False):
                score += 0.5
            if capabilities.get("available_storage") in ["medium", "high"]:
                score += 0.3
        
        # Battery level bonus
        battery_level = capabilities.get("battery_level", 0)
        if battery_level > 80:
            score += 0.2
        elif battery_level > 50:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _layer_monitoring_loop(self):
        """Background task for monitoring communication layers."""
        while self.is_initialized:
            try:
                await self._update_layer_status()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Layer monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _update_layer_status(self):
        """Update status of communication layers."""
        # Update SMS layer (always available for lilEVY)
        self.layer_status[CommunicationLayer.SMS] = True
        
        # Update LoRa layer
        try:
            from backend.lilevy.services.lora_radio_service import lora_radio_service
            self.layer_status[CommunicationLayer.LORA] = lora_radio_service.is_initialized
        except ImportError:
            self.layer_status[CommunicationLayer.LORA] = False
        
        # Update Internet layer
        self.layer_status[CommunicationLayer.INTERNET] = await self._check_internet_availability()
        
        # Update Bluetooth layer (would check actual hardware)
        self.layer_status[CommunicationLayer.BLUETOOTH] = False
    
    async def _performance_tracking_loop(self):
        """Background task for tracking performance metrics."""
        while self.is_initialized:
            try:
                await self._update_performance_metrics()
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Performance tracking error: {e}")
                await asyncio.sleep(60)
    
    async def _update_performance_metrics(self):
        """Update performance metrics for each layer."""
        for layer in CommunicationLayer:
            if layer in self.stats["layer_usage"] and self.stats["layer_usage"][layer.value] > 0:
                # Calculate average latency and reliability
                # This would be based on actual performance data
                self.stats["average_latency"][layer.value] = self.communication_layers[layer]["latency"]
                self.stats["reliability_scores"][layer.value] = self.communication_layers[layer]["reliability"]
    
    def register_node(self, node_id: str, capabilities: Dict[str, Any]):
        """Register a node in the network topology."""
        self.known_nodes[node_id] = {
            "last_seen": time.time(),
            "capabilities": capabilities
        }
        self.node_capabilities[node_id] = capabilities
        logger.info(f"Registered node: {node_id}")
    
    def unregister_node(self, node_id: str):
        """Unregister a node from the network topology."""
        if node_id in self.known_nodes:
            del self.known_nodes[node_id]
        if node_id in self.node_capabilities:
            del self.node_capabilities[node_id]
        logger.info(f"Unregistered node: {node_id}")
    
    def get_network_topology(self) -> Dict[str, Any]:
        """Get current network topology."""
        return {
            "known_nodes": self.known_nodes.copy(),
            "node_capabilities": self.node_capabilities.copy(),
            "layer_status": self.layer_status.copy(),
            "layer_capabilities": self.layer_capabilities.copy()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            **self.stats,
            "is_initialized": self.is_initialized,
            "available_layers": [layer.value for layer, status in self.layer_status.items() if status],
            "total_known_nodes": len(self.known_nodes),
            "routing_policies": len(self.routing_policies)
        }
    
    async def cleanup(self):
        """Cleanup smart communication router."""
        try:
            self.is_initialized = False
            logger.info("Smart Communication Router cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global router instance
smart_router = SmartCommunicationRouter("lilevy-001")
