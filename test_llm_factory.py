"""
Example usage of the LLM Provider Factory
"""
from stores.llm import LLMProviderFactory, LLMEnum

def test_llm_factory():
    """Test the LLM Provider Factory with different providers"""
    
    # Sample configuration
    config = {
        "OPENAI_API_KEY": "your-openai-api-key",
        "OPENAI_API_URL": "https://api.openai.com/v1",
        "COHERE_API_KEY": "your-cohere-api-key",
        "LLM_MAX_INPUT_TOKENS": 2000,
        "LLM_MAX_OUTPUT_TOKENS": 1000,
        "LLM_MODEL_TEMPERATURE": 0.7
    }
    
    # Create factory instance
    factory = LLMProviderFactory(config)
    
    # Example 1: Create OpenAI provider
    try:
        openai_provider = factory.create_provider(LLMEnum.OPENAI.value)
        print("✅ OpenAI provider created successfully")
        
        # Set models
        openai_provider.set_generation_model("gpt-3.5-turbo")
        openai_provider.set_embedding_model("text-embedding-ada-002", 1536)
        
    except ValueError as e:
        print(f"❌ OpenAI provider creation failed: {e}")
    
    # Example 2: Create CoHere provider
    try:
        cohere_provider = factory.create_provider(LLMEnum.COHERE.value)
        print("✅ CoHere provider created successfully")
        
        # Set models
        cohere_provider.set_generation_model("command")
        cohere_provider.set_embedding_model("embed-english-v3.0", 1024)
        
    except ValueError as e:
        print(f"❌ CoHere provider creation failed: {e}")
    
    # Example 3: Test unsupported provider
    try:
        # This should raise an error
        unsupported_provider = factory.create_provider("UNSUPPORTED")
    except ValueError as e:
        print(f"✅ Correctly caught unsupported provider error: {e}")

if __name__ == "__main__":
    test_llm_factory() 