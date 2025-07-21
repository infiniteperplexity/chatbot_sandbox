# The idea here is I'm going to implement something like the Mem0 system
## Testing was less than thorough...
import json
import chainlit as cl
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from chainlit_tools import files_to_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import app_memory_hook
from mem0_tools import ChatHistorySummarizer, Mem0izer
from langchain_tools import long_division

with open("config.json", "r") as f:
    config = json.load(f)

model = config["openai"]["default_model"]
api_key = config["openai"]["api_key"]

chat_history = []
keep_n_full_messages = 5

agent = create_react_tool_agent(
    model=model,
    api_key=api_key,
    tools=[long_division],
)
# Set up memory system
llm = agent.agent.runnable.steps[2].bound
summarizer = ChatHistorySummarizer(llm=llm)
mem0izer = Mem0izer(llm=llm, api_key=api_key)
# attach memory hooks so they can be accessed in the notebook
app_memory_hook.chat_history = chat_history
app_memory_hook.agent = agent
app_memory_hook.llm = llm
app_memory_hook.summarizer = summarizer
app_memory_hook.mem0izer = mem0izer




@cl.on_chat_start
async def on_chat_start():   
    print("CHAT STARTED")
    chat_history.clear()  # Clear chat history at the start of each chat  
    intro_message = AIMessage(f"Welcome to the Chainlit app! I can perform long division and read file attachments. Try sending me a message or attaching a file.")
    await cl.Message(content=intro_message.content).send()
    
@cl.on_message
async def on_message(message: cl.Message):
    print(f"=== MESSAGE RECEIVED: {message.content} ===")
    input = message.content


    ## Prepare the chat history for the agent
    file_messages = files_to_messages(message) # Add file attachments to the chat history
    older_messages, newer_messages = chat_history[:-keep_n_full_messages], chat_history[-keep_n_full_messages:]
    if len(older_messages) > 0:
        summary_message = summarizer.summarize(older_messages, cumulative=True)
        summary_message = SystemMessage(content=summary_message)
    else:
        summary_message = None

    if file_messages:
        file_message_test = "\n".join(["File Attachments:"]+[msg.content for msg in file_messages])
        current_message_text = f"{file_message_test}\n\n{input}"
    ## Note that in this setup, we aren't actually adding the files to the chat history...
    else:
        current_message_text = input

    memories = mem0izer.apply_mem0_operations(current_message_text)
    if memories:
        memories_message = SystemMessage(content="\n".join([f"{memory.text}" for memory in memories]))
    else:
        memories_message = None

    input_chat_history = newer_messages
    if memories_message:
        input_chat_history = [memories_message] + input_chat_history
    if summary_message:
        input_chat_history = [summary_message] + input_chat_history

    response = await agent.ainvoke({
        "input": current_message_text,
        "chat_history": input_chat_history
    })
    output = response["output"]
    if response["intermediate_steps"]:
        print(response["intermediate_steps"])

    ## Update chat history with the new message and response
    chat_history.append(HumanMessage(content=input))
    chat_history.append(AIMessage(content=output))

    print(f"=== SENDING RESPONSE: {output} ===")
    # Send the response back to the user
    await cl.Message(content=output).send()