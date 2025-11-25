import streamlit as st
import json
import os
import warnings
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv() # Load environment variables from .env file

# 1. SILENCE WARNINGS
warnings.filterwarnings("ignore", category=UserWarning, module='google.generativeai')
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except ImportError:
    pass

# 2. API SETUP
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Missing GOOGLE_API_KEY. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- FILE PATHS ---
PROFILE_FILE = "cognitive_profile.json"

# --- HELPER: HISTORY CONVERTER ---
def convert_history_to_gemini(messages):
    """
    Converts Streamlit format [{'role': 'user', 'content': '...'}]
    to Gemini format [{'role': 'user', 'parts': ['...']}]
    """
    gemini_history = []
    for msg in messages:
        # Map 'assistant' to 'model' for Gemini
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })
    return gemini_history

# --- AGENT 1: THE HISTORIAN (MEMORY) ---
class HistorianAgent:
    def __init__(self):
        self.profile = self._load_profile()

    def _load_profile(self):
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        return {"recurring_fallacies": {}, "core_beliefs": [], "struggle_history": []}

    def save_interaction(self, user_input, critic_analysis):
        detected_fallacy = critic_analysis.get("identified_fallacy")
        if detected_fallacy and detected_fallacy != "None":
            current_count = self.profile["recurring_fallacies"].get(detected_fallacy, 0)
            self.profile["recurring_fallacies"][detected_fallacy] = current_count + 1
        
        self.profile["struggle_history"].append({
            "timestamp": str(datetime.now()),
            "topic": user_input[:50] + "...",
            "fallacy": detected_fallacy,
            "strategy_used": critic_analysis.get("adversarial_strategy")
        })

        with open(PROFILE_FILE, "w") as f:
            json.dump(self.profile, f, indent=4)

    def get_context_summary(self):
        top_fallacies = sorted(self.profile["recurring_fallacies"].items(), key=lambda x: x[1], reverse=True)[:3]
        return f"User's top recurring cognitive weaknesses: {top_fallacies}. Challenge these specifically."

# --- AGENT 2: THE CRITIC (THE CHALLENGER) ---
def run_critic_agent(user_input, history_context):
    # UPDATED: Using 'gemini-2.5-flash'
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction="You are 'The Critic'. You analyze arguments for logical flaws. You output ONLY JSON."
    )

    prompt = f"""
    CONTEXT ON USER:
    {history_context}

    USER INPUT:
    "{user_input}"

    TASK:
    1. Identify logical fallacies or cognitive biases.
    2. Determine the 'Intellectual Struggle' strategy.
    3. Output PURE JSON.
    
    Output Schema:
    {{
        "identified_fallacy": "Name of fallacy or 'None'",
        "reasoning": "Brief explanation of flaws.",
        "adversarial_strategy": "Specific instruction for Socrates.",
        "thought_experiment_idea": "A hypothetical scenario to test consistency."
    }}
    """
    
    # Force JSON response type
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        return json.loads(response.text)
    except Exception as e:
        return {
            "identified_fallacy": "Error",
            "reasoning": f"Failed to parse JSON: {e}",
            "adversarial_strategy": "Ask for clarification",
            "thought_experiment_idea": "None"
        }

# --- AGENT 3: THE PERSONA (SOCRATES) ---
def run_socratic_agent(user_input, critic_analysis, chat_history):
    # UPDATED: Using 'gemini-2.5-flash'
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=f"""
        You are 'The Generative Socratic Dialogue Partner'. 
        
        CRITIC'S STRATEGY: {critic_analysis.get('adversarial_strategy')}
        THOUGHT EXPERIMENT: {critic_analysis.get('thought_experiment_idea')}
        REASONING: {critic_analysis.get('reasoning')}
        
        TONE:
        - Do NOT lecture.
        - Ask probing questions.
        - Your goal is 'Aporia' (puzzlement) in the user.
        """
    )

    gemini_history = convert_history_to_gemini(chat_history)
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(user_input)
    return response.text

# --- STREAMLIT UI ---
st.set_page_config(page_title="Socratic Gemini", layout="wide")

st.title("🧠 Socratic Partner (Powered by Gemini)")
st.markdown("*An Adversarial Cognitive Agent designed to challenge your premises.*")

if "historian" not in st.session_state:
    st.session_state.historian = HistorianAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: System Internals
with st.sidebar:
    st.header("System Internals")
    st.success("Connected to Gemini 2.5 Flash")
    critic_container = st.container()

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("State a belief or argument..."):
    # 1. User turn
    st.chat_message("user").markdown(prompt)
    
    # 2. Historian retrieves context
    history_context = st.session_state.historian.get_context_summary()

    # 3. The Critic Analyzes (Hidden Layer)
    with st.spinner("The Critic (Gemini 2.5 Flash) is analyzing your logic..."):
        critic_analysis = run_critic_agent(prompt, history_context)
    
    # Show Critic output
    with critic_container:
        st.subheader("🧐 Critic Analysis")
        st.json(critic_analysis)

    # 4. The Persona Responds
    with st.chat_message("assistant"):
        with st.spinner("Socrates is thinking..."):
            response_text = run_socratic_agent(prompt, critic_analysis, st.session_state.messages)
            st.markdown(response_text)
    
    # Save to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # 5. Historian updates profile
    st.session_state.historian.save_interaction(prompt, critic_analysis)