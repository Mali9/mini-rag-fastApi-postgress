import requests
from ..LLMInterface import LLMInterface
from ..LLMEnum import OllamaEnum
import logging

class OllamaProvidor(LLMInterface):
    def __init__(self, api_url: str = "http://localhost:11434",
                 default_max_input_tokens: int = 1000, 
                 default_max_output_tokens: int = 1000,
                 default_temperature: float = 0.1):
        self.api_url = api_url
        self.default_max_input_tokens = default_max_input_tokens
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature
        self.model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.logger = logging.getLogger(__name__)
    
    def set_generation_model(self, model_id: str):
        self.model_id = model_id
        self.logger.info(f"set generation model id to {self.model_id}")
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
         self.embedding_model_id = model_id
         self.embedding_size = embedding_size
         self.logger.info(f"set embedding model id to {self.embedding_model_id}")

    def generate_text(self, prompt: str, chat_history: list = None, max_tokens: int = None, temperature: float = None):
        if not self.model_id:
            raise Exception("model id is not set")
        if chat_history is None:
            chat_history = []
        if not max_tokens:
            max_tokens = self.default_max_output_tokens
        if not temperature:
            temperature = self.default_temperature

        # Make a copy to avoid mutating the original
        messages = list(chat_history)
        messages.append({
            "role": OllamaEnum.USER.value,
            "content": self.process_text(prompt)
        })
        try:
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={
                    "model": self.model_id,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            try:
                result = response.json()
            except Exception as json_err:
                raw = response.text
                raise Exception(f"Failed to decode Ollama response as JSON. Raw response: {raw}") from json_err

            if not result or "message" not in result or "content" not in result["message"]:
                raise Exception(f"generation failed, response: {result}")

            return result["message"]["content"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {str(e)}")
    
    def emebed_text(self, text: str, document_type: str = None):
        if not self.embedding_model_id:
            raise Exception("embedding model id is not set")
        if not self.embedding_size:
            raise Exception("embedding size is not set")
        try:
            response = requests.post(
                f"{self.api_url}/api/embeddings",
                json={
                    "model": self.embedding_model_id,
                    "prompt": self.process_text(text)
                },
                timeout=30
            )
            response.raise_for_status()
            try:
                result = response.json()
            except Exception as json_err:
                # Log the raw response for debugging
                raw = response.text
                raise Exception(f"Failed to decode Ollama embedding response as JSON. Raw response: {raw}") from json_err
            if not result or "embedding" not in result:
                raise Exception(f"embedding failed, response: {result}")
            embedding = result["embedding"]
            # Ensure embedding is a list
            if not isinstance(embedding, list):
                embedding = list(embedding)
            # Check embedding dimension
            if len(embedding) != int(self.embedding_size):
                raise Exception(f"Embedding dimension mismatch: expected {self.embedding_size}, got {len(embedding)}")
            return embedding
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama embedding API request failed: {str(e)}")

    def process_text(self, text: str):
        return text[:self.default_max_input_tokens]

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        } 