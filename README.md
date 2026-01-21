# NLP Assistant Chatbot

A ChatGPT-style web application for NLP-powered question answering with intelligent caching and chat history.

## Features

- 🤖 **RAG-based Q&A** - Retrieval-Augmented Generation using FAISS + FLAN-T5
- ⚡ **Smart Caching** - High-confidence answers cached for instant responses
- 🧠 **Refusal Logic** - Returns "not confident" message for low-confidence queries
- 💬 **Chat History** - Persistent chat sessions with MongoDB
- 📊 **Activity Logging** - Complete logging of all Q&A interactions
- 🎨 **Modern UI** - ChatGPT-inspired dark mode interface

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (or local MongoDB)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Verify environment variables:**
   - Check that `.env` file exists in `backend/` directory
   - Ensure MongoDB URI is correctly configured

4. **Start the Flask server:**
   ```bash
   python app.py
   ```
   
   The server will start on `http://localhost:5000`
   
   **Note:** Models (FAISS index, sentence transformer, FLAN-T5) load once at startup. This may take 30-60 seconds.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The app will open at `http://localhost:5173` (or another port if 5173 is busy)

## Usage

1. **Start a new chat** - Click the "New Chat" button in the sidebar
2. **Ask a question** - Type your question in the input box and press Enter or click send
3. **View indicators**:
   - 🤔 **Thinking...** - Retrieving relevant documents
   - ✍️ **Generating...** - Generating answer
   - ⚡ **Cached** - Answer retrieved from cache
   - ✓ **High Confidence** - Confident answer
   - ⚠️ **Low Confidence** - Low confidence (refusal message)
4. **Manage chats** - Switch between chats or delete old ones from the sidebar

## Configuration

Configuration values can be adjusted in `backend/.env`:

- `TOP_K=5` - Number of documents to retrieve
- `CONFIDENCE_THRESHOLD=1.2` - Minimum confidence score (lower is better)
- `MAX_GENERATION_LENGTH=400` - Maximum answer length

## Caching Behavior

The system caches answers when:
- Confidence score is below the threshold (high confidence)
- Answer is meaningful and in-domain

Cached answers are returned instantly on repeat questions.

## MongoDB Collections

- **chats** - Chat session metadata
- **messages** - Individual chat messages
- **cache** - Cached Q&A pairs
- **activity_log** - Complete activity logs with timestamps and metadata

## Tech Stack

**Backend:**
- Flask + Flask-CORS
- FAISS (vector similarity search)
- Sentence Transformers (all-MiniLM-L6-v2)
- Hugging Face Transformers (FLAN-T5-base)
- PyMongo (MongoDB driver)

**Frontend:**
- React 19 + Vite
- Modern CSS with dark mode
- Responsive design

## Important Notes

⚠️ **DO NOT MODIFY**:
- `backend/rag/retrieve.py`
- `backend/rag/generate.py`
- `backend/data/chunks.pkl`
- `backend/data/faiss.index`

These files contain the pre-trained models and vector database. Modifications will break the system.

## Troubleshooting

**Backend won't start:**
- Ensure MongoDB URI is correct in `.env`
- Check that all Python dependencies are installed
- Verify `chunks.pkl` and `faiss.index` exist in `backend/data/`

**Frontend can't connect:**
- Ensure backend is running on port 5000
- Check browser console for CORS errors
- Verify API_BASE_URL in `frontend/src/services/api.js`

**Models loading slowly:**
- First startup takes 30-60 seconds to load models
- This is normal - models load once and stay in memory
