from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sys
import os
import time

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from models import Chat, Message, ActivityLog
from cache_manager import check_cache, save_to_cache, apply_refusal
from security import validate_api_key, validate_question, validate_chat_title, sanitize_input

# Import RAG modules (DO NOT MODIFY THESE FILES)
from rag.retrieve import retrieve
from rag.generate import generate

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize rate limiter
if config.RATE_LIMIT_ENABLED:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[config.RATE_LIMIT_GLOBAL],
        storage_uri="memory://"
    )
else:
    limiter = None

# Initialize models at startup (loaded once, never reloaded)
print("=" * 50)
print("🚀 Starting NLP Assistant Backend")
print("=" * 50)
print("✅ Loading FAISS index and sentence transformer...")
print("✅ Loading FLAN-T5 model...")
print("✅ Models loaded successfully!")
if config.RATE_LIMIT_ENABLED:
    print("🔒 Rate limiting enabled")
if config.REQUIRE_API_KEY:
    print("🔑 API key authentication required")
print("=" * 50)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "NLP Assistant API is running"})


@app.route('/api/ask', methods=['POST'])
@limiter.limit(config.RATE_LIMIT_ASK) if config.RATE_LIMIT_ENABLED else lambda f: f
@validate_api_key
def ask_question():
    """
    Main endpoint to ask a question.
    Checks cache first, then runs RAG pipeline if not cached.
    """
    try:
        data = request.json
        question = data.get('question', '').strip()
        chat_id = data.get('chat_id')
        
        # Validate and sanitize question
        is_valid, sanitized_question, error_msg = validate_question(question)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        question = sanitized_question
        
        # Check cache first
        cached_result = check_cache(question)
        
        if cached_result:
            # Return cached answer
            answer = cached_result['answer']
            sources = cached_result['sources']
            confidence = cached_result['confidence']
            scores = cached_result.get('scores', [])
            
            # Save user message
            if chat_id:
                Message.create(chat_id, "user", question)
                Message.create(chat_id, "assistant", answer, {
                    "cached": True,
                    "confidence": confidence,
                    "sources": sources
                })
                Chat.update_timestamp(chat_id)
            
            # Log activity
            ActivityLog.log(
                question=question,
                answer=answer,
                confidence_score=confidence,
                sources=sources,
                was_cached=True,
                chat_id=chat_id,
                scores=scores
            )
            
            return jsonify({
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "cached": True,
                "scores": scores
            })
        
        # Not in cache - run RAG pipeline
        # Step 1: Retrieve relevant documents (THINKING phase)
        retrieval_start = time.time()
        sources, scores = retrieve(question, top_k=config.TOP_K)
        retrieval_time = time.time() - retrieval_start
        
        # Step 2: Apply refusal logic based on confidence
        generation_start = time.time()
        
        # Check if we should refuse to answer
        min_score = min(scores) if len(scores) > 0 else float('inf')
        
        if min_score >= config.CONFIDENCE_THRESHOLD:
            # Low confidence - apply refusal
            answer, sources, confidence = apply_refusal("", sources, scores)
            generation_time = time.time() - generation_start
        else:
            # High confidence - generate answer (GENERATING phase)
            answer = generate(question, sources)
            generation_time = time.time() - generation_start
            
            # Check if generation returned a refusal (despite high retrieval confidence)
            is_refusal = "I am not confident enough to answer" in answer
            confidence = "Low" if is_refusal else "High"
            
            # Only save to cache if it's not a refusal
            if not is_refusal:
                save_to_cache(question, answer, confidence, sources, scores)
        
        # Save messages to chat
        if chat_id:
            Message.create(chat_id, "user", question)
            Message.create(chat_id, "assistant", answer, {
                "cached": False,
                "confidence": confidence,
                "sources": sources,
                "retrieval_time": retrieval_time,
                "generation_time": generation_time
            })
            Chat.update_timestamp(chat_id)
        
        # Log activity
        ActivityLog.log(
            question=question,
            answer=answer,
            confidence_score=confidence,
            sources=sources,
            was_cached=False,
            retrieval_time=retrieval_time,
            generation_time=generation_time,
            chat_id=chat_id,
            scores=scores
        )
        
        return jsonify({
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "cached": False,
            "retrieval_time": retrieval_time,
            "generation_time": generation_time,
            "scores": scores.tolist() if hasattr(scores, 'tolist') else scores
        })
        
    except Exception as e:
        print(f"Error in ask_question: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/chats', methods=['GET'])
@limiter.limit(config.RATE_LIMIT_CHAT) if config.RATE_LIMIT_ENABLED else lambda f: f
@validate_api_key
def get_chats():
    """Get all chat sessions"""
    try:
        chats = Chat.get_all()
        # Convert ObjectId to string for JSON serialization
        for chat in chats:
            chat['_id'] = str(chat['_id'])
        return jsonify(chats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chats/new', methods=['POST'])
@limiter.limit(config.RATE_LIMIT_CHAT) if config.RATE_LIMIT_ENABLED else lambda f: f
@validate_api_key
def create_new_chat():
    """Create a new chat session"""
    try:
        data = request.json or {}
        title = data.get('title', 'New Chat')
        
        # Sanitize title
        title = sanitize_input(title, max_length=config.MAX_TITLE_LENGTH)
        
        chat = Chat.create(title)
        chat['_id'] = str(chat['_id'])
        return jsonify(chat)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chats/<chat_id>', methods=['GET'])
@limiter.limit(config.RATE_LIMIT_CHAT) if config.RATE_LIMIT_ENABLED else lambda f: f
@validate_api_key
def get_chat_messages(chat_id):
    """Get all messages for a specific chat"""
    try:
        messages = Message.get_by_chat(chat_id)
        # Convert ObjectId to string
        for msg in messages:
            msg['_id'] = str(msg['_id'])
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chats/<chat_id>', methods=['DELETE'])
@limiter.limit(config.RATE_LIMIT_CHAT) if config.RATE_LIMIT_ENABLED else lambda f: f
@validate_api_key
def delete_chat(chat_id):
    """Delete a chat session and all its messages"""
    try:
        Chat.delete(chat_id)
        return jsonify({"message": "Chat deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chats/<chat_id>/title', methods=['PUT'])
@limiter.limit(config.RATE_LIMIT_CHAT) if config.RATE_LIMIT_ENABLED else lambda f: f
@validate_api_key
def update_chat_title(chat_id):
    """Update a chat's title"""
    try:
        data = request.json
        new_title = data.get('title', '').strip()
        
        # Validate and sanitize title
        is_valid, sanitized_title, error_msg = validate_chat_title(new_title)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        Chat.update_title(chat_id, sanitized_title)
        return jsonify({"message": "Title updated successfully", "title": sanitized_title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n🌐 Server running on http://localhost:5000")
    print("📡 Ready to receive requests!\n")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.DEBUG
    )
