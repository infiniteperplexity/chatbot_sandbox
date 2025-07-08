# Can I abstract this out of ChainLit somehow, while still making it easy to stick back into ChainLit?

import json
import chainlit as cl
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

with open("config.json", "r") as f:
    config = json.load(f)

model = config["openai"]["default_model"]
api_key = config["openai"]["api_key"]


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

chat_history = []

## This could be swapped for a non-ChainLit function
async def send_message_to_user(message: str):
    await cl.Message(content=message).send()

async def on_chat_start_function():
    intro_message = AIMessage(f"Welcome to the Chainlit app! I can perform long division and read file attachments. Try sending me a message or attaching a file.")
    await send_message_to_user(intro_message.content)
    chat_history.append(intro_message)

@cl.on_chat_start
async def on_chat_start():   
    await on_chat_start_function()


## This is a little trickier, because if you want to abstract away from ChainLit,
# you need to break out every property and sub-property of the message that you plan to use.
# although, I think there might be a to_dict() method that does just that.
async def send_message_dict_to_model(message_dict: dict):
    print(f"=== MESSAGE RECEIVED: {message_dict['content']} ===")
    input = message_dict['content']
    if message_dict['elements']:
        print("=== FILE ATTACHMENTS RECEIVED ===")
        for element in message_dict["elements"]:
            if element["type"] == "file" and ("mime" not in element or element["mime"] == "text/plain" or not element["mime"]):
                file_name = element["name"] if element["name"] else "(unknown file name)"
                with open(file_name, "r") as f:
                    file_text = f.read()
                print(f"=== FILE CONTENTS OF {file_name} ===")
                print(file_text)
                chat_history.append(HumanMessage(content=f"Attached file name: {file_name}\n\nContents: {file_text}"))
    response = await agent.ainvoke({
        "input": input,
        "chat_history": chat_history,
    })
    output = response["output"]
    if response["intermediate_steps"]:
        print("=== INTERMEDIATE STEPS ===")
        print(response["intermediate_steps"])

    ## Update chat history with the new message and response
    print(f"=== UPDATING CHAT HISTORY ===")
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=output))
    print(f"=== SENDING RESPONSE: {output} ===")
    # Send the response back to the user
    await send_message_to_user(output)

@cl.on_message
async def on_message(message: cl.Message):
    message_dict = message.to_dict() # I think this works
    await send_message_dict_to_model(message_dict)