import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(provider="Ollama", model_name=None):
    """
    Factory function to return the requested LLM provider.
    """
    if provider == "Groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # Fallback or error if Groq is selected but no key is found
            # In a production app, we'd handle this more gracefully in the UI
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        
        # Default Groq model if none provided
        model = model_name if model_name else "llama-3.3-70b-versatile"
        return ChatGroq(
            model=model,
            temperature=0,
            api_key=api_key
        )
    else:
        # Default to local Ollama
        model = model_name if model_name else "phi3:mini"
        return ChatOllama(
            model=model,
            temperature=0
        )
