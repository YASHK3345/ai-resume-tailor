from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {str(e)} - {process_time:.4f}s")
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: timestamps for ip, timestamps in self.clients.items()
            if any(t > current_time - self.period for t in timestamps)
        }
        
        # Check rate limit for current client
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Remove old timestamps
        self.clients[client_ip] = [
            t for t in self.clients[client_ip] 
            if t > current_time - self.period
        ]
        
        # Check if limit exceeded
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Add current request timestamp
        self.clients[client_ip].append(current_time)
        
        response = await call_next(request)
        return response