import { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  addUserMessage,
  addAIMessage,
  setInteractionFields,
  updateInteractionFields,
  setLoading,
  setError,
} from '../store/interactionSlice';
import { sendChatMessage } from '../api/chatApi';
import ChatMessage from './ChatMessage';
import './ChatPanel.css';

export default function ChatPanel() {
  const [input, setInput] = useState('');
  const dispatch = useDispatch();
  const { messages, isLoading } = useSelector((state) => state.interaction);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    // Add user message to Redux
    dispatch(addUserMessage(trimmed));
    setInput('');
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      // Call backend → LangGraph agent
      const response = await sendChatMessage(trimmed);

      // Update form fields based on tool used
      if (response.fields_updated) {
        if (response.tool_used === 'log_interaction') {
          dispatch(setInteractionFields(response.fields_updated));
        } else if (response.tool_used === 'edit_interaction') {
          dispatch(updateInteractionFields(response.fields_updated));
        }
      }

      // Check if it's the schedule meeting tool
      if (response.tool_used === 'schedule_follow_up') {
        const alertMsg = response.message.replace(/[*📅]/g, '').trim();
        window.alert(alertMsg);
      }

      // Add AI response message
      dispatch(
        addAIMessage({
          message: response.message,
          toolUsed: response.tool_used,
        })
      );
    } catch (err) {
      dispatch(setError(err.message));
      dispatch(
        addAIMessage({
          message: `❌ Error: ${err.message}. Please try again.`,
          toolUsed: null,
        })
      );
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-icon">🤖</div>
        <div className="chat-header-text">
          <h2 className="chat-header-title">AI Assistant</h2>
          <p className="chat-header-subtitle">Log Interaction details here via chat</p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {/* Onboarding hint */}
        <div className="chat-hint">
          <p>
            Log interaction details here (e.g., "Met Dr. Smith, discussed
            Prodo-X efficacy, positive sentiment, shared brochure") or ask
            for help.
          </p>
        </div>

        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}

        {isLoading && (
          <div className="chat-message ai-message">
            <div className="message-bubble typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe Interaction..."
          disabled={isLoading}
        />
        <button
          className="chat-send-btn"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
        >
          <span className="send-btn-icon">A</span>
          <span className="send-btn-label">Log</span>
        </button>
      </div>
    </div>
  );
}
