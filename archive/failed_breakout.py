## Let's try to add the following features:
# 1. Be able to see the file attachments.
# 2. Very basic tool use.
# 3. The simplest form of chat history that doesn't reduce in any way.

import json
import chainlit as cl
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import sys
import time

print(f"=== MODULE LOADING at {time.time()} ===")
print(f"Module name: {__name__}")
print(f"Reload count: {getattr(sys.modules.get(__name__, None), '_reload_count', 0) + 1}")

with open("config.json", "r") as f:
    config = json.load(f)

model = config["openai"]["default_model"]
api_key = config["openai"]["api_key"]

chat_history = []

@tool
def long_division(dividend: int, divisor: int) -> str:
    """Perform long division on two integers."""
    if divisor == 0:
        return "Error: Division by zero is not allowed."
    result = dividend / divisor
    quotient = int(result)
    remainder = dividend % divisor
    return f"The result of {dividend} divided by {divisor} is {quotient} with a remainder of {remainder} ({result})."

agent = create_react_tool_agent(
    model=model,
    api_key=api_key,
    tools=[long_division],
)

@cl.on_chat_start
async def on_chat_start():   
    intro_message = AIMessage(f"Welcome to the Chainlit app! I can perform long division and read file attachments. Try sending me a message or attaching a file.")
    await cl.Message(content=intro_message.content).send()
    print("does this actually run?")
    chat_history = [intro_message]
    print(f"Length of chat history: {len(chat_history)}")
    print(f"id of chat history: {id(chat_history)}")

@cl.on_message
async def on_message(message: cl.Message):
    #global chat_history
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    input = message.content
    if message.elements:
        print("=== FILE ATTACHMENTS RECEIVED ===")
        for element in message.elements:
            if element.type == "file" and (element.mime == "text/plain" or not element.mime): 
                file_name = element.name if element.name else "(unknown file name)"
                with open(file_name, "r") as f:
                    file_text = f.read()
                #input = f"{message.content}\n\nFile name: {file_name}\nFile content:\n{file_text}"
                # once we actually have chat history, we will want to use that instead of concatenating, I think.
    #response = (await agent.ainvoke({"input": input}))
    
    response = await agent.ainvoke({
        "input": input,
        #"chat_history": chat_history,
        "chat_history": [msg for msg in chat_history],  # Convert messages to string content
    })
    output = response["output"]
    if response["intermediate_steps"]:
        print("=== INTERMEDIATE STEPS ===")
        print(response["intermediate_steps"])

    ## Update chat history with the new message and response
    print(f"=== UPDATING CHAT HISTORY ===")
    
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=output))
    print(f"Length of chat history: {len(chat_history)}")
    print(f"id of chat history: {id(chat_history)}")

    print(f"=== SENDING RESPONSE: {output} ===")
    # Send the response back to the user
    await cl.Message(content=output).send()