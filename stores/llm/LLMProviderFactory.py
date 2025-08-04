from .LLMEnum import LLMEnum
from .LLMInterface import LLMInterface
from .providors.CoHereProvidor import CoHereProvidor
from .providors.OpenAiProvidor import OpenAiProvidor
from .providors.OllamaProvidor import OllamaProvidor
import logging

class LLMProviderFactory:
    """
    Factory class for creating LLM provider instances based on the LLMEnum.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def create_provider(self, provider: str | None):
        """
        Create an LLM provider instance based on the provider type.
        
        Args:
            provider (str | None): The type of LLM provider to create
            
        Returns:
            LLMInterface: An instance of the requested LLM provider
            
        Raises:
            ValueError: If an unsupported provider type is specified or provider is None
        """
        
        if provider is None:
            raise ValueError("Provider type cannot be None")
        
        if provider == LLMEnum.OPENAI.value:
            return OpenAiProvidor(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_max_input_tokens=self.config.LLM_MAX_INPUT_TOKENS or 1000,
                default_max_output_tokens=self.config.LLM_MAX_OUTPUT_TOKENS or 1000,
                default_temperature=self.config.LLM_MODEL_TEMPERATURE or 0.1
            )
            
        elif provider == LLMEnum.COHERE.value:
            return CoHereProvidor(
                api_key=self.config.COHERE_API_KEY,
                default_max_input_tokens=self.config.LLM_MAX_INPUT_TOKENS or 1000,
                default_max_output_tokens=self.config.LLM_MAX_OUTPUT_TOKENS or 1000,
                default_temperature=self.config.LLM_MODEL_TEMPERATURE or 0.1
            )
            
        elif provider == LLMEnum.OLLAMA.value:
            return OllamaProvidor(
                api_url=getattr(self.config, 'OLLAMA_API_URL', 'http://localhost:11434'),
                default_max_input_tokens=self.config.LLM_MAX_INPUT_TOKENS or 1000,
                default_max_output_tokens=self.config.LLM_MAX_OUTPUT_TOKENS or 1000,
                default_temperature=self.config.LLM_MODEL_TEMPERATURE or 0.1
            )
             
        else:
            raise ValueError(f"Unsupported provider type: {provider}")