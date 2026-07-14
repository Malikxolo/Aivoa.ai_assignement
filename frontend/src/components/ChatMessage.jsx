import './ChatMessage.css';

export default function ChatMessage({ message }) {
  const isUser = message.type === 'user';

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}>
      <div className="message-bubble">
        <span
          className="message-content"
          dangerouslySetInnerHTML={{
            __html: message.content
              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
              .replace(/\n/g, '<br/>'),
          }}
        />
      </div>
    </div>
  );
}
