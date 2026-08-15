# 🎙️ Voice AI Financial Assistant — VoiceForBharat

A real-time **Financial Services Voice AI Agent** built during **10 Days of Voice Agents — VoiceForBharat Edition**.

The project combines **Murf Falcon, LiveKit, LLMs, Speech-to-Text, Twilio, persistent memory, tools, analytics, human escalation, and specialist handoffs** to create a more natural voice-first financial assistance experience.

## 🚀 What Does It Do?

The agent allows users to interact with a financial assistant through voice instead of relying only on traditional text-based interfaces.

Users can ask questions such as:

* "Am I eligible for this scheme?"
* "What documents do I need?"
* "Can you explain this in simple language?"
* "Can you help me with my request?"

The agent can understand the conversation, respond using voice, remember relevant information, use tools, and escalate when necessary.

## ✨ Key Features

### 🎙️ Voice AI

* Real-time voice conversations
* Speech-to-Text
* LLM-powered responses
* Text-to-Speech using **Murf Falcon**
* Indian-focused conversational experience

### 🧠 Persistent Memory

The agent can remember relevant user information across conversations using a database-backed memory layer.

### 🛠️ Agent Tools

The agent can call functions/tools when information needs to be retrieved or calculated rather than simply generated.

### 📞 Outbound Calling

Integrated **Twilio** to enable phone-based conversations with the voice agent.

### 👤 Human Escalation

The agent can recognize situations where human assistance may be more appropriate instead of attempting to answer everything itself.

### 🔄 Specialist Handoff

The architecture supports transferring conversations toward specialized agents for more specific tasks.

### 📊 Call Analytics

Call outcomes are tracked to help understand successful and unsuccessful interactions and improve the system.

### 🛡️ Guardrails

The agent has defined objectives, personality, financial-assistance boundaries, and conversation safety rules.

---

## 🏗️ Architecture

```text
                         USER
                           │
                           ▼
                    🎙️ Voice Input
                           │
                           ▼
                    Speech-to-Text
                           │
                           ▼
                    ┌──────────────┐
                    │   LiveKit    │
                    │ Voice Agent  │
                    └──────┬───────┘
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
                LLM            Memory / Tools
                  │                 │
                  └────────┬────────┘
                           ▼
                    Agent Response
                           │
                           ▼
                     Murf Falcon
                           │
                           ▼
                     🔊 Voice Output
                           │
                           ▼
                         USER
```

### Phone Architecture

```text
        User Phone
             │
             ▼
           Twilio
             │
             ▼
      LiveKit Voice Agent
             │
      ┌──────┼───────┐
      ▼      ▼       ▼
   Memory  Tools  Analytics
             │
             ▼
     Human / Specialist
       Escalation
```

---

## 🧰 Tech Stack

| Component      | Technology      |
| -------------- | --------------- |
| Voice AI       | LiveKit Agents  |
| Text-to-Speech | Murf Falcon     |
| LLM            | Google Gemini   |
| Speech-to-Text | Deepgram        |
| Telephony      | Twilio          |
| Backend        | Python          |
| Memory         | SQLite          |
| Frontend       | Next.js / React |
| Styling        | Tailwind CSS    |
| Environment    | `.env.local`    |

---

## 📂 Project Structure

```text
murf-livekit-starter/
│
├── backend/
│   ├── src/
│   │   ├── agent.py
│   │   └── memory.py
│   ├── .env.local
│   └── ...
│
├── frontend/
│   ├── components/
│   │   └── app/
│   └── ...
│
└── README.md
```

> **Note:** API keys and private credentials are intentionally not included in this repository.

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd murf-livekit-starter
```

### 2. Configure environment variables

Create:

```text
backend/.env.local
```

Add your credentials:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
MURF_API_KEY=your_murf_api_key

# Add other required service credentials
# according to your configuration
```

**Never commit API keys, phone numbers, caller data, or other private credentials.**

Make sure `.env.local` is included in `.gitignore`.

### 3. Start the backend

```bash
cd backend
uv run python src/agent.py dev
```

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
pnpm dev
```

Then open the local frontend in your browser and start a voice session.

---

## 🧪 Testing

After starting both services:

1. Open the frontend.
2. Allow microphone permissions.
3. Start the voice session.
4. Ask the financial assistant a question.
5. Test memory with a returning-user conversation.
6. Test available tools.
7. Test phone functionality separately if Twilio is configured.
8. Check call outcomes and analytics.

---

## 🔐 Security

Do **not** commit:

```text
.env
.env.local
API keys
Twilio credentials
Phone numbers
Caller information
Database files containing private user data
```

Use environment variables for secrets and keep sensitive data out of the public repository.

---

## 🧩 Challenges I Faced

Building the agent involved several real-world debugging challenges:

* LiveKit authentication and connection issues
* Microphone and browser permission problems
* Multilingual voice behavior
* Python errors and backend debugging
* Frontend integration issues
* Twilio authentication and call configuration
* Connecting browser voice and phone-based communication
* Making memory and analytics work reliably

The biggest lesson was to debug the system **layer by layer** instead of treating the entire voice agent as one component.

---

## 📈 Future Improvements

* Better Hindi and code-mixed conversations
* Lower response latency
* More financial-service tools
* Improved specialist routing
* More detailed analytics
* Better automated testing
* Improved failure recovery
* Production deployment
* More robust multilingual support

---

## 🏆 10 Days of Voice Agents

This project was built as part of:

**10 Days of Voice Agents — VoiceForBharat Edition**

The challenge helped me understand how a simple voice interaction can evolve into a complete AI agent capable of:

**Listening → Reasoning → Remembering → Acting → Calling → Escalating → Tracking**

---

## 🔗 Links

**GitHub:** url_added

**Blog:** [Add your published blog URL]

**LinkedIn:** [Add your LinkedIn post URL]

---

## 🙌 Acknowledgements

Built with:

* **Murf Falcon**
* **LiveKit**
* **Google Gemini**
* **Deepgram**
* **Twilio**

Special thanks to **Murf AI** for the VoiceForBharat challenge.

#VoiceForBharat #MurfAI #MurfFalcon #VoiceAI #AIAgents #LiveKit
