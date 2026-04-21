"""Application configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Oracle Configuration
    ORACLE_HOST: str = "cms-oracle-xe"
    ORACLE_PORT: int = 1521
    ORACLE_USER: str = "system"
    ORACLE_PASSWORD: str = "oracle"
    ORACLE_SERVICE: str = "xepdb1"
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = "jposee-db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "jposee"
    
    # API Configuration
    API_TITLE: str = "CMS Platform API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
