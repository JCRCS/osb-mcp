# osb_agent_app/gemini_client.py

import os
from google import generativeai

def initialize_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set.")
    generativeai.configure(api_key=api_key)
    return generativeai
