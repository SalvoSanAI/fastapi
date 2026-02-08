from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    database_host: str = "localhost"  # Default to localhost
    database_password: str = "sa"  # Default password for the database (not recommended for production)
    database_name: str = "fastapi"  # Default database name
    database_user: str = "postgres"  # Default username for the database    
    database_port: str = "5432"  # Default port for the database (e.g., PostgreSQL default port)
    secret_key: str = "your_secret_key_here"  # Default secret key for JWT token encoding (should be overridden in production)
    algorithm: str = "HS256"  # Default algorithm for JWT token encoding
    access_token_expire_seconds: int = 30 * 60  # Default token expiration time (30 minutes)
    
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()  # Load settings from environment variables or use defaults    
