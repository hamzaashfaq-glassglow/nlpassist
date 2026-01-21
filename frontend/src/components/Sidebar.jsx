import { useState } from 'react';
import './Sidebar.css';

function Sidebar({ chats, activeChat, onSelectChat, onNewChat, onDeleteChat, onRenameChat }) {
    const [editingId, setEditingId] = useState(null);
    const [editTitle, setEditTitle] = useState('');

    const handleStartEdit = (chat, e) => {
        e.stopPropagation();
        setEditingId(chat._id);
        setEditTitle(chat.title);
    };

    const handleSaveEdit = async (chatId) => {
        if (editTitle.trim()) {
            await onRenameChat(chatId, editTitle.trim());
        }
        setEditingId(null);
    };

    const handleKeyPress = (e, chatId) => {
        if (e.key === 'Enter') {
            handleSaveEdit(chatId);
        } else if (e.key === 'Escape') {
            setEditingId(null);
        }
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h1 className="app-title">NLP Assistant</h1>
                <button onClick={onNewChat} className="new-chat-button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    New Chat
                </button>
            </div>

            <div className="chats-list">
                {chats.map((chat) => (
                    <div
                        key={chat._id}
                        className={`chat-item ${activeChat === chat._id ? 'active' : ''}`}
                        onClick={() => onSelectChat(chat._id)}
                    >
                        <div className="chat-item-content">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                            </svg>

                            {editingId === chat._id ? (
                                <input
                                    type="text"
                                    value={editTitle}
                                    onChange={(e) => setEditTitle(e.target.value)}
                                    onBlur={() => handleSaveEdit(chat._id)}
                                    onKeyDown={(e) => handleKeyPress(e, chat._id)}
                                    onClick={(e) => e.stopPropagation()}
                                    className="chat-title-input"
                                    autoFocus
                                />
                            ) : (
                                <span className="chat-title">{chat.title}</span>
                            )}
                        </div>

                        <div className="chat-actions">
                            <button
                                onClick={(e) => handleStartEdit(chat, e)}
                                className="edit-button"
                                title="Rename chat"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                </svg>
                            </button>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDeleteChat(chat._id);
                                }}
                                className="delete-button"
                                title="Delete chat"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Sidebar;
