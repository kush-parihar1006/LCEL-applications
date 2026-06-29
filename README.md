# 🌱 Plant-Based Diet Assistant — Streamlit App

An AI-powered conversational Q&A chatbot for plant-based diet guidance, built with Streamlit, LangChain, Groq, and HuggingFace.

## Features
- 💬 **Conversational memory** — follow-up questions work naturally
- 🔍 **RAG (Retrieval-Augmented Generation)** — answers grounded in Healthline's plant-based diet guide
- 💡 **Quick suggestion chips** — one-click starter questions
- 🎨 **Beautiful green-themed UI** — custom CSS chat bubbles and hero banner
- ⚡ **Fast inference** via Groq (Llama 3.1 8B)

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API keys
- **Groq API Key**: https://console.groq.com/
- **HuggingFace Token**: https://huggingface.co/settings/tokens

### 3. (Optional) Create a `.env` file
```
GROQ_API_KEY=gsk_...
HF_TOKEN=hf_...
```

### 4. Run the app
```bash
streamlit run app.py
```

## Usage
1. Enter your Groq API key and HuggingFace token in the sidebar
2. Click **Initialize Bot** — the knowledge base will be built (takes ~30 seconds)
3. Ask questions using the chat input or the quick suggestion chips
4. The bot remembers your conversation history for natural follow-ups

## Architecture
```
User Question
    │
    ▼
History-Aware Question Reformulation (LLM)
    │
    ▼
Vector Retrieval (Chroma + MiniLM embeddings)
    │
    ▼
Context-Grounded Answer Generation (Llama 3.1 8B via Groq)
    │
    ▼
Streamlit Chat UI
```
