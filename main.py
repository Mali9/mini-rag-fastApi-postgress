from fastapi import FastAPI, Request, Response
# from dotenv import load_dotenv
# load_dotenv(".env")
from routers import base
from routers import data
from routers import nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Referrer-Policy header
@app.middleware("http")
async def add_referrer_policy_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
@app.on_event("startup")
async def startup():
        settings = get_settings()
        postgress_connection = f"postgresql+asyncpg://{settings.POSTGRES_DB_USER}:{settings.POSTGRES_DB_PASSWORD}@{settings.POSTGRES_DB_HOST}:{settings.POSTGRES_DB_PORT}/{settings.POSTGRES_DB_NAME}"
        app.dbengine = create_async_engine(postgress_connection)
        app.db_client = sessionmaker(app.dbengine, expire_on_commit=False, class_=AsyncSession)
        

        llmfactory = LLMProviderFactory(settings)
        vectordb_factory = VectorDBProviderFactory(settings)
        
        #llm client
        app.generation_client = llmfactory.create_provider(provider=settings.GENERATION_BACKEND)
        app.generation_client.set_generation_model(settings.LLM_MODEL_ID)
        
        #embedding client
        app.embedding_client = llmfactory.create_provider(provider=settings.EMBEDDING_BACKEND)
        app.embedding_client.set_embedding_model(settings.LLM_EMBEDDINGS_MODEL_ID, settings.LLM_MODEL_SIZE)
        
        
        #vector db client
        app.vectordb_client = vectordb_factory.create_provider(provider=settings.VECTOR_DB_TYPE)
        app.vectordb_client.connect()
        
        
        #template parser
        app.template_parser = TemplateParser(settings.DEFAULT_LANGUAGE, settings.DEFAULT_LANGUAGE)


@app.on_event("shutdown")
async def shutdown():
        app.dbengine.dispose()
        app.vectordb_client.disconnect()
        

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)