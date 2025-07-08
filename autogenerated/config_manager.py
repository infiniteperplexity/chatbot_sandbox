"""
Configuration utility module for loading and managing app settings.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration from JSON files."""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration JSON file
        """
        self.config_file = Path(config_file)
        self._config = None
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from the JSON file."""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found. "
                f"Please create it based on 'config.template.json'"
            )
        
        try:
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'openai.api_key')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        if self._config is None:
            self.load_config()
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
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
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.get('database', {})
    
    def set_env_vars(self) -> None:
        """Set environment variables from configuration."""
        # OpenAI
        openai_key = self.get('openai.api_key')
        if openai_key and openai_key != "your-openai-api-key-here":
            os.environ['OPENAI_API_KEY'] = openai_key
        
        # Anthropic
        anthropic_key = self.get('anthropic.api_key')
        if anthropic_key and anthropic_key != "your-anthropic-api-key-here":
            os.environ['ANTHROPIC_API_KEY'] = anthropic_key
        
        # LangSmith
        langsmith_key = self.get('langchain.langsmith_api_key')
        if langsmith_key and langsmith_key != "your-langsmith-api-key-here":
            os.environ['LANGCHAIN_API_KEY'] = langsmith_key
            os.environ['LANGSMITH_API_KEY'] = langsmith_key
        
        # LangChain tracing
        if self.get('langchain.tracing'):
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        
        # LangChain project
        project_name = self.get('langchain.project_name')
        if project_name:
            os.environ['LANGCHAIN_PROJECT'] = project_name
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.load_config()
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        if self._config is None:
            self.load_config()
        return self._config


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config


def load_config(config_file: str = "config.json") -> ConfigManager:
    """
    Load configuration from a specific file.
    
    Args:
        config_file: Path to the configuration JSON file
        
    Returns:
        ConfigManager instance
    """
    return ConfigManager(config_file)


# Example usage functions
def setup_openai_client():
    """Setup OpenAI client with configuration."""
    try:
        from openai import OpenAI
        
        openai_config = config.get_openai_config()
        api_key = openai_config.get('api_key')
        
        if not api_key or api_key == "your-openai-api-key-here":
            raise ValueError("OpenAI API key not configured")
        
        return OpenAI(api_key=api_key)
    except ImportError:
        raise ImportError("OpenAI package not installed")


def setup_anthropic_client():
    """Setup Anthropic client with configuration."""
    try:
        from anthropic import Anthropic
        
        anthropic_config = config.get_anthropic_config()
        api_key = anthropic_config.get('api_key')
        
        if not api_key or api_key == "your-anthropic-api-key-here":
            raise ValueError("Anthropic API key not configured")
        
        return Anthropic(api_key=api_key)
    except ImportError:
        raise ImportError("Anthropic package not installed")


if __name__ == "__main__":
    # Example usage
    print("Configuration loaded:")
    print(f"OpenAI model: {config.get('openai.model')}")
    print(f"Chainlit port: {config.get('chainlit.port')}")
    print(f"Debug mode: {config.get('chainlit.debug')}")
    
    # Set environment variables
    config.set_env_vars()
    print("Environment variables set from configuration")
