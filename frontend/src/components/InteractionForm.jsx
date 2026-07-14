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
import './InteractionForm.css';

export default function InteractionForm() {
  const interaction = useSelector((state) => state.interaction);
  const dispatch = useDispatch();

  const handleSuggestionClick = async (e, suggestionText) => {
    e.preventDefault();
    if (!interaction.hcp_name) {
      window.alert("Please fill the HCP Name in the form first, or specify the doctor's name in your message.");
      return;
    }
    
    // Check if chat is currently loading
    if (interaction.isLoading) return;

    dispatch(addUserMessage(suggestionText));
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      const response = await sendChatMessage(suggestionText);
      if (response.fields_updated) {
        if (response.tool_used === 'log_interaction') {
          dispatch(setInteractionFields(response.fields_updated));
        } else if (response.tool_used === 'edit_interaction') {
          dispatch(updateInteractionFields(response.fields_updated));
        }
      }
      if (response.tool_used === 'schedule_follow_up') {
        const alertMsg = response.message.replace(/[*📅]/g, '').trim();
        window.alert(alertMsg);
      }
      dispatch(addAIMessage({ message: response.message, toolUsed: response.tool_used }));
    } catch (err) {
      dispatch(setError(err.message));
      dispatch(addAIMessage({ message: `❌ Error: ${err.message}. Please try again.`, toolUsed: null }));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="interaction-form">
      <h1 className="form-title">Log HCP Interaction</h1>

      {/* Interaction Details Section */}
      <section className="form-section">
        <h3 className="section-label">Interaction Details</h3>

        <div className="field-row two-col">
          <div className="field-group">
            <label className="field-label">HCP Name</label>
            <input
              type="text"
              className="field-input"
              value={interaction.hcp_name}
              placeholder="Search or select HCP..."
              readOnly
              tabIndex={-1}
            />
          </div>
          <div className="field-group">
            <label className="field-label">Interaction Type</label>
            <div className="select-wrapper">
              <select
                className="field-select"
                value={interaction.interaction_type || 'Meeting'}
                disabled
                tabIndex={-1}
              >
                <option value="Meeting">Meeting</option>
                <option value="Call">Call</option>
                <option value="Email">Email</option>
                <option value="Video Call">Video Call</option>
              </select>
            </div>
          </div>
        </div>

        <div className="field-row two-col">
          <div className="field-group">
            <label className="field-label">Date</label>
            <input
              type="text"
              className="field-input date-input"
              value={interaction.date}
              placeholder="MM/DD/YYYY"
              readOnly
              tabIndex={-1}
            />
          </div>
          <div className="field-group">
            <label className="field-label">Time</label>
            <input
              type="text"
              className="field-input time-input"
              value={interaction.time || ''}
              placeholder="HH:MM AM/PM"
              readOnly
              tabIndex={-1}
            />
          </div>
        </div>
      </section>

      {/* Attendees */}
      <section className="form-section">
        <label className="field-label">Attendees</label>
        <input
          type="text"
          className="field-input"
          value={interaction.attendees}
          placeholder="Enter names or search..."
          readOnly
          tabIndex={-1}
        />
      </section>

      {/* Topics Discussed */}
      <section className="form-section">
        <label className="field-label">Topics Discussed</label>
        <textarea
          className="field-textarea"
          value={interaction.topics_discussed}
          placeholder="Enter key discussion points..."
          readOnly
          tabIndex={-1}
          rows={4}
        />
        <div className="voice-note-link">
          <span className="voice-icon">🎙</span>
          <a href="#" className="voice-link" onClick={(e) => e.preventDefault()}>
            Summarize from Voice Note (Requires Consent)
          </a>
        </div>
      </section>

      {/* Materials Shared / Samples Distributed */}
      <section className="form-section">
        <h3 className="section-label">Materials Shared / Samples Distributed</h3>

        <div className="sub-section">
          <label className="field-label">Materials Shared</label>
          <div className="materials-row">
            <span className="materials-value">
              {interaction.materials_shared || 'No materials added.'}
            </span>
            <button className="search-add-btn" disabled tabIndex={-1}>
              🔍 Search/Add
            </button>
          </div>
        </div>

        <div className="sub-section">
          <label className="field-label">Samples Distributed</label>
          <div className="materials-row">
            <span className="materials-value">
              {interaction.samples_distributed || 'No samples added.'}
            </span>
            <button className="add-sample-btn" disabled tabIndex={-1}>
              + Add Sample
            </button>
          </div>
        </div>
      </section>

      {/* Sentiment */}
      <section className="form-section">
        <label className="field-label">Observed/Inferred HCP Sentiment</label>
        <div className="sentiment-row">
          {['positive', 'neutral', 'negative'].map((s) => (
            <label key={s} className={`sentiment-option ${interaction.sentiment === s ? 'selected' : ''}`}>
              <input
                type="radio"
                name="sentiment"
                value={s}
                checked={interaction.sentiment === s}
                readOnly
                tabIndex={-1}
              />
              <span className="sentiment-emoji">
                {s === 'positive' ? '😊' : s === 'neutral' ? '😐' : '😞'}
              </span>
              <span className="sentiment-text">{s.charAt(0).toUpperCase() + s.slice(1)}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Outcomes */}
      <section className="form-section">
        <label className="field-label">Outcomes</label>
        <textarea
          className="field-textarea"
          value={interaction.outcomes}
          placeholder="Key outcomes or agreements..."
          readOnly
          tabIndex={-1}
          rows={3}
        />
      </section>

      {/* Follow-up Actions */}
      <section className="form-section">
        <label className="field-label">Follow-up Actions</label>
        <textarea
          className="field-textarea"
          value={interaction.follow_up_actions}
          placeholder="Scheduled follow-ups..."
          readOnly
          tabIndex={-1}
          rows={3}
        />
      </section>

      {/* AI Suggested Follow-ups */}
      <section className="form-section ai-suggestions-section">
        <label className="field-label" style={{ color: '#4a5568', fontWeight: 600 }}>
          AI Suggested Follow-ups:
        </label>
        <ul className="ai-suggestions-list">
          {['Schedule follow-up meeting in 2 weeks', 'Generate Follow up suggestion', 'View previous conversation history'].map((suggestion, index) => (
            <li key={index} className="ai-suggestion-item">
              <a 
                href="#" 
                className="ai-suggestion-link" 
                onClick={(e) => handleSuggestionClick(e, suggestion)}
              >
                + {suggestion}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
