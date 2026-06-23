import os
import json
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically locate the backend base directory and .env file
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="your-openai-api-key-here")
    DATABASE_URL: str = Field(default="sqlite:///./doubt_resolution.db")
    
    # Store ALLOWED_ORIGINS as a plain string to completely bypass 
    # Pydantic Settings' internal JSON decoder for complex types.
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000")

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """
        Parses the ALLOWED_ORIGINS string into a list of origins.
        Handles both JSON lists (e.g. '["http://localhost:3000"]') and 
        comma-separated strings (e.g. 'http://localhost:3000,https://app.vercel.app').
        """
        v = self.ALLOWED_ORIGINS.strip()
        if not v:
            return []
        
        # If it looks like a JSON array, attempt parsing
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
            except Exception:
                pass
                
        # Fall back to standard comma separation
        return [x.strip() for x in v.split(",") if x.strip()]

# Instantiate settings
try:
    settings = Settings()
except Exception as e:
    # Graceful fallback if settings parsing encounters an error
    print(f"Warning: Failed to load environment settings: {e}. Using default settings.")
    settings = Settings(_env_file=None)
