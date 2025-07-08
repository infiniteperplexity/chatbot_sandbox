"""
Basic Chainlit chatbot using LangChain and GPT-4.

This example demonstrates how to create a simple conversational AI
using Chainlit, LangChain, and OpenAI's GPT-4 model.
"""
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config_loader import config

# Load OpenAI configuration
openai_config = config.get_openai_config()

# Initialize the OpenAI chat model
llm = ChatOpenAI(
    api_key=openai_config.get('api_key'),
    model=openai_config.get('model', 'gpt-4.1'),
    temperature=openai_config.get('temperature', 0.7),
    max_tokens=openai_config.get('max_tokens', 1000)
)

# System message to set the AI's behavior
SYSTEM_MESSAGE = SystemMessage(content="""
You are a helpful AI assistant built with Chainlit and LangChain. 
You should be friendly, informative, and concise in your responses.
""")

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    await cl.Message(
        content="Hello! I'm your AI assistant powered by GPT-4.1. How can I help you today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages from the user."""
    try:
        # Create the message list with system message and user input
        messages = [
            SYSTEM_MESSAGE,
            HumanMessage(content=message.content)
        ]
        
        # Get response from the LLM
        response = await llm.ainvoke(messages)
        
        # Send the response back to the user
        await cl.Message(content=response.content).send()
        
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Sorry, I encountered an error: {str(e)}"
        await cl.Message(content=error_message).send()

if __name__ == "__main__":
    # Run the Chainlit app
    # Note: This will be handled by the chainlit command in practice
    pass
