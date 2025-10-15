from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st

# Company info (using Flipkart + Meesho policy snippets)
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

st.set_page_config(page_title="AI Customer Support Bot")

st.title("AI Customer Support Bot")

# Maintain chat history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask your query:")

if user_input:
    # add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})

    # Build prompt template for each query
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Customer Support Assistant for an e-commerce company. Use the provided company policies to answer user queries in a polite, professional, and clear manner."),
        ("user", "Company Policies:\n" + company_info),
        ("user", "User Query: {question}")
    ])

    llm = Ollama(model="llama3.2:1b")
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Invoke model
    response = chain.invoke({"question": user_input})
    st.session_state.history.append({"role": "assistant", "content": response})

# Display chat
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"*You:* {msg['content']}")
    else:
        st.markdown(f"*Bot:* {msg['content']}")