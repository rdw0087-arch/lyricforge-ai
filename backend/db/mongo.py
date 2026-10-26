import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "ai_video_generator")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable is required")

client = AsyncIOMotorClient(MONGO_URL)
db: AsyncIOMotorDatabase = client[DB_NAME]


def get_db() -> AsyncIOMotorDatabase:
    return db
