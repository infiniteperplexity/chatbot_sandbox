"""
Configuration loader utility for the Chainlit chatbot.
"""
import json
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    """Load and manage configuration from JSON file."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the config loader.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self._config: Optional[Dict[str, Any]] = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file.
        
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if self._config is None:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file '{self.config_path}' not found")
            
            with open(self.config_path, 'r') as file:
                self._config = json.load(file)
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'openai.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = self.load_config()
        keys = key.split('.')
        
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return self.get('openai', {})
    
    def get_anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic configuration."""
        return self.get('anthropic', {})
    
    def get_langchain_config(self) -> Dict[str, Any]:
        """Get LangChain configuration."""
        return self.get('langchain', {})
    
    def get_chainlit_config(self) -> Dict[str, Any]:
        """Get Chainlit configuration."""
        return self.get('chainlit', {})

# Global config instance
config = ConfigLoader()
