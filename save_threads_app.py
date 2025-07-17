# Now we can save and load chat history in a Chainlit app
import os
import json
from operator import sub
import chainlit as cl
from chainlit.input_widget import Slider, Select
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import app_memory_hook

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

# So I can see these variables from a notebook running this app as a thread
app_memory_hook.chat_history = chat_history
app_memory_hook.agent = agent

save_action = cl.Action(
    name="save_chat_history",
    icon="hard-drive-download",
    payload={"action": "save"},
    label="Save Chat History"
)
load_action = cl.Action(
    name="load_thread",
    icon="hard-drive-upload",
    payload={"action": "load"},
    label="Load Chat History"
)

@cl.on_chat_start
async def on_chat_start():   
    chat_history.clear()  # Clear chat history at the start of each chat  
    intro_message = AIMessage(f"Welcome to the Chainlit app!")
    chat_history.append(intro_message)
    await cl.Message(content=intro_message.content, actions=[load_action]).send()


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
    await cl.Message(content=output, actions=[save_action]).send()


@cl.action_callback("save_chat_history")
async def save_chat_history(action):
    """Save the in-memory chat_history to a JSON file chosen by the user."""

    name_msg = await cl.AskUserMessage(
        content="Please type a name for this chat history, or leave blank to cancel:",
        # Note: This actually won't let you leave it blank, so we'll need some other way to cancel.
        raise_on_timeout=False,
    ).send()


    if not name_msg or not name_msg["output"]:
        await cl.Message("Cancelled: no name provided.").send()
        await work_around_end_task_bug()
        return
    else:
        raw_name = name_msg["output"]

    # the chatbot wanted me to sanitize the name
    filename   = raw_name + ".json"
    subdir     = "saved_threads"
    os.makedirs(subdir, exist_ok=True)
    filepath   = os.path.join(subdir, filename)

    # -------------------- 4) if the file exists, ask about overwrite --
    if os.path.exists(filepath):
        overwrite = await cl.AskActionMessage(
            content=(f"A file named **{filename}** already exists. "
                     "Overwrite it?"),
            actions=[
                cl.Action(name="ow_yes", label="✅ Overwrite", payload=True),
                cl.Action(name="ow_no",  label="❌ Choose new name", payload=False),
            ],
        ).send()

        if not overwrite or not overwrite["payload"]:
            await cl.Message("Save cancelled.").send()
            await work_around_end_task_bug()
            return

    # -------------------- 5) write the file --------------------------
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([m.dict() for m in chat_history], f, indent=2, ensure_ascii=False)

    await cl.Message(f"✅ Chat history saved to `{filepath}`").send()
    await work_around_end_task_bug()

@cl.action_callback("load_thread")
async def load_thread(action):
    import os, json
    from langchain.schema import HumanMessage, AIMessage, SystemMessage

    # Step 1: List files
    subdir = "saved_threads"
    files = [f for f in os.listdir(subdir) if f.endswith(".json")]
    if not files:
        await cl.Message(content="No saved threads found.").send()
        return

    # Step 2: Build actions
    actions = [
        cl.Action(name=f"file_{i}", label=f, icon="file", payload={"value": f})
        for i, f in enumerate(files)
    ]
    cancel_action = cl.Action(
        name="cancel_load", 
        label="❌ Cancel", 
        payload={"value": "cancel"}
    )
    actions.append(cancel_action)

    # Step 3: Prompt selection
    selected = await cl.AskActionMessage(
        content="Select a chat-history file to load:",
        actions=actions,
        #timeout=60,
    ).send()
    if not selected or selected["name"] == "cancel_load":
        await cl.Message(content="Selection cancelled.").send()
        await work_around_end_task_bug()
        return

    # Step 4: Load and replay
    filename = selected["payload"]["value"]
    path = os.path.join(subdir, filename)
    try:
        with open(path, "r") as f:
            history = json.load(f)
        chat_history.clear()
        for msg in history:
            if msg["type"] == "human":
                chat_history.append(HumanMessage(**msg))
            elif msg["type"] == "ai":
                chat_history.append(AIMessage(**msg))
            elif msg["type"] == "system":
                chat_history.append(SystemMessage(**msg))
        await cl.Message(content=f"Loaded history from **{filename}**").send()
    except Exception as e:
        await cl.Message(content=f"Error loading file: {e}").send()
    await work_around_end_task_bug()

async def work_around_end_task_bug():
    await cl.context.emitter.task_end()