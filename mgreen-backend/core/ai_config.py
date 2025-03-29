from openai import OpenAI
from core.config import settings

OPENAI_CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY)

AI_CONFIG = {
    "role": "Plants AI - Знаток по микрозелени",  
    "temperature": 1e-5,  
    "system_message": (
        ""
    ),
}


