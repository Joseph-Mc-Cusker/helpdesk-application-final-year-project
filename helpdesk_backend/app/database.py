from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "helpdesk_db")

client: Optional[AsyncIOMotorClient] = None
db = None


async def connect_to_mongo() -> None:
  """Create MongoDB client on startup."""
  global client, db
  client = AsyncIOMotorClient(MONGODB_URL)
  db = client[DATABASE_NAME]
  print(f"Connected to MongoDB: {DATABASE_NAME}")


async def close_mongo_connection() -> None:
  """Close MongoDB client on shutdown."""
  global client
  if client is not None:
    client.close()
    print("Disconnected from MongoDB")


def get_db():
  """Return current database handle."""
  if db is None:
    raise RuntimeError("Database not initialised. Did you call connect_to_mongo?")
  return db

