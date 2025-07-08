# Chainlit AI Project

A conversational AI application built with Chainlit, LangChain, and OpenAI.

## Setup

### 1. Environment Setup

Activate the virtual environment:
```bash
source chainlit-env/bin/activate
```

### 2. Configuration

#### Method 1: Using the JSON config file (Recommended)

1. Copy the template configuration:
   ```bash
   cp config.template.json config.json
   ```

2. Edit `config.json` and add your API keys:
   ```json
   {
     "openai": {
       "api_key": "sk-your-actual-openai-api-key",
       "model": "gpt-4",
       "temperature": 0.7,
       "max_tokens": 1000
     },
     "anthropic": {
       "api_key": "sk-ant-your-anthropic-api-key",
       "model": "claude-3-sonnet-20240229"
     }
   }
   ```

#### Method 2: Using environment variables

Alternatively, you can set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export LANGCHAIN_API_KEY="your-langsmith-api-key"
```

### 3. Using the Configuration

#### In Python code:

```python
from config_manager import config, setup_openai_client, setup_anthropic_client

# Load configuration and set environment variables
config.set_env_vars()

# Get configuration values
openai_model = config.get('openai.model')
chainlit_port = config.get('chainlit.port')

# Setup clients
openai_client = setup_openai_client()
anthropic_client = setup_anthropic_client()
```

#### Direct access to config values:

```python
from config_manager import config

# Access nested configuration
api_key = config.get('openai.api_key')
model = config.get('openai.model', 'gpt-3.5-turbo')  # with default
debug_mode = config.get('chainlit.debug')

# Get entire sections
openai_config = config.get_openai_config()
chainlit_config = config.get_chainlit_config()
```

## Configuration File Structure

The `config.json` file contains the following sections:

- **openai**: OpenAI API settings
- **anthropic**: Anthropic Claude API settings  
- **langchain**: LangChain and LangSmith settings
- **chainlit**: Chainlit application settings
- **database**: Database connection settings
- **logging**: Logging configuration

## Security

- `config.json` is included in `.gitignore` to prevent committing API keys
- Use `config.template.json` as a reference for the expected structure
- Never commit actual API keys to version control

## Getting API Keys

### OpenAI
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `config.json` file

### Anthropic
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Add it to your `config.json` file

### LangSmith (optional)
1. Go to [LangSmith](https://smith.langchain.com/)
2. Create an API key for tracing and monitoring
3. Add it to your `config.json` file

## Available Models

### OpenAI Models
- `gpt-4` (recommended)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### Anthropic Models
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`
- `claude-3-opus-20240229`

## Running the Application

```bash
# Activate environment
source chainlit-env/bin/activate

# Run your Chainlit app (once you create one)
chainlit run app.py
```

## Development

### Installing Additional Packages

```bash
source chainlit-env/bin/activate
pip install package-name
pip freeze > requirements.txt  # Update requirements
```

### Project Structure

```
chainlit/
├── chainlit-env/          # Virtual environment
├── config.json            # Your configuration (gitignored)
├── config.template.json   # Template configuration
├── config_manager.py      # Configuration utility
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```
