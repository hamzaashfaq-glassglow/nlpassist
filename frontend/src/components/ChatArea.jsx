import { useEffect, useRef } from 'react';
import Message from './Message';
import MessageInput from './MessageInput';
import './ChatArea.css';

function ChatArea({ messages, onSendMessage, isLoading, loadingState }) {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    return (
        <div className="chat-area">
            <div className="messages-container">
                {messages.length === 0 && !isLoading && (
                    <div className="empty-state">
                        <div className="empty-icon">💬</div>
                        <h2>NLP Assistant</h2>
                        <p>Ask me anything about the documents!</p>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <Message key={index} message={msg} />
                ))}

                {isLoading && (
                    <div className="loading-message">
                        <div className="loading-content">
                            <div className="loading-spinner"></div>
                            <span className="loading-text">
                                {loadingState === 'thinking' ? '🤔 Thinking...' : '✍️ Generating...'}
                            </span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <MessageInput onSendMessage={onSendMessage} disabled={isLoading} />
        </div>
    );
}

export default ChatArea;
