import motor.motor_asyncio
from bson.objectid import ObjectId  # noqa: F401
from pymongo.collection import ReturnDocument  # noqa: F401

from core.config import mongodb

db = motor.motor_asyncio.AsyncIOMotorClient(**mongodb).bot
