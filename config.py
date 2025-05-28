import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
OPEN_STUDY_BUILDER_URL = os.getenv("OPEN_STUDY_BUILDER_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_MODEL2 = os.getenv("GEMINI_MODEL2")