import motor.motor_asyncio
from core.config import mongodb
from pymongo.collection import ReturnDocument

db = motor.motor_asyncio.AsyncIOMotorClient(**mongodb).bot
