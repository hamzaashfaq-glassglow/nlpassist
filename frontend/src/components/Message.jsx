import './Message.css';

function Message({ message }) {
    const isUser = message.role === 'user';
    const metadata = message.metadata || {};
    const sources = metadata.sources || [];

    return (
        <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
            <div className="message-content">
                <div className="message-text">{message.content}</div>

                {!isUser && metadata.cached && (
                    <div className="message-badge cached-badge">
                        ⚡ Cached
                    </div>
                )}

                {!isUser && metadata.confidence === 'Low' && (
                    <div className="message-badge low-confidence-badge">
                        ⚠️ Low Confidence
                    </div>
                )}

                {!isUser && metadata.confidence === 'High' && (
                    <div className="message-badge high-confidence-badge">
                        ✓ High Confidence
                    </div>
                )}

                {!isUser && sources.length > 0 && (
                    <details className="message-sources">
                        <summary>📚 Sources ({sources.length})</summary>
                        <div className="sources-list">
                            {sources.map((source, index) => (
                                <div key={index} className="source-item">
                                    <span className="source-number">[{index + 1}]</span>
                                    <span className="source-text">{source}</span>
                                </div>
                            ))}
                        </div>
                    </details>
                )}
            </div>

            <div className="message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
            </div>
        </div>
    );
}

export default Message;
