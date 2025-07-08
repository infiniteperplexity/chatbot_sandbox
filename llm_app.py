# Now let's modify it so there's an actuall LLM involved.
import json
import chainlit as cl
from tools import create_react_tool_agent

with open("config.json", "r") as f:
    config = json.load(f)

model = config["openai"]["default_model"]
api_key = config["openai"]["api_key"]

agent = create_react_tool_agent(
    model=model,
    api_key=api_key,
)

@cl.on_message
async def on_message(message: cl.Message):
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    response = (await agent.ainvoke({"input": message.content}))["output"]
    print(f"=== SENDING RESPONSE: {response} ===")
    await cl.Message(content=response).send()