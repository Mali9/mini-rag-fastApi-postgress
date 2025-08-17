from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Mini RAG FastAPI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    # File settings
    FILE_ALLOWED_EXTENSIONS: list[str] = ["pdf", "txt", "docx"]
    FILE_MAX_SIZE: int = 10485760  # 10MB
    FILE_CHUNK_SIZE: int = 1000

    # Database settings
    MONGO_DB_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "mini_rag_db"

    # LLM Provider Backends
    GENERATION_BACKEND: str | None = "OLLAMA"
    EMBEDDING_BACKEND: str | None = "OLLAMA"

    # --- LLM Models & Parameters ---
    LLM_MODEL_ID: str | None = "gemma3:1b"
    LLM_EMBEDDINGS_MODEL_ID: str | None = "nomic-embed-text"
    LLM_MODEL_SIZE: int | None = 768
    LLM_MODEL_TEMPERATURE: float | None = 0.1
    LLM_MAX_OUTPUT_TOKENS: int | None = 1024
    LLM_MAX_INPUT_TOKENS: int | None = 2048

    # --- Provider Specific ---
    OPENAI_API_KEY: str | None = None
    OPENAI_API_URL: str | None = None
    COHERE_API_KEY: str | None = None

    # --- Vector DB ---
    VECTOR_DB_TYPE: str = "QDRANT"
    VECTOR_DB_PATH: str = "src/assets/database/qdrant.db"
    VECTOR_DB_DISTANCE_METRIC: str = "Cosine"
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 1000

    # --- Deprecated fields from user's .env to prevent validation errors ---
    # Please migrate to the LLM_... variables above
    default_model: str | None = None
    default_model_size: int | None = None
    default_model_temperature: float | None = None
    default_model_max_output_tokens: int | None = None
    default_model_max_input_tokens: int | None = None
    
    DEFAULT_LANGUAGE: str = "en"
    OLLAMA_MODEL_ID: str = "gemma:2b"
    OLLAMA_MODEL_SIZE: int = 768
    OLLAMA_API_URL: str = "http://localhost:11434"

    POSTGRES_DB_HOST: str = "localhost"
    POSTGRES_DB_PORT: int = 5432
    POSTGRES_DB_NAME: str = "vectordb"
    POSTGRES_DB_USER: str = "postgres"
    POSTGRES_DB_PASSWORD: str = "yourpassword"

    class Config:
        # env_file = ".env"  # Temporarily disabled due to encoding issues
        env_file_encoding = "utf-8"
        env_file_ignore_empty = True
        
def get_settings():
    return Settings()
