import cohere.client_v2
from ..LLMInterface import LLMInterface
from ..LLMEnum import CoHereEnum
import cohere
import logging

class CoHereProvidor(LLMInterface):
    def __init__(self, api_key: str,
                 default_max_input_tokens: int = 1000, 
                 default_max_output_tokens: int = 1000,
                 default_temperature: float = 0.1):
        self.api_key = api_key
        self.default_max_input_tokens = default_max_input_tokens
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature
        self.model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = cohere.ClientV2(api_key=api_key)
        self.logger = logging.getLogger(__name__)
  
    def set_generation_model(self, model_id: str):
        self.model_id = model_id
        self.logger.info(f"set generation model id to {self.model_id}")
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
         self.embedding_model_id = model_id
         self.embedding_size = embedding_size
         self.logger.info(f"set embedding model id to {self.embedding_model_id}")

    
    def generate_text(self, prompt: str, chat_history: list = [], max_tokens: int = None, temperature: float = None):
        if not self.model_id:
            raise Exception("model id is not set")
        if not self.client:
            raise Exception("client is not set")

        # Build messages list with chat history
        chat_history.append(self.construct_prompt(prompt=prompt, role=CoHereEnum.USER.value))
            
        response = self.client.chat(
            model=self.model_id,
            messages=chat_history,
            temperature=temperature if temperature else self.default_temperature,
            max_tokens=max_tokens if max_tokens else self.default_max_output_tokens,
        )
        if not response or not response.messages or not response.messages[-1].content:
            raise Exception("generation failed")
        return response.messages[-1].content
    
    def emebed_text(self, text: str, document_type: str = None):
        if not self.embedding_model_id:
            raise Exception("embedding model id is not set")
        if not self.embedding_size:
            raise Exception("embedding size is not set")
        if not self.client:
            raise Exception("client is not set")
        
        response = self.client.embed(
            model=self.embedding_model_id,
            input_type=document_type,  
            texts=[self.process_text(text)],
        )
        if not response or not response.embeddings or not response.embeddings.float:
            raise Exception("embedding failed")
        return response.embeddings.float[0]

    def process_text(self, text: str):
        return text[:self.default_max_input_tokens]

    def construct_prompt(self, prompt: str, role: str):
         return {
            "role": role,
            "content": self.process_text(prompt)
        }