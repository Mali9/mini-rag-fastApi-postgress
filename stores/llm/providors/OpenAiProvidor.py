from ..LLMInterface import LLMInterface
from ..LLMEnum import OpenAIEnum
import openai
import logging

class OpenAiProvidor(LLMInterface):
    def __init__(self, api_key: str
                 ,api_url: str,
                 default_max_input_tokens: int = 1000, 
                 default_max_output_tokens: int = 1000,
                 default_temperature: float = 0.1):
        self.api_key = api_key
        self.api_url = api_url
        self.default_max_input_tokens = default_max_input_tokens
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature
        self.model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.api_url)
        self.logger = logging.getLogger(__name__)
    
    def set_generation_model(self, model_id: str):
        self.model_id = model_id
        self.logger.info(f"set model id to {self.model_id}")
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
         self.embedding_model_id = model_id
         self.embedding_size = embedding_size
         self.logger.info(f"set embedding model id to {self.embedding_model_id}")

    
    def generate_text(self, prompt: str,chat_history: list = [], max_tokens: int = None, temperature: float = None):
        if not self.model_id:
            raise Exception("model id is not set")
        if not self.client:
            raise Exception("client openApi is not set")
        if not max_tokens:
            max_tokens = self.default_max_output_tokens
        if not temperature:
            temperature = self.default_temperature
            
        chat_history.append(self.construct_prompt(prompt=prompt,role=OpenAIEnum.USER.value))
        response = self.client.chat.completions.create(
            messages=chat_history,
            model=self.model_id,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if not response or not response.choices or not response.choices[0] or not response.choices[0].message.content:
            raise Exception("generation failed")
        return response.choices[0].message.content
    
    def emebed_text(self, text: str,document_type: str = None):
        if not self.embedding_model_id:
            raise Exception("embedding model id is not set")
        if not self.embedding_size:
            raise Exception("embedding size is not set")
        if not self.client:
            raise Exception("openApi client is not set")
        
        response = self.client.embeddings.create(
            model=self.embedding_model_id,  
            input=text,
        )
        if not response or not response.data or not response.data[0] or not response.data[0].embedding:
            raise Exception("embedding failed")
        return response.data[0].embedding

    def process_text(self, text: str):
        return text[:self.default_max_input_tokens]

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role":role,
            "content":self.process_text(prompt)
        }