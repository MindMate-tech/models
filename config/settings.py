import os
from enum import Enum
from pydantic_settings import BaseSettings

class RunMode(Enum):
    PRODUCTION = "production"
    DEMO = "demo"
    TEST = "test"

class Settings(BaseSettings):
    # Load from environment
    dedalus_api_key: str = ""
    anthropic_api_key: str = ""
    
    run_mode: RunMode = RunMode.PRODUCTION
    use_mock_llm: bool = False
    use_cache: bool = True
    default_model: str = "anthropic/claude-sonnet-4-20250514"
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set environment variables for Dedalus
        if self.dedalus_api_key:
            os.environ['DEDALUS_API_KEY'] = self.dedalus_api_key
        if self.anthropic_api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.anthropic_api_key

settings = Settings()
