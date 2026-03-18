import os
from dotenv import load_dotenv
from utils.llm_factory import get_llm
from langchain_core.messages import HumanMessage

def test_groq_integration():
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found. Please set it in .env")
        return

    print("Testing Groq Factory...")
    try:
        llm = get_llm(provider="Groq")
        print(f"✅ Factory returned LLM: {type(llm).__name__}")
        
        print("Sending test message to Groq...")
        response = llm.invoke([HumanMessage(content="Hello Groq! Say 'Groq integration works!' if you hear me.")])
        print(f"🤖 Groq Response: {response.content}")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_groq_integration()
