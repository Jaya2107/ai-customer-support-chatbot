

# backend_api.py
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import uvicorn

app = FastAPI()

company_info = """
Company (E-Commerce) Policies:

* Order cancellation & refunds: If an order is cancelled or returned, payments are refunded within 5-7 business days.
* Return window: Customers can return most products within 7 days of delivery.
* Refund processing: Refunds typically take 2-10 business days after return is received.
* Replacement / defective items: Customers can request replacement for damaged or wrong items within 7 days.
"""

llm = Ollama(model="llama3.2:1b")

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask_question(data: Query):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Customer Support Assistant. Use the company policies below to answer queries."),
        ("user", "Company Policies:\n" + company_info),
        ("user", "User Query: {question}")
    ])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": data.question})
    return {"answer": response}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
