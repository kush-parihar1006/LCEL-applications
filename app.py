import os
import streamlit as st
from dotenv import load_dotenv

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="🌿 Plant-Based Diet Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

/* Background */
.stApp { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #f0fdf4 100%); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14532d 0%, #166534 60%, #15803d 100%);
    color: white;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: white !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.6) !important; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #166534 0%, #15803d 50%, #16a34a 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 40px rgba(22,101,52,0.25);
}
.hero-banner h1 { color: white; font-size: 2.4rem; font-weight: 800; margin: 0; }
.hero-banner p  { color: #bbf7d0; font-size: 1.05rem; margin: 0.5rem 0 0; }

/* Chat bubbles */
.chat-bubble {
    display: flex;
    gap: 12px;
    margin-bottom: 1rem;
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.chat-bubble.user  { flex-direction: row-reverse; }
.chat-bubble .avatar {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0;
}
.chat-bubble.user  .avatar { background: #16a34a; }
.chat-bubble.bot   .avatar { background: #14532d; }

.bubble-text {
    max-width: 75%; padding: 0.8rem 1.1rem;
    border-radius: 18px; line-height: 1.6; font-size: 0.95rem;
}
.chat-bubble.user .bubble-text {
    background: #16a34a; color: white;
    border-bottom-right-radius: 4px;
}
.chat-bubble.bot .bubble-text {
    background: white; color: #1a2e1a;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border: 1px solid #dcfce7;
}

/* Suggestions */
.suggestion-btn {
    display: inline-block; background: white; border: 2px solid #16a34a;
    color: #166534; border-radius: 20px; padding: 0.4rem 1rem;
    font-size: 0.85rem; font-weight: 600; cursor: pointer; margin: 4px;
    transition: all 0.2s;
}
.suggestion-btn:hover { background: #16a34a; color: white; }

/* Info cards */
.info-card {
    background: white; border-radius: 14px; padding: 1.2rem;
    border-left: 4px solid #16a34a;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 0.8rem;
}
.info-card h4 { color: #166534; margin: 0 0 0.4rem; font-size: 1rem; }
.info-card p  { color: #555; margin: 0; font-size: 0.88rem; }

/* Input area */
.stTextInput > div > div > input {
    border-radius: 30px !important;
    border: 2px solid #16a34a !important;
    padding: 0.7rem 1.2rem !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus { box-shadow: 0 0 0 3px rgba(22,163,74,0.2) !important; }

/* Buttons */
.stButton > button {
    border-radius: 30px !important;
    background: linear-gradient(135deg, #166534, #16a34a) !important;
    color: white !important; font-weight: 700 !important;
    border: none !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(22,163,74,0.3) !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(22,163,74,0.4) !important; }

/* Status badge */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #dcfce7; color: #166534;
    border-radius: 20px; padding: 4px 12px; font-size: 0.82rem; font-weight: 700;
}
.status-dot { width: 8px; height: 8px; background: #16a34a; border-radius: 50%; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Hide streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────────
for key, val in {
    "messages": [],
    "session_id": "session_001",
    "chain_ready": False,
    "chain": None,
    "groq_key": "",
    "hf_token": "",
    "suggestion_clicked": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── RAG chain builder (cached) ─────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def build_chain(groq_api_key: str, hf_token: str):
    groq_api_key = os.getenv("GROQ_API_KEY")
    os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")
    from langchain_groq import ChatGroq
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from langchain_community.document_loaders import WebBaseLoader
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.chat_history import InMemoryChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory

    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    loader = WebBaseLoader(web_paths=("https://www.healthline.com/nutrition/plant-based-diet-guide",))
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever()

    system_prompt = (
        "You are a friendly and knowledgeable plant-based diet assistant. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer from the context, say so honestly. "
        "Keep answers helpful, clear, and encouraging. Use 3–5 sentences maximum.\n\n"
        "{context}"
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Given a chat history and the latest user question which might reference "
         "context in the chat history, formulate a standalone question which can be "
         "understood without the chat history. Do NOT answer it — just reformulate if "
         "needed, otherwise return as is."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

    def contextualized_question(inp: dict):
        if inp.get("chat_history"):
            return contextualize_q_chain
        return inp["input"]

    history_aware_retriever = RunnableLambda(contextualized_question) | retriever

    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(x["context"]))
        | qa_prompt | llm | StrOutputParser()
    )

    rag_chain = RunnablePassthrough.assign(
        context=history_aware_retriever
    ).assign(answer=question_answer_chain)

    store: dict = {}

    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_chain


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Configuration")
    st.markdown("---")

    groq_key = st.text_input("🔑 Groq API Key", type="password",
                             value=st.session_state.groq_key,
                             placeholder="gsk_...")
    hf_token = st.text_input("🤗 HuggingFace Token", type="password",
                              value=st.session_state.hf_token,
                              placeholder="hf_...")

    if groq_key: st.session_state.groq_key = groq_key
    if hf_token: st.session_state.hf_token = hf_token

    st.markdown("---")
    init_btn = st.button("🚀 Initialize Bot", use_container_width=True)
    if init_btn:
        if not st.session_state.groq_key or not st.session_state.hf_token:
            st.error("Please enter both API keys.")
        else:
            with st.spinner("Loading knowledge base…"):
                try:
                    chain = build_chain(st.session_state.groq_key, st.session_state.hf_token)
                    st.session_state.chain = chain
                    st.session_state.chain_ready = True
                    st.success("✅ Bot is ready!")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    if st.session_state.chain_ready:
        st.markdown('<div class="status-badge"><span class="status-dot"></span>Bot Active</div>', unsafe_allow_html=True)
    else:
        st.markdown("⚪ **Bot Inactive**")

    st.markdown("---")
    st.markdown("### 📚 Knowledge Source")
    st.markdown("Powered by [Healthline's Plant-Based Diet Guide](https://www.healthline.com/nutrition/plant-based-diet-guide)")

    st.markdown("### 🤖 Model")
    st.markdown("**Llama 3.1 8B** via Groq  \n**all-MiniLM-L6-v2** embeddings")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"session_{len(st.session_state.messages)}"
        st.rerun()

    st.markdown("---")
    st.markdown("### 🌱 Quick Tips")
    tips = ["🥦 Focus on whole foods", "🍎 Eat the rainbow", "💧 Stay hydrated", "🌾 Include whole grains"]
    for tip in tips:
        st.markdown(f"<small>{tip}</small>", unsafe_allow_html=True)


# ── Main content ───────────────────────────────────────────────────────────────
# Hero
st.markdown("""
<div class="hero-banner">
  <h1>🌱 Plant-Based Diet Assistant</h1>
  <p>Your AI-powered guide to a healthier, plant-forward lifestyle</p>
</div>
""", unsafe_allow_html=True)

# Top info cards
if not st.session_state.chain_ready:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="info-card">
          <h4>🥗 What I Can Help With</h4>
          <p>Meal planning, nutrition advice, food choices, health benefits, and tips for starting a plant-based diet.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
          <h4>🔬 RAG-Powered Answers</h4>
          <p>Answers are grounded in curated dietary science content — not just general knowledge.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="info-card">
          <h4>💬 Conversational Memory</h4>
          <p>Ask follow-up questions naturally — the bot remembers your conversation context.</p>
        </div>""", unsafe_allow_html=True)

    st.info("👈 Enter your API keys in the sidebar and click **Initialize Bot** to get started.")

# ── Chat area ──────────────────────────────────────────────────────────────────
if st.session_state.chain_ready:
    chat_container = st.container()

    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="chat-bubble bot">
              <div class="avatar">🌿</div>
              <div class="bubble-text">
                Hello! I'm your plant-based diet assistant. 🌱 Ask me anything about plant-based eating —
                from what foods to eat, to health benefits, meal ideas, and more!
              </div>
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"""
                <div class="chat-bubble user">
                  <div class="avatar">🙋</div>
                  <div class="bubble-text">{content}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble bot">
                  <div class="avatar">🌿</div>
                  <div class="bubble-text">{content}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Suggestion chips
    suggestions = [
        "What is a plant-based diet?",
        "What are the health benefits?",
        "What should I eat for breakfast?",
        "How do I get enough protein?",
        "Can I lose weight on a plant-based diet?",
        "What foods should I avoid?",
    ]
    st.markdown("**💡 Quick Questions:**")
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}"):
                st.session_state.suggestion_clicked = suggestion
                st.rerun()

    st.markdown("---")

    # Input
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Ask your question…",
            value=st.session_state.suggestion_clicked,
            key="user_input",
            label_visibility="collapsed",
            placeholder="e.g. What are the best protein sources on a plant-based diet?"
        )
    with col_send:
        send = st.button("Send ➤", use_container_width=True)

    # Handle input
    query = None
    if send and user_input.strip():
        query = user_input.strip()
    elif st.session_state.suggestion_clicked and not send:
        pass  # wait for send
    if st.session_state.suggestion_clicked and send:
        query = st.session_state.suggestion_clicked
        st.session_state.suggestion_clicked = ""

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.spinner("🌿 Thinking…"):
            try:
                result = st.session_state.chain.invoke(
                    {"input": query},
                    config={"configurable": {"session_id": st.session_state.session_id}}
                )
                answer = result.get("answer", "Sorry, I couldn't generate a response.")
            except Exception as e:
                answer = f"⚠️ Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
