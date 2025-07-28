import json
import chainlit as cl
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import app_memory_hook
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

client = MultiServerMCPClient({
    "sequential_thinking": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "transport": "stdio",
    }
})
#mcp_tools = await client.get_tools() # this got an error from running await outside a function
mcp_tools = asyncio.run(client.get_tools())  # Use asyncio.run to get tools in


with open("config.json", "r") as f:
    config = json.load(f)

model = config["openai"]["default_model"]
api_key = config["openai"]["api_key"]

chat_history = []


agent = create_react_tool_agent(
    model=model,
    api_key=api_key,
    tools=mcp_tools,  # Use the MCP tools loaded from the client
)

# So I can see these variables from a notebook running this app as a thread
app_memory_hook.chat_history = chat_history
app_memory_hook.agent = agent

@cl.on_chat_start
async def on_chat_start():   
    chat_history.clear()  # Clear chat history at the start of each chat  
    intro_message = AIMessage(f"Welcome to the Chainlit app! I can perform long division and read file attachments. Try sending me a message or attaching a file.")
    chat_history.append(intro_message)
    await cl.Message(content=intro_message.content).send()
    

@cl.on_message
async def on_message(message: cl.Message):
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    input = message.content
    if message.elements:
        print("=== FILE ATTACHMENTS RECEIVED ===")
        for element in message.elements:
            if element.type == "file" and (element.mime == "text/plain" or not element.mime): 
                file_name = element.name if element.name else "(unknown file name)"
                with open(element.path, "r") as f:
                    file_text = f.read()
                file_input = f"File name: {file_name}\nFile content:\n{file_text}"
                chat_history.append(HumanMessage(content=file_input))
    
    response = await agent.ainvoke({
        "input": input,
        "chat_history": chat_history,
    })
    output = response["output"]
    if response["intermediate_steps"]:
        print("=== INTERMEDIATE STEPS ===")
        print(response["intermediate_steps"])

    ## Update chat history with the new message and response
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=output))

    print(f"=== SENDING RESPONSE: {output} ===")
    # Send the response back to the user
    await cl.Message(content=output).send()
