# osb_agent_app/gemini_client.py

import os
import google.generativeai as genai

def initialize_gemini_client(api_key, model ):

    # 1️⃣ Configure with your API key
    genai.configure(api_key=api_key)

    # 2️⃣ Instantiate the Gemini‑Pro model
    llm = genai.GenerativeModel(model)

    return llm