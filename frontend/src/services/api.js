const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
  // Ask a question
  askQuestion: async (chatId, question) => {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ chat_id: chatId, question }),
    });

    if (!response.ok) {
      throw new Error('Failed to get answer');
    }

    return response.json();
  },

  // Get all chats
  getChats: async () => {
    const response = await fetch(`${API_BASE_URL}/chats`);

    if (!response.ok) {
      throw new Error('Failed to fetch chats');
    }

    return response.json();
  },

  // Create a new chat
  createNewChat: async (title = 'New Chat') => {
    const response = await fetch(`${API_BASE_URL}/chats/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error('Failed to create chat');
    }

    return response.json();
  },

  // Get chat messages
  getChatMessages: async (chatId) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`);

    if (!response.ok) {
      throw new Error('Failed to fetch messages');
    }

    return response.json();
  },

  // Delete a chat
  deleteChat: async (chatId) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete chat');
    }

    return response.json();
  },

  // Update chat title
  updateChatTitle: async (chatId, title) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}/title`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error('Failed to update chat title');
    }

    return response.json();
  },
};
