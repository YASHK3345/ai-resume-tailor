from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

# Import routes
from routes.auth_routes import router as auth_router
from routes.cv_routes import router as cv_router
from routes.ai_routes import router as ai_router
from routes.template_routes import router as template_router
from routes.export_routes import router as export_router
from routes.stripe_routes import router as stripe_router

# Import middleware
from middleware import LoggingMiddleware, RateLimitMiddleware

# Import database
from database import close_database_connection

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(
    title="CraftMyCV API",
    description="AI-powered CV builder with ATS optimization",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "CraftMyCV API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "craftmycv-api",
        "version": "1.0.0"
    }

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(cv_router)
api_router.include_router(ai_router)
api_router.include_router(template_router)
api_router.include_router(export_router)
api_router.include_router(stripe_router)

# Include the API router in the main app
app.include_router(api_router)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=1000, period=60)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("CraftMyCV API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("CraftMyCV API shutting down...")
    await close_database_connection()
