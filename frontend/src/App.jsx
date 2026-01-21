import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { api } from './services/api';
import './App.css';

function App() {
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingState, setLoadingState] = useState('thinking'); // 'thinking' or 'generating'

  // Load chats on mount
  useEffect(() => {
    loadChats();
  }, []);

  // Load messages when active chat changes
  useEffect(() => {
    if (activeChat) {
      loadMessages(activeChat);
    }
  }, [activeChat]);

  const loadChats = async () => {
    try {
      const fetchedChats = await api.getChats();
      setChats(fetchedChats);

      // If no active chat and chats exist, select the first one
      if (!activeChat && fetchedChats.length > 0) {
        setActiveChat(fetchedChats[0]._id);
      }
    } catch (error) {
      console.error('Failed to load chats:', error);
    }
  };

  const loadMessages = async (chatId) => {
    try {
      const fetchedMessages = await api.getChatMessages(chatId);
      setMessages(fetchedMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      setMessages([]);
    }
  };

  const handleNewChat = async () => {
    try {
      const newChat = await api.createNewChat();
      setChats([newChat, ...chats]);
      setActiveChat(newChat._id);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create new chat:', error);
    }
  };

  const handleSelectChat = (chatId) => {
    setActiveChat(chatId);
  };

  const handleDeleteChat = async (chatId) => {
    try {
      await api.deleteChat(chatId);
      const updatedChats = chats.filter((c) => c._id !== chatId);
      setChats(updatedChats);

      // If deleted chat was active, select another
      if (activeChat === chatId) {
        if (updatedChats.length > 0) {
          setActiveChat(updatedChats[0]._id);
        } else {
          setActiveChat(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  const handleRenameChat = async (chatId, newTitle) => {
    try {
      await api.updateChatTitle(chatId, newTitle);
      // Update local state
      setChats(chats.map(chat =>
        chat._id === chatId ? { ...chat, title: newTitle } : chat
      ));
    } catch (error) {
      console.error('Failed to rename chat:', error);
    }
  };

  const generateChatTitle = (question) => {
    // Generate a title from the first question (first 50 chars)
    const maxLength = 50;
    if (question.length <= maxLength) {
      return question;
    }
    // Truncate at word boundary
    const truncated = question.substring(0, maxLength);
    const lastSpace = truncated.lastIndexOf(' ');
    return lastSpace > 0 ? truncated.substring(0, lastSpace) + '...' : truncated + '...';
  };

  const handleSendMessage = async (question) => {
    // Create a new chat if none exists
    let currentChatId = activeChat;

    if (!currentChatId) {
      try {
        const newChat = await api.createNewChat();
        setChats([newChat, ...chats]);
        setActiveChat(newChat._id);
        currentChatId = newChat._id;
      } catch (error) {
        console.error('Failed to create chat:', error);
        return;
      }
    }

    // Check if this is the first message in the chat
    const isFirstMessage = messages.length === 0;

    // Add user message to UI immediately
    const userMessage = {
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Start loading
    setIsLoading(true);
    setLoadingState('thinking');

    try {
      // Simulate thinking phase
      setTimeout(() => {
        setLoadingState('generating');
      }, 500);

      const response = await api.askQuestion(currentChatId, question);

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
        metadata: {
          cached: response.cached,
          confidence: response.confidence,
          sources: response.sources,
        },
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Auto-generate title from first question
      if (isFirstMessage) {
        const autoTitle = generateChatTitle(question);
        await handleRenameChat(currentChatId, autoTitle);
      }

      // Reload chats to update timestamp
      loadChats();
    } catch (error) {
      console.error('Failed to get answer:', error);

      // Add error message
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        metadata: {},
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        chats={chats}
        activeChat={activeChat}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
      />
      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        loadingState={loadingState}
      />
    </div>
  );
}

export default App;
