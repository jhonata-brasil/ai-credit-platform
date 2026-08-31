from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    app_url: str = "http://localhost:8000"
    vectorstore: str = "chroma"
    pinecone_api_key: str = ""
    pinecone_index: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
