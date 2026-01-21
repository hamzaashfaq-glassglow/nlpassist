from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import config

# Initialize MongoDB client
client = MongoClient(config.MONGO_URI)
db = client[config.DATABASE_NAME]

# Collections
chats_collection = db["chats"]
messages_collection = db["messages"]
cache_collection = db["cache"]
activity_log_collection = db["activity_log"]


class Chat:
    @staticmethod
    def create(title="New Chat"):
        """Create a new chat session"""
        chat = {
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = chats_collection.insert_one(chat)
        chat["_id"] = result.inserted_id
        return chat

    @staticmethod
    def get_all():
        """Get all chat sessions"""
        return list(chats_collection.find().sort("updated_at", -1))

    @staticmethod
    def get_by_id(chat_id):
        """Get a specific chat by ID"""
        return chats_collection.find_one({"_id": ObjectId(chat_id)})

    @staticmethod
    def update_timestamp(chat_id):
        """Update the last updated timestamp"""
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )

    @staticmethod
    def update_title(chat_id, new_title):
        """Update the chat title"""
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"title": new_title, "updated_at": datetime.utcnow()}}
        )

    @staticmethod
    def delete(chat_id):
        """Delete a chat and all its messages"""
        messages_collection.delete_many({"chat_id": chat_id})
        chats_collection.delete_one({"_id": ObjectId(chat_id)})


class Message:
    @staticmethod
    def create(chat_id, role, content, metadata=None):
        """Create a new message in a chat"""
        message = {
            "chat_id": chat_id,
            "role": role,  # "user" or "assistant"
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        }
        result = messages_collection.insert_one(message)
        message["_id"] = result.inserted_id
        return message

    @staticmethod
    def get_by_chat(chat_id):
        """Get all messages for a specific chat"""
        return list(messages_collection.find({"chat_id": chat_id}).sort("timestamp", 1))


class Cache:
    @staticmethod
    def find_cached(question, similarity_threshold=0.9):
        """
        Find a cached answer for the question.
        For now, we'll do exact match. Can be enhanced with semantic similarity.
        """
        # Exact match
        cached = cache_collection.find_one({"question": question})
        if cached:
            return cached
        
        # Could add semantic similarity search here using embeddings
        return None

    @staticmethod
    def save(question, answer, confidence, sources, scores):
        """Save a Q&A pair to cache"""
        cache_entry = {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "scores": scores.tolist() if hasattr(scores, 'tolist') else scores,
            "created_at": datetime.utcnow(),
            "access_count": 0
        }
        cache_collection.insert_one(cache_entry)

    @staticmethod
    def increment_access(question):
        """Increment the access count for a cached question"""
        cache_collection.update_one(
            {"question": question},
            {"$inc": {"access_count": 1}}
        )


class ActivityLog:
    @staticmethod
    def log(question, answer, confidence_score, sources, was_cached, 
            retrieval_time=0, generation_time=0, chat_id=None, scores=None):
        """Log all Q&A activity to MongoDB"""
        log_entry = {
            "question": question,
            "answer": answer,
            "confidence_score": confidence_score,
            "sources": sources,
            "was_cached": was_cached,
            "retrieval_time": retrieval_time,
            "generation_time": generation_time,
            "chat_id": chat_id,
            "scores": scores.tolist() if hasattr(scores, 'tolist') else scores,
            "timestamp": datetime.utcnow()
        }
        activity_log_collection.insert_one(log_entry)
