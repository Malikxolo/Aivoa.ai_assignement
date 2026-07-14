import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // Form fields — all driven by AI, never by manual input
  hcp_name: '',
  interaction_type: 'Meeting',
  date: '',
  time: '',
  attendees: '',
  topics_discussed: '',
  materials_shared: '',
  samples_distributed: '',
  sentiment: '',
  outcomes: '',
  follow_up_actions: '',

  // Chat state
  messages: [],
  isLoading: false,
  error: null,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    // Set ALL form fields at once (for log_interaction)
    setInteractionFields(state, action) {
      const fields = action.payload;
      Object.keys(fields).forEach((key) => {
        if (key in state && key !== 'messages' && key !== 'isLoading' && key !== 'error') {
          state[key] = fields[key];
        }
      });
    },

    // Update ONLY specific fields (for edit_interaction)
    updateInteractionFields(state, action) {
      const fields = action.payload;
      Object.keys(fields).forEach((key) => {
        if (key in state && key !== 'messages' && key !== 'isLoading' && key !== 'error') {
          state[key] = fields[key];
        }
      });
    },

    // Chat message management
    addUserMessage(state, action) {
      state.messages.push({
        type: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },

    addAIMessage(state, action) {
      state.messages.push({
        type: 'ai',
        content: action.payload.message,
        toolUsed: action.payload.toolUsed || null,
        timestamp: new Date().toISOString(),
      });
    },

    setLoading(state, action) {
      state.isLoading = action.payload;
    },

    setError(state, action) {
      state.error = action.payload;
    },

    // Reset entire interaction
    resetInteraction() {
      return initialState;
    },
  },
});

export const {
  setInteractionFields,
  updateInteractionFields,
  addUserMessage,
  addAIMessage,
  setLoading,
  setError,
  resetInteraction,
} = interactionSlice.actions;

export default interactionSlice.reducer;
