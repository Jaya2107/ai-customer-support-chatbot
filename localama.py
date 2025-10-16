
import streamlit as st
import requests
import sqlite3

# Backend API URL (FastAPI server)

BACKEND_URL = "http://127.0.0.1:8000/ask"


# Database Setup

def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO conversations (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def load_all_history():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM conversations ORDER BY id ASC")
    history = c.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in history]

def clear_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()

# Initialize DB
init_db()


# Streamlit UI

st.set_page_config(page_title="AI Customer Support Bot")
st.title("🤖 AI Customer Support Bot")

tab1, tab2 = st.tabs(["💬 Chat", "📜 Past Conversations"])


# Chat Tab

with tab1:
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.button("🧹 Clear Current Chat"):
        st.session_state.history = []
        st.rerun()

    user_input = st.text_input("💬 Ask your query:")

    if user_input:
        # Save user message
        st.session_state.history.append({"role": "user", "content": user_input})
        save_message("user", user_input)

        try:
            # Send query to backend API
            response = requests.post(BACKEND_URL, json={"question": user_input})
            if response.status_code == 200:
                answer = response.json().get("answer", "No response from AI.")
            else:
                answer = "⚠️ Backend error: Unable to fetch response."
        except Exception as e:
            answer = f"❌ Connection error: {e}"

        # Save bot response
        st.session_state.history.append({"role": "assistant", "content": answer})
        save_message("assistant", answer)

    # Display chat
    st.markdown("### 🗨️ Current Chat")
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Bot:** {msg['content']}")


# History Tab

with tab2:
    st.markdown("### 📜 Chat History from Database")
    all_history = load_all_history()
    if not all_history:
        st.info("No saved conversations yet.")
    else:
        for i, msg in enumerate(all_history, start=1):
            if msg["role"] == "user":
                st.markdown(f"**{i}. 🧑 You:** {msg['content']}")
            else:
                st.markdown(f"**{i}. 🤖 Bot:** {msg['content']}")

    if st.button("🗑️ Clear All Saved Conversations"):
        clear_db()
        st.success("All saved conversations deleted!")
        st.rerun()
