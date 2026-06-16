import os

from groq import AsyncGroq

groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY", ""))
