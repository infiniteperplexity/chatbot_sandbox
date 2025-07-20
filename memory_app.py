# The idea here is I'm going to implement something like the Mem0 system
import json
import chainlit as cl
from langchain_core.tools import tool 
from tools import create_react_tool_agent
from chainlit_tools import files_to_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import app_memory_hook
from mem0_tools import ChatHistorySummarizer, Mem0izer

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
## Maybe break out summarizer and just keep it separate?
summarizer = ChatHistorySummarizer(llm=agent.llm)
mem0izer = Mem0izer(llm=agent.llm)

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
    input_chat_history = [msg for msg in chat_history] # at some point, we could apply some filter logic


    ## modify the view of the chat history in various ways
    input_chat_history.extend(files_to_messages(message))  # Add file attachments to the chat history
    input_chat_history = summarize(input_chat_history)
    ## Note that in this setup, we aren't actually adding the files to the chat history...
    memory_message = SystemMessage(content=apply_mem0_operations(input)) # at the moment, this can't memorize facts from files
    ## I think my brain might be getting tired...let's go back to this in a bit.
    input_chat_history - [memory_message] + input_chat_history
    
    response = await agent.ainvoke({
        "input": input,
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


## Mem0 consists of a memory store and these four operations, basically.
# Actually, summarization is also part of it, but I don't know if the library actively implements that.

## These should all probably use the structured output API.
extract_facts_prompt_template = """
You are a Personal Information Organizer, specialized in accurately storing facts, user memories, and preferences. Your primary role is to extract relevant pieces of information from conversations and organize them into distinct, manageable facts. …  

Input: Yesterday, I had a meeting with John at 3pm. We discussed the new project.  
Output: {"facts" : ["Had a meeting with John at 3pm", "Discussed the new project"]}  
…
Return the facts and preferences in a json format as shown above.
"""

prepare_updates_prompt_template = """
You are a smart memory manager which controls the memory of a system.
You can perform four operations: (1) add … (2) update … (3) delete … (4) no change.
Compare newly retrieved facts with the existing memory. For each new fact, decide whether to:
- ADD …
- UPDATE …
- DELETE …
- NONE …
Return the updated memory in JSON format with id/text/event (and old_memory if UPDATE).
"""

summarization_prompt = """
Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.

EXAMPLE
Current summary:
The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good.

New lines of conversation:
Human: Why do you think artificial intelligence is a force for good?
AI: Because artificial intelligence will help humans reach their full potential.

New summary:
The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.
END OF EXAMPLE

Current summary:
{summary}

New lines of conversation:
{new_lines}

New summary:

"""
memories = {}

def summarize(chat_history):
    pass
    return chat_history

# The example I saw simply ran a post-processing step that applies a structured schema, which is actually kind of a good idea in general.
# However, given that these steps are already split off from the main conversation flow, maybe they simply get their own agent.
# structured_llm = model.with_structured_output(ResponseSchema, method="json_schema")

def extract_facts(messages):
    pass
    return []

def retrieve_memories(messages):
    pass
    return []

def prepare_updates(facts, memories):
    pass
    return []

def update_memory(updates):
    pass

def apply_mem0_operations(message):
    memory_inputs = extract_facts([message])
    facts = extract_facts(memory_inputs)
    for fact in facts:
        top_facts = retrieve_memories([fact])
        if top_facts:
            updates = prepare_updates(facts, top_facts)
            update_memory(updates)
    context_memories = retrieve_memories(memory_inputs)
    context_text = "\n".join([f"{m.content}" for m in context_memories])
    return context_text