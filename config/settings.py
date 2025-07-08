from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    chroma_db_path: str = "./data/chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    log_level: str = "INFO"
