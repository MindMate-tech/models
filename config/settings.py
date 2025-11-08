import os
from enum import Enum

try:
    from pydantic_settings import BaseSettings
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback if pydantic_settings is not installed
    class BaseSettings:
        """Fallback BaseSettings class when pydantic_settings is not available"""
        def __init__(self, **kwargs):
            # Load from environment variables directly
            for key, default in kwargs.items():
                env_key = key.upper()
                value = os.getenv(env_key, default)
                setattr(self, key, value)
            
            # Also try loading from .env file if it exists
            env_file = ".env"
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip().upper()
                                value = value.strip().strip('"').strip("'")
                                # Convert to attribute name (lowercase, remove DEDALUS_/ANTHROPIC_ prefix if needed)
                                attr_key = key.lower().replace('dedalus_api_key', 'dedalus_api_key').replace('anthropic_api_key', 'anthropic_api_key')
                                if hasattr(self, attr_key) or attr_key in ['dedalus_api_key', 'anthropic_api_key']:
                                    setattr(self, attr_key, value)
                except Exception:
                    pass  # Ignore errors reading .env file
    
    PYDANTIC_AVAILABLE = False
    print("⚠️  WARNING: pydantic_settings not installed. Using fallback implementation.")
    print("   Install with: pip install pydantic-settings")

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
    
    if PYDANTIC_AVAILABLE:
        class Config:
            env_file = ".env"
    
    def __init__(self, **kwargs):
        if PYDANTIC_AVAILABLE:
            super().__init__(**kwargs)
        else:
            # Fallback initialization
            self.dedalus_api_key = os.getenv('DEDALUS_API_KEY', kwargs.get('dedalus_api_key', ''))
            self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', kwargs.get('anthropic_api_key', ''))
            self.run_mode = RunMode(kwargs.get('run_mode', os.getenv('RUN_MODE', 'production')))
            self.use_mock_llm = kwargs.get('use_mock_llm', os.getenv('USE_MOCK_LLM', 'False').lower() == 'true')
            self.use_cache = kwargs.get('use_cache', os.getenv('USE_CACHE', 'True').lower() == 'true')
            self.default_model = kwargs.get('default_model', os.getenv('DEFAULT_MODEL', 'anthropic/claude-sonnet-4-20250514'))
        
        # Set environment variables for Dedalus
        if self.dedalus_api_key:
            os.environ['DEDALUS_API_KEY'] = self.dedalus_api_key
        if self.anthropic_api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.anthropic_api_key

settings = Settings()
