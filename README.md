# Social-to-Lead Agentic Workflow

An intelligent sales assistant designed to convert social media interest into qualified leads. This project uses a state-of-the-art agentic workflow powered by LangGraph to handle user greetings, provide product information via RAG (Retrieval-Augmented Generation), and capture lead details in a conversational manner.

## 🚀 Architecture Explanation

The core of this system is built on **LangGraph**, which provides a state-machine approach to agentic orchestration. Unlike traditional linear LLM chains, LangGraph allows for **cyclic workflows**, which is critical for a "Social-to-Lead" assistant. For example, if a user expresses high intent but provides an incomplete lead (e.g., missing an email), the agent can circle back to the "Lead Collector" node until all required fields are extracted.

**State Management** is handled via a `AppState` TypedDict that tracks the conversation history (`messages`) and specific lead attributes (`name`, `email`, `platform`). Persistence is achieved using LangGraph's `MemorySaver` (Checkpointer). This allows the system to support persistent user sessions (mapped to a `session_id`) where the agent "remembers" the current extraction progress even if the conversation is interrupted. Each node in the graph (Classify, Extract, Greeting, RAG, Lead Collector) communicates by updating this shared state, and conditional edges guide the conversation flow based on the extracted data.

## 🛠️ Local Setup

### Backend (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or source venv/bin/activate # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend` folder (already present if cloned):
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
5. Run the server:
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:8000`.

### Frontend (Vite + React)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

## 📱 WhatsApp Deployment (Webhooks)

Integrating this agent with WhatsApp allows you to automate lead capture directly from chat. Here is how you can deploy it using a Webhook architecture and the **Meta Cloud API (WhatsApp)**:

1.  **Configure WhatsApp Business**: Set up a developer account on [Meta for Developers](https://developers.facebook.com/) and create a WhatsApp Business app.
2.  **Expose Local Server**: Use a tool like `ngrok` to expose your local FastAPI server to the internet:
    ```bash
    ngrok http 8000
    ```
3.  **Setup Webhook Endpoint**: Create a new endpoint in `backend/app.py` (e.g., `POST /whatsapp/webhook`) to handle incoming messages from Meta.
4.  **Verify Webhook**: In the Meta App Dashboard, add your Ngrok URL as the Webhook URL. Meta will send a verification challenge to your GET endpoint which you must return.
5.  **Process Messages**:
    *   When a user sends a message, Meta sends an HTTP POST with the message JSON.
    *   Extract the user's phone number (sender ID) and message text.
    *   Pass the sender ID as the `session_id` to the LangGraph agent to maintain per-user state.
    *   Invoke the agent and get the `final_output`.
6.  **Send Reply**: Use the **WhatsApp Send API** to push the agent's response back to the user's phone number.
