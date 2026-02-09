import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory (one level up from app/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Configuration
    API_STR: str = "/api"
    PROJECT_NAME: str = "software-template-service"
    
    # GitHub Configuration
    GH_ACCESS_TOKEN: Optional[str] = None
    EXCLUDE_GITHUB_WORKFLOWS: bool = False  # Set to True if your token doesn't have 'workflow' scope
    
    # DX Self-Service Configuration
    DX_API_URL: str = "https://api.getdx.com"
    DX_API_KEY: Optional[str] = None
    
    # Cookiecutter Template URLs
    COOKIECUTTER_DJANGO_URL: str = "https://github.com/cookiecutter/cookiecutter-django"
    COOKIECUTTER_GO_URL: str = "https://github.com/lacion/cookiecutter-golang"
    COOKIECUTTER_CPP_URL: str = "https://github.com/DerThorsten/cpp_cookiecutter"
    COOKIECUTTER_PYTHON_URL: str = "https://github.com/audreyfeldroy/cookiecutter-pypackage"
    COOKIECUTTER_OUTPUT_DIR: str = "cookiecutter_output/{uuid}"
    
    # Cookiecutter Hook Configuration
    # Set to False to skip post-generation hooks (useful if templates require tools like 'uv')
    COOKIECUTTER_ACCEPT_HOOKS: bool = False
    
    # Webhook Security (optional)
    WEBHOOK_SECRET: Optional[str] = None


settings = Settings()
