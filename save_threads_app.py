# Now we can save and load chat history in a Chainlit app
import os
import json
from operator import sub
import chainlit as cl
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from chainlit_tools import files_to_messages, ChatHistorySaver
import app_memory_hook # could be folded into chainlit_tools.py
from langchain_tools import long_division

with open("config.json", "r") as f:
    config = json.load(f)

model = config["openai"]["default_model"]
api_key = config["openai"]["api_key"]

chat_history = []
chat_history_saver = ChatHistorySaver(subdir="saved_threads")

agent = create_react_tool_agent(
    model=model,
    api_key=api_key,
    tools=[long_division],
)
app_memory_hook.chat_history, app_memory_hook.agent = chat_history, agent

@cl.on_chat_start
async def on_chat_start():   
    chat_history.clear()  # Clear chat history at the start of each chat  
    intro_message = AIMessage(f"Welcome to the Chainlit app!") # don't save this into chat_history
    await cl.Message(content=intro_message.content, actions=[chat_history_saver.load_action]).send()

# break out the logic below that turns attachments into messages


@cl.on_message
async def on_message(message: cl.Message):
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    if message.elements:
        chat_history.extend(files_to_messages(message))
    
    input = message.content
    response = await agent.ainvoke({
        "input": input,
        "chat_history": chat_history,
    })
    output = response["output"] # we can look at this more later
    if response["intermediate_steps"]:
        for step in response["intermediate_steps"]:
            print(f"Step: {step}")

    ## Update chat history with the new message and response
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=output))

    print(f"=== SENDING RESPONSE: {output} ===")
    await cl.Message(content=output, actions=[chat_history_saver.save_action]).send()


@cl.action_callback("save_chat_history")
async def save_chat_history_action():
    await chat_history_saver.save_chat_history(chat_history)
    await cl.Message("Chat history saved.").send()

@cl.action_callback("load_chat_history")
async def load_chat_history_action():
    loaded_history = await chat_history_saver.load_chat_history()
    if loaded_history:
        chat_history.clear()
        chat_history.extend(loaded_history)
        await cl.Message("Chat history loaded.").send()
    else:
        await cl.Message("No chat history loaded.").send()
    await cl.Message("You may now continue the conversation.").send()