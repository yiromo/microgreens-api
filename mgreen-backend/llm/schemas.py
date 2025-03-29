from enum import Enum

class AIModelType(str, Enum):
    GPT4O = "gpt-4o"
    GPT4OMINI = "gpt-4o-mini-2024-07-18"

class LLMTemperature:
    LOWEST = 1e-5
    CREATIVE = 0.7
    BALANCED = 0.5
    PRECISE = 0.2

class MAXTOKENS:
    MIN=8000
    MAX = 16000