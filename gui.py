
import streamlit as st
import asyncio
import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from core.system import AegisSystem

# --- CONFIG ---
st.set_page_config(
    page_title="Aegis V",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLES (ChatGPT-like Dark Theme) ---
st.markdown("""
    <style>
    /* --- CSS VARIABLES --- */
    :root {
        --bg-color: #343541;
        --sidebar-bg: #202123;
        --user-msg-bg: #343541;
        --bot-msg-bg: #444654;
        --text-color: #ECECF1;
        --border-color: #565869;
        --input-bg: #40414F;
    }

    /* --- MAIN LAYOUT --- */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    /* Hide Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- CHAT MESSAGES --- */
    /* Enhance the container for messages */
    .stChatMessage {
        background-color: transparent;
        border: none; 
    }

    /* Streamlit puts the content in a div with data-testid="stChatMessage" */
    div[data-testid="stChatMessage"] {
        padding: 1.5rem 1rem;
        border-bottom: 1px solid #2d2f3c;
        margin: 0;
        width: 100%;
        max-width: 100%;
    }
    
    /* Alternating backgrounds for that chat-app feel */
    /* Note: Streamlit structure changes often, but targeting even/odd usually works for the list */
    div[data-testid="stChatMessage"]:nth-of-type(odd) {
        background-color: var(--bot-msg-bg);
    }
    div[data-testid="stChatMessage"]:nth-of-type(even) {
        background-color: var(--user-msg-bg);
    }
    
    /* Avatar Styling */
    div[data-testid="stChatMessageAvatar"] {
        background-color: transparent;
        border: none;
        margin-right: 1rem;
    }
    div[data-testid="stChatMessageAvatar"] img {
        width: 32px;
        height: 32px;
        border-radius: 4px;
    }

    /* --- INPUT AREA --- */
    .stChatInput {
        padding-bottom: 3rem;
        max-width: 800px;
        margin: auto;
    }
    .stChatInput textarea {
        background-color: var(--input-bg) !important;
        color: white !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* --- HERO SECTION --- */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
        color: var(--text-color);
    }
    .hero-title {
        font-family: 'Söhne', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #C5C5D2;
        margin-bottom: 3rem;
    }
    
    /* --- INFO CARDS (Hero) --- */
    div.stInfo {
        background-color: #3E3F4B;
        border: 1px solid #565869;
        color: #ECECF1;
    }

    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid #4d4d4f;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        border: 1px solid #565869;
        padding: 10px;
        border-radius: 5px;
        background-color: #40414F;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        background: #202123;
    }
    ::-webkit-scrollbar-thumb {
        background: #565869;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if "aegis" not in st.session_state:
    st.session_state.aegis = AegisSystem()
    st.session_state.messages = []
    st.session_state.last_metrics = {
        "l1_dist": 0.0,
        "l2_score": 0,
        "stage": "IDLE",
        "latency": 0.0,
        "antibodies": len(st.session_state.aegis.layer1.vectors)
    }

# --- SIDEBAR: SYSTEM CONTEXT ---
with st.sidebar:
    st.title("🛡️ System Telemetry")
    
    # Status Indicator
    status_label = st.session_state.last_metrics["stage"]
    s_color = "green" if "BLOCKED" not in status_label else "red"
    st.markdown(f"**Status**: :{s_color}[{status_label}]")
    
    st.divider()
    
    # Layer 1 Data
    st.caption("Layer 1: Cognitive Membrane")
    col1, col2 = st.columns(2)
    col1.metric("Distance", f"{st.session_state.last_metrics['l1_dist']:.3f}")
    col2.metric("Antibodies", st.session_state.last_metrics["antibodies"])
    
    # Layer 2 Data
    st.caption("Layer 2: Intent Tracker")
    risk = st.session_state.last_metrics["l2_score"]
    st.metric("Risk Score", f"{risk}/100", delta=None, help="Over 70 is blocked")
    
    st.divider()
    
    if st.button("🗑️ New Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.aegis.reset_state()
        st.rerun()

# --- MAIN CHAT UI ---

# Hero Screen if empty
if not st.session_state.messages:
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Aegis V</div>
            <div class="hero-subtitle">Self-Hardening Adaptive Defense System</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered cards
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.info("**Layer 1**\n\nSemantic Membrane\n(Vector Similarity)")
    with c2:
        st.info("**Layer 2**\n\nIntent Analysis\n(LLM Reasoning)")
    with c3:
        st.info("**Layer 3**\n\nSelf-Immunization\n(Memory Injection)")

# Chat History
for msg in st.session_state.messages:
    avatar = "🛡️" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input Handling
if prompt := st.chat_input("Send a message..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Aegis Processing
    with st.chat_message("assistant", avatar="🛡️"):
        status_placeholder = st.status("Initializing Defense Protocols...", expanded=False)
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # A. Security Checks (Async)
            with status_placeholder:
                st.write("🔄 **Layer 1**: Scanning Vector Space...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(st.session_state.aegis.process_prompt(prompt))
                loop.close()
                
                # Visual Feedback for Checks
                if result["l1_safe"]:
                    st.write(f"✅ **Layer 1**: Safe (Dist: {result['l1_dist']:.4f})")
                else:
                    st.write(f"❌ **Layer 1**: BLOCKED ({result['block_reason']})")
                    status_placeholder.update(label="Security Violation Detected", state="error", expanded=True)
                
                if result["stage"] != "BLOCKED_L1":
                    st.write("🔄 **Layer 2**: Analyzing Intent...")
                    if result["l2_safe"]:
                        st.write(f"✅ **Layer 2**: Safe (Risk: {result['l2_score']})")
                    else:
                        st.write(f"❌ **Layer 2**: BLOCKED ({result['block_reason']})")
                        status_placeholder.update(label="Unsafe Intent Detected", state="error", expanded=True)

            # B. Response Generation (Stream or Static)
            if result["stage"] == "SUCCESS":
                status_placeholder.update(label="Verified Safe", state="complete", expanded=False)
                
                # Consume Stream
                if "response_generator" in result:
                    # Streamlit write_stream helper (or manual loop)
                    def stream_generator():
                        for chunk in result["response_generator"]:
                            content = chunk['message']['content']
                            yield content
                    
                    full_response = st.write_stream(stream_generator)
                else:
                    # Fallback for static (shouldn't happen with new core)
                    full_response = result["response"]
                    st.markdown(full_response)
            
            else:
                # Blocked Response
                full_response = result["response"]
                st.markdown(full_response)

            # Save to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # C. Update Telemetry
            st.session_state.last_metrics = {
                "l1_dist": result.get("l1_dist", 0.0),
                "l2_score": result.get("l2_score", 0),
                "stage": result.get("stage", "ERR"),
                "latency": result.get("latency_ms", 0),
                "antibodies": len(st.session_state.aegis.layer1.vectors)
            }
            
        except Exception as e:
            st.error(f"System Error: {e}")
            
    # Refresh sidebar metrics (lazy update)
    st.rerun()
