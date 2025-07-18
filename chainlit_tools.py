import os
import json
import chainlit as cl
from chainlit.input_widget import Select
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def files_to_messages(msg):
    if not msg.elements:
        return []
    messages = []
    for element in msg.elements:
        if element.type == "file" and (element.mime == "text/plain" or not element.mime):
            file_name = element.name if element.name else "(unknown file name)"
            with open(element.path, "r") as f:
                file_text = f.read()
            file_input = f"File name: {file_name}\nFile content:\n{file_text}"
            messages.append(HumanMessage(content=file_input))
    return messages

class ChatHistorySaver:
    def __init__(self, subdir="saved_threads"):
        self.subdir = subdir
        os.makedirs(self.subdir, exist_ok=True)
        self.save_action = cl.Action(
            name="save_chat_history",
            icon="hard-drive-download",
            payload={"action": "save"},
            label="Save Chat History"
        )
        self.load_action = cl.Action(
            name="load_chat_history",
            icon="hard-drive-upload",
            payload={"action": "load"},
            label="Load Chat History"
        )
    
    async def work_around_end_task_bug(self):
        await cl.context.emitter.task_end()

    async def save_chat_history(self, chat_history):
        name_msg = await cl.AskUserMessage(
            content="Please type a name for this chat history, or leave blank to cancel:",
            raise_on_timeout=False,
        ).send()

        if not name_msg or not name_msg["output"]:
            await cl.Message("Cancelled: no name provided.").send()
            await self.work_around_end_task_bug()
            return
        else:
            raw_name = name_msg["output"]

        filename = raw_name + ".json"
        filepath = os.path.join(self.subdir, filename)

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
                await self.work_around_end_task_bug()
                return

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([m.dict() for m in chat_history], f, indent=2, ensure_ascii=False)

        await cl.Message(f"✅ Chat history saved to `{filepath}`").send()
        await self.work_around_end_task_bug()
        

    async def load_chat_history(self):
        new_history = []
        files = [f for f in os.listdir(self.subdir) if f.endswith(".json")]
        if not files:
            await cl.Message(content="No saved threads found.").send()
            return

        actions = [
            cl.Action(name=f"file_{i}", label=f, icon="file", payload={"value": f})
            for i, f in enumerate(files)
        ]
        actions.append(cl.Action(name="cancel_load", label="❌ Cancel", payload={"value": "cancel"}))

        selected = await cl.AskActionMessage(
            content="Select a chat-history file to load:",
            actions=actions,
        ).send()
        if not selected or selected["name"] == "cancel_load":
            await cl.Message(content="Selection cancelled.").send()
            await self.work_around_end_task_bug()
            return None

        filename = selected["payload"]["value"]
        path = os.path.join(self.subdir, filename)
        try:
            with open(path, "r") as f:
                history = json.load(f)

            for msg in history:
                if msg["type"] == "human":
                    new_history.append(HumanMessage(**msg))
                elif msg["type"] == "ai":
                    new_history.append(AIMessage(**msg))
                elif msg["type"] == "system":
                    new_history.append(SystemMessage(**msg))
            await cl.Message(content=f"Loaded history from **{filename}**").send()
        except Exception as e:
            await cl.Message(content=f"Error loading file: {e}").send()
        await self.work_around_end_task_bug()
        return new_history