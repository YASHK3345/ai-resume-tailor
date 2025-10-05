from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    """Get database instance"""
    if db.client is None:
        mongo_url = os.environ['MONGO_URL']
        db.client = AsyncIOMotorClient(mongo_url)
        db.database = db.client[os.environ['DB_NAME']]
    
    return db.database

async def close_database_connection():
    """Close database connection"""
    if db.client:
        db.client.close()