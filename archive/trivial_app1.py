import chainlit as cl

@cl.on_message
async def on_message(message: cl.Message):
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    print("hello world")
    response = "I can't complete your request, but hello world!"
    print(f"=== SENDING RESPONSE: {response} ===")
    await cl.Message(content=response).send()