const API_BASE = 'http://localhost:8000/api';

export async function sendChatMessage(message, interactionId = null) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      interaction_id: interactionId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

export async function resetInteractionAPI() {
  const response = await fetch(`${API_BASE}/reset`, {
    method: 'POST',
  });
  return response.json();
}
