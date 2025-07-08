# This should be a nearly-trivial ChainLit app.  It won't even have a language model; it always tells you it can't complete the request.
# It should log to a file, using the default level, and it should also write "hello world" to the log whenever the user sends submits a message.
import chainlit as cl
import logging
import os

print("=== TRIVIAL APP STARTING ===")
print(f"Current working directory: {os.getcwd()}")

# Create a dedicated logger for this app
logger = logging.getLogger('trivial_app')
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('trivial_app.log')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)

# Log that the app is starting
print("About to write startup log message...")
logger.info("Trivial Chainlit app started")
print("Startup log message written")

# Also write to a backup file to ensure we can write somewhere
with open('/home/perplexity/Desktop/GitHub/chainlit/app_debug.txt', 'w') as f:
    f.write("App started successfully\n")

@cl.on_message
async def on_message(message: cl.Message):
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    
    # Log the incoming message
    logger.info(f"Received message: {message.content}")
    
    # Also log "hello world" as requested
    logger.info("hello world")
    
    # Respond with a fixed message
    response = "I can't complete your request, but hello world!"
    
    # Log the response
    logger.info(f"Sending response: {response}")
    
    print(f"=== SENDING RESPONSE: {response} ===")
    
    # Send the response back to the user
    await cl.Message(content=response).send()