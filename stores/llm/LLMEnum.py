from enum import Enum
class LLMEnum(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    OLLAMA = "OLLAMA"
    
class OpenAIEnum(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class CoHereEnum(Enum):
    USER = "USER"
    ASSISTANT = "CHATBOT"
    SYSTEM = "SYSTEM"
    
class OllamaEnum(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"