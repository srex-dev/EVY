"""Node-to-node communication client for EVY system."""
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
import hashlib
from dataclasses import dataclass

from backend.shared.deployment_config import NodeType, get_deployment_profile
from backend.shared.models import SMSMessage, LLMRequest, LLMResponse, RAGQuery, RAGResult
from backend.shared.logging import setup_logger

logger = setup_logger("node-communication")


@dataclass
class NodeInfo:
    """Information about a remote EVY node."""
    node_id: str
    node_type: NodeType
    address: str
    port: int
    capabilities: Dict[str, Any]
    last_seen: datetime
    is_online: bool = False


class NodeClient:
    """Client for communicating with other EVY nodes."""
    
    def __init__(self, local_node_type: NodeType, local_node_id: str):
        self.local_node_type = local_node_type
        self.local_node_id = local_node_id
        self.known_nodes: Dict[str, NodeInfo] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Communication settings
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.retry_attempts = 3
        self.retry_delay = 1.0
        
        # Discovery settings
        self.discovery_interval = 300  # 5 minutes
        self.node_timeout = 1800  # 30 minutes
        
    async def initialize(self):
        """Initialize the communication client."""
        try:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.info(f"Node client initialized for {self.local_node_type.value} node {self.local_node_id}")
            
            # Start discovery if enabled
            if self._should_discover_peers():
                asyncio.create_task(self._peer_discovery_loop())
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize node client: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup the communication client."""
        if self.session:
            await self.session.close()
        logger.info("Node client cleaned up")
    
    def _should_discover_peers(self) -> bool:
        """Check if this node type should discover peers."""
        profile = get_deployment_profile(self.local_node_type)
        return profile.network.peer_discovery
    
    async def register_node(self, node_info: Dict[str, Any]) -> bool:
        """Register this node with the network."""
        try:
            # For now, just log the registration
            # In a real implementation, this would register with a discovery service
            logger.info(f"Node registered: {node_info}")
            return True
        except Exception as e:
            logger.error(f"Failed to register node: {e}")
            return False
    
    async def discover_peers(self) -> List[NodeInfo]:
        """Discover other EVY nodes on the network."""
        try:
            # In a real implementation, this would use mDNS, UPnP, or a discovery service
            # For now, return empty list
            discovered_nodes = []
            
            # Clean up old nodes
            current_time = datetime.utcnow()
            nodes_to_remove = []
            
            for node_id, node in self.known_nodes.items():
                if (current_time - node.last_seen).total_seconds() > self.node_timeout:
                    nodes_to_remove.append(node_id)
            
            for node_id in nodes_to_remove:
                del self.known_nodes[node_id]
                logger.info(f"Removed stale node: {node_id}")
            
            return discovered_nodes
            
        except Exception as e:
            logger.error(f"Failed to discover peers: {e}")
            return []
    
    async def _peer_discovery_loop(self):
        """Background task for peer discovery."""
        while True:
            try:
                await self.discover_peers()
                await asyncio.sleep(self.discovery_interval)
            except Exception as e:
                logger.error(f"Peer discovery error: {e}")
                await asyncio.sleep(self.discovery_interval)
    
    async def forward_llm_request(self, request: LLMRequest, target_node_type: NodeType) -> Optional[LLMResponse]:
        """Forward LLM request to appropriate node type."""
        try:
            # Find suitable node
            target_node = self._find_suitable_node(target_node_type)
            if not target_node:
                logger.warning(f"No suitable {target_node_type.value} node available")
                return None
            
            # Forward request
            url = f"http://{target_node.address}:{target_node.port}/llm/generate"
            
            async with self.session.post(url, json=request.dict()) as response:
                if response.status == 200:
                    result = await response.json()
                    return LLMResponse(**result)
                else:
                    logger.error(f"LLM request failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to forward LLM request: {e}")
            return None
    
    async def forward_rag_request(self, query: RAGQuery, target_node_type: NodeType) -> Optional[RAGResult]:
        """Forward RAG request to appropriate node type."""
        try:
            # Find suitable node
            target_node = self._find_suitable_node(target_node_type)
            if not target_node:
                logger.warning(f"No suitable {target_node_type.value} node available")
                return None
            
            # Forward request
            url = f"http://{target_node.address}:{target_node.port}/search"
            
            async with self.session.post(url, json=query.dict()) as response:
                if response.status == 200:
                    result = await response.json()
                    return RAGResult(**result)
                else:
                    logger.error(f"RAG request failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to forward RAG request: {e}")
            return None
    
    async def sync_knowledge(self, local_documents: List[Dict[str, Any]]) -> bool:
        """Sync local knowledge with bigEVY nodes."""
        try:
            if self.local_node_type != NodeType.LILEVY:
                return False
            
            # Find bigEVY nodes
            bigevy_nodes = [node for node in self.known_nodes.values() 
                           if node.node_type == NodeType.BIGEVY and node.is_online]
            
            if not bigevy_nodes:
                logger.warning("No bigEVY nodes available for knowledge sync")
                return False
            
            # Sync with first available bigEVY node
            target_node = bigevy_nodes[0]
            url = f"http://{target_node.address}:{target_node.port}/sync/knowledge"
            
            async with self.session.post(url, json={"documents": local_documents}) as response:
                if response.status == 200:
                    logger.info(f"Knowledge synced with {target_node.node_id}")
                    return True
                else:
                    logger.error(f"Knowledge sync failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to sync knowledge: {e}")
            return False
    
    async def get_analytics(self) -> Optional[Dict[str, Any]]:
        """Get analytics from bigEVY nodes."""
        try:
            if self.local_node_type != NodeType.LILEVY:
                return None
            
            # Find bigEVY nodes
            bigevy_nodes = [node for node in self.known_nodes.values() 
                           if node.node_type == NodeType.BIGEVY and node.is_online]
            
            if not bigevy_nodes:
                return None
            
            # Get analytics from first available bigEVY node
            target_node = bigevy_nodes[0]
            url = f"http://{target_node.address}:{target_node.port}/analytics/global"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Analytics request failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return None
    
    def _find_suitable_node(self, node_type: NodeType) -> Optional[NodeInfo]:
        """Find a suitable node of the specified type."""
        suitable_nodes = [node for node in self.known_nodes.values() 
                         if node.node_type == node_type and node.is_online]
        
        if not suitable_nodes:
            return None
        
        # For now, return the first available node
        # In a real implementation, this would use load balancing
        return suitable_nodes[0]
    
    def add_known_node(self, node_info: NodeInfo):
        """Add a known node to the registry."""
        self.known_nodes[node_info.node_id] = node_info
        logger.info(f"Added known node: {node_info.node_id} ({node_info.node_type.value})")
    
    def get_known_nodes(self) -> Dict[str, NodeInfo]:
        """Get all known nodes."""
        return self.known_nodes.copy()
    
    def get_node_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of this node."""
        profile = get_deployment_profile(self.local_node_type)
        return {
            "node_id": self.local_node_id,
            "node_type": self.local_node_type.value,
            "capabilities": profile.features,
            "services": profile.services,
            "hardware": profile.hardware.dict()
        }


class HybridOrchestrator:
    """Orchestrates requests between lilEVY and bigEVY nodes."""
    
    def __init__(self, local_node_type: NodeType, local_node_id: str):
        self.node_client = NodeClient(local_node_type, local_node_id)
        self.local_node_type = local_node_type
        
        # Fallback settings
        self.fallback_enabled = True
        self.complexity_threshold = 0.7  # Threshold for offloading to bigEVY
    
    async def initialize(self):
        """Initialize the orchestrator."""
        return await self.node_client.initialize()
    
    async def cleanup(self):
        """Cleanup the orchestrator."""
        await self.node_client.cleanup()
    
    async def process_llm_request(self, request: LLMRequest) -> LLMResponse:
        """Process LLM request with hybrid routing."""
        try:
            # Determine if request should be handled locally or forwarded
            should_forward = self._should_forward_to_bigevy(request)
            
            if should_forward and self.local_node_type == NodeType.LILEVY:
                # Try to forward to bigEVY
                response = await self.node_client.forward_llm_request(request, NodeType.BIGEVY)
                if response:
                    return response
                
                # Fallback to local processing
                if self.fallback_enabled:
                    logger.info("Falling back to local LLM processing")
                    # This would call the local LLM service
                    # For now, return a simple response
                    return LLMResponse(
                        response="Request processed locally (fallback)",
                        model_used="local-fallback",
                        tokens_used=0,
                        processing_time=0.1
                    )
            
            # Handle locally
            # This would call the appropriate local LLM service
            return LLMResponse(
                response="Request processed locally",
                model_used="local",
                tokens_used=0,
                processing_time=0.1
            )
            
        except Exception as e:
            logger.error(f"Failed to process LLM request: {e}")
            return LLMResponse(
                response="Error processing request",
                model_used="error",
                tokens_used=0,
                processing_time=0.1
            )
    
    async def process_rag_request(self, query: RAGQuery) -> RAGResult:
        """Process RAG request with hybrid routing."""
        try:
            # Determine if request should be handled locally or forwarded
            should_forward = self._should_forward_to_bigevy(query)
            
            if should_forward and self.local_node_type == NodeType.LILEVY:
                # Try to forward to bigEVY
                result = await self.node_client.forward_rag_request(query, NodeType.BIGEVY)
                if result:
                    return result
                
                # Fallback to local processing
                if self.fallback_enabled:
                    logger.info("Falling back to local RAG processing")
                    # This would call the local RAG service
                    return RAGResult(documents=[], scores=[], metadata=[])
            
            # Handle locally
            # This would call the appropriate local RAG service
            return RAGResult(documents=[], scores=[], metadata=[])
            
        except Exception as e:
            logger.error(f"Failed to process RAG request: {e}")
            return RAGResult(documents=[], scores=[], metadata=[])
    
    def _should_forward_to_bigevy(self, request: Any) -> bool:
        """Determine if request should be forwarded to bigEVY."""
        # Simple heuristics for now
        if isinstance(request, LLMRequest):
            # Forward if request is complex (long, multiple questions, etc.)
            complexity_score = len(request.prompt) / 1000.0  # Simple length-based scoring
            return complexity_score > self.complexity_threshold
        
        elif isinstance(request, RAGQuery):
            # Forward if query is complex or requires global knowledge
            complexity_score = len(request.query) / 500.0
            return complexity_score > self.complexity_threshold
        
        return False
    
    async def sync_with_peers(self, local_data: Dict[str, Any]) -> bool:
        """Sync local data with peer nodes."""
        try:
            if self.local_node_type == NodeType.LILEVY:
                # Sync knowledge with bigEVY
                documents = local_data.get("documents", [])
                return await self.node_client.sync_knowledge(documents)
            else:
                # bigEVY nodes don't sync up, they receive syncs
                return True
                
        except Exception as e:
            logger.error(f"Failed to sync with peers: {e}")
            return False
