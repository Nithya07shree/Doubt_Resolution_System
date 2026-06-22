import os
import json
from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically locate the backend base directory and .env file
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="your-openai-api-key-here")
    DATABASE_URL: str = Field(default="sqlite:///./doubt_resolution.db")
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            try:
                if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                    v = v[1:-1]
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:
                return [x.strip() for x in v.split(",") if x.strip()]
        return v

# Instantiate settings
try:
    settings = Settings()
except Exception as e:
    # Graceful fallback if settings parsing encounters an error
    print(f"Warning: Failed to load environment settings: {e}. Using default settings.")
    settings = Settings(_env_file=None)
