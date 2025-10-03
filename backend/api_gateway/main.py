"""API Gateway - Main entry point for EVY system."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from typing import Dict, List

from backend.shared.models import SMSMessage, ServiceHealth
from backend.shared.config import settings
from backend.shared.logging import setup_logger

logger = setup_logger("api-gateway")


class APIGateway:
    """Manages routing to microservices."""
    
    def __init__(self):
        self.services = {
            "sms-gateway": f"http://localhost:{settings.sms_gateway_port}",
            "message-router": f"http://localhost:{settings.message_router_port}",
            "llm-inference": f"http://localhost:{settings.llm_inference_port}",
            "rag-service": f"http://localhost:{settings.rag_service_port}",
            "privacy-filter": f"http://localhost:{settings.privacy_filter_port}",
        }
    
    async def check_all_services(self) -> Dict[str, Dict]:
        """Check health of all services."""
        results = {}
        
        async with httpx.AsyncClient() as client:
            for service_name, service_url in self.services.items():
                try:
                    response = await client.get(
                        f"{service_url}/health",
                        timeout=5.0
                    )
                    if response.status_code == 200:
                        results[service_name] = {
                            "status": "healthy",
                            "details": response.json()
                        }
                    else:
                        results[service_name] = {
                            "status": "unhealthy",
                            "code": response.status_code
                        }
                except Exception as e:
                    results[service_name] = {
                        "status": "unreachable",
                        "error": str(e)
                    }
        
        return results


# Global gateway instance
api_gateway = APIGateway()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the service."""
    logger.info("API Gateway starting up...")
    logger.info(f"Services configured: {list(api_gateway.services.keys())}")
    yield
    logger.info("API Gateway shutting down...")


# Create FastAPI app
app = FastAPI(
    title="EVY API Gateway",
    description="Main API gateway for EVY SMS-based AI system",
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "EVY API Gateway",
        "version": "1.0.0",
        "description": "Everyone's Voice, Everywhere, Everytime",
        "services": list(api_gateway.services.keys())
    }


@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Health check endpoint."""
    return ServiceHealth(
        service_name="api-gateway",
        status="healthy",
        version="1.0.0"
    )


@app.get("/services/health")
async def check_services():
    """Check health of all services."""
    results = await api_gateway.check_all_services()
    
    # Determine overall status
    all_healthy = all(
        service["status"] == "healthy"
        for service in results.values()
    )
    
    return {
        "overall_status": "healthy" if all_healthy else "degraded",
        "services": results
    }


@app.post("/sms/send")
async def send_sms(message: SMSMessage):
    """Send an SMS message."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_gateway.services['sms-gateway']}/sms/send",
                json=message.model_dump(mode='json'),
                timeout=30.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sms/receive")
async def receive_sms(message: SMSMessage):
    """Receive and process an SMS message."""
    try:
        # First validate with privacy filter
        async with httpx.AsyncClient() as client:
            validation_response = await client.post(
                f"{api_gateway.services['privacy-filter']}/validate",
                json=message.model_dump(mode='json'),
                timeout=10.0
            )
            
            validation = validation_response.json()
            
            if not validation.get("valid", False):
                return {
                    "status": "rejected",
                    "reason": validation.get("reason", "validation_failed")
                }
            
            # Forward to SMS gateway for processing
            process_response = await client.post(
                f"{api_gateway.services['sms-gateway']}/sms/receive",
                json=message.model_dump(mode='json'),
                timeout=30.0
            )
            
            return process_response.json()
            
    except Exception as e:
        logger.error(f"Error receiving SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sms/history")
async def get_sms_history(limit: int = 50):
    """Get SMS history."""
    try:
        async with httpx.AsyncClient() as client:
            sent_response = await client.get(
                f"{api_gateway.services['sms-gateway']}/sms/sent?limit={limit}",
                timeout=10.0
            )
            received_response = await client.get(
                f"{api_gateway.services['sms-gateway']}/sms/received?limit={limit}",
                timeout=10.0
            )
            
            return {
                "sent": sent_response.json(),
                "received": received_response.json()
            }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_gateway.services['rag-service']}/stats",
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.api_gateway_port,
        log_level="info"
    )


