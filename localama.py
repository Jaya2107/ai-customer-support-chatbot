# -----------------------------------
# Imports
# -----------------------------------
import streamlit as st
import sqlite3
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain.schema import StrOutputParser

# -----------------------------------
# Company Contact Info (generic placeholders)
# -----------------------------------
support_link = "https://www.ourcompany.com/contact"
support_email = "support@ourcompany.com"
support_location = "Surat, Gujarat"

# -----------------------------------
# Database Setup
# -----------------------------------
def init_db():
    """Initialize SQLite database."""
    try:
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
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
    finally:
        conn.close()


def save_message(role, content):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO conversations (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()


def clear_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()


def load_all_history():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM conversations ORDER BY id ASC")
    history = c.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in history]


# Initialize database
init_db()

# -----------------------------------
# Company Info
# -----------------------------------
company_info = """
Company (E-Commerce) Policies:
* Order cancellation & refunds: If an order is cancelled or returned, payments are refunded within 5-7 business days after seller confirms return.
* Return window: Customers can return most products within 7 days of delivery (some categories may vary).
* Refund processing: Refunds typically take 2-10 business days after return is received.
* Free shipping: Free standard shipping for orders above a threshold (e.g. ₹500 or as per company rules).
* Replacement / defective items: If product is damaged, defective, or wrong item delivered, customer can request replacement within 7 days.
* Return conditions: Returned item should be unused, in original packaging with accessories.
* Non-returnable items: Some products (e.g. clearance, final sale, perishable) may be non-returnable as per policy.
"""

# -----------------------------------
# Streamlit UI Setup
# -----------------------------------
st.set_page_config(page_title="AI Customer Support Bot")
st.title("🤖 AI Customer Support Bot")

tab1, tab2 = st.tabs(["💬 Chat", "📜 Past Conversations"])

# -----------------------------------
# TAB 1: Chat Interface
# -----------------------------------
with tab1:
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.button("🧹 Clear Current Chat"):
        st.session_state.history = []
        st.rerun()

    user_input = st.text_input("💬 Ask your query:")

    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        save_message("user", user_input)

        # LLM Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI Customer Support Assistant for an e-commerce company named OurCompany. Use the provided company policies to answer user queries politely, clearly, and professionally."),
            ("user", "Company Policies:\n" + company_info),
            ("user", "User Query: {question}")
        ])

        llm = Ollama(model="llama3.2:1b")
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        response = chain.invoke({"question": user_input})

        # -----------------------------------
        # Escalation Condition (Smart Detection)
        # -----------------------------------
        response_lower = response.lower()
        vague_phrases = ["i don't know", "not sure", "can't help", "sorry, i can't", "no idea"]
        policy_keywords = ["refund", "return", "shipping", "replacement", "order", "delivery"]

        is_vague = any(phrase in response_lower for phrase in vague_phrases)
        has_keywords = any(keyword in response_lower for keyword in policy_keywords)

        if is_vague or (len(response) < 30 and not has_keywords):
            escalation_msg = (
                f"I can't provide you with the personal contact information of our manager. "
                f"If you'd like to speak with someone, please try the following options:\n\n"
                f"• 🌐 **Website Contact Page:** [Click here]({support_link})\n"
                f"• 📧 **Customer Support Email:** {support_email}\n"
                f"• 📍 **Visit Us:** {support_location}\n\n"
                f"Would you like more details about our contact form or visiting hours?"
            )
            st.session_state.history.append({"role": "assistant", "content": escalation_msg})
            save_message("assistant", escalation_msg)
        else:
            # Replace accidental placeholder mismatches in model outputs
            response = response.replace("support@yourcompany.com", support_email)
            response = response.replace("support@example-ecommerce.com", support_email)
            response = response.replace("Example Plaza", support_location)
            response = response.replace("[insert location]", support_location)
            response = response.replace("yourcompany.com", "ourcompany.com")
            response = response.replace("example-ecommerce.com", "ourcompany.com")

            st.session_state.history.append({"role": "assistant", "content": response})
            save_message("assistant", response)

    # Display Chat
    st.markdown("### 🗨️ Current Chat")
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Bot:** {msg['content']}")

# -----------------------------------
# TAB 2: Past Conversations
# -----------------------------------
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
