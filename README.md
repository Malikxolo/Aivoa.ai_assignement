# AI-First CRM HCP Module

This project is an AI-first Customer Relationship Management (CRM) module specifically designed for Healthcare Professionals (HCP). It enables field representatives to effortlessly log their interactions with doctors via a structured form or a conversational AI chat interface, reducing administrative burden and providing intelligent coaching and scheduling capabilities.

## Features

- **Conversational Logging**: Simply describe a meeting in the chat, and the AI extracts the relevant data (HCP Name, Interaction Type, Topics, Date, Sentiment) to populate the CRM form instantly.
- **Interaction Editing**: Correct errors organically by chatting with the AI (e.g., "I actually distributed 3 samples, not 5"), and it updates only the relevant fields.
- **Smart Follow-up Suggestions**: Based on the sentiment and context of the meeting, the AI acts as a sales coach recommending next actions.
- **HCP History Retrieval**: Query past interactions using natural language or pronouns (e.g., "What did I discuss with him last time?").
- **Task Scheduling**: Schedule future follow-ups directly from the chat.
- **Out-of-Scope Handling**: The AI gracefully redirects generic chat requests back to CRM-specific workflows.

## Tech Stack

- **Frontend**: React, Redux (for state management), Vite.
- **Backend**: Python, FastAPI.
- **AI/Orchestration**: LangGraph, LangChain.
- **Database**: SQLite (SQLAlchemy) - lightweight and portable for immediate local testing.
- **LLM**: Groq (`gemma2-9b-it`).

## Project Structure

```
├── backend/                  # FastAPI & LangGraph backend
│   ├── main.py               # Application entry point
│   ├── database.py           # SQLAlchemy setup & models
│   ├── routes/               # API endpoints
│   ├── agent/                # LangGraph orchestration
│   │   ├── graph.py          # State machine, Router, and Nodes
│   │   └── tools/            # The 5 specific AI tools
│   └── requirements.txt      # Python dependencies
└── frontend/                 # React frontend
    ├── src/
    │   ├── api/              # API clients for communicating with backend
    │   ├── components/       # UI Components (ChatPanel, InteractionForm)
    │   ├── store/            # Redux store and slices
    │   └── App.jsx           # Main application shell
    └── package.json          # Node dependencies
```

## How to Run the Project

### Prerequisites

1. Python 3.10+
2. Node.js 18+
3. A Groq API Key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Create a `.env` file in the `backend/` directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=gemma2-9b-it
   ```
5. Start the backend server:
   ```bash
   python main.py
   ```
   *The FastAPI server will be available at `http://localhost:8000`.*

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

## LangGraph Architecture

The backbone of this AI assistant is built using **LangGraph**. A main router node classifies user inputs and explicitly routes them to one of five independent tool nodes. This strict State Machine approach guarantees that the agent remains hyper-focused on CRM tasks without hallucinating or triggering standard generic chat functions.

**The 5 defined tools are:**
1. `log_interaction`: Extracts fields to populate a new interaction.
2. `edit_interaction`: Modifies fields of the currently loaded interaction.
3. `generate_follow_ups`: Generates coaching advice based on recent interaction context.
4. `schedule_follow_up`: Analyzes date references to schedule actionable items.
5. `fetch_hcp_history`: Queries the SQLite DB to retrieve past interactions with specific HCPs.
