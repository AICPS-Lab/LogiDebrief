import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration management for LogiDebrief research prototype."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.load_config()
        
    def load_config(self):
        """Load configuration from environment variables and files."""
        # API Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )
        
        # Assistant IDs Configuration
        self.function_mappings_path = self.base_dir / 'function_mappings.json'
        self.assistant_ids = self._load_assistant_ids()
        
        # Paths Configuration
        self.guidecards_dir = self.base_dir / 'guidecards'
        self.protocols_dir = self.base_dir / 'protocols'
        self.examples_dir = self.base_dir / 'examples'
        
        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logidebrief.log')
        
    def _load_assistant_ids(self) -> Dict[str, str]:
        """Load and validate OpenAI Assistant IDs from configuration file."""
        if not self.function_mappings_path.exists():
            raise FileNotFoundError(
                f"function_mappings.json not found at {self.function_mappings_path}"
            )
        
        with open(self.function_mappings_path, 'r') as f:
            mappings = json.load(f)
        
        # Check for placeholder values
        placeholders = []
        for key, value in mappings.items():
            if 'YOUR_ASSISTANT_ID' in value or not value:
                placeholders.append(key)
        
        if placeholders:
            raise ValueError(
                f"Please configure the following assistant IDs in function_mappings.json: "
                f"{', '.join(placeholders)}"
            )
        
        return mappings
    
    def validate(self) -> bool:
        """Validate all required configuration is present."""
        required_dirs = [self.guidecards_dir, self.protocols_dir]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                raise FileNotFoundError(f"Required directory not found: {dir_path}")
        
        return True
    
    @property
    def is_configured(self) -> bool:
        """Check if the application is properly configured."""
        try:
            return self.validate()
        except (ValueError, FileNotFoundError):
            return False