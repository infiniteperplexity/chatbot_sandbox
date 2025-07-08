from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def tool_method(func):
    """Mark a method to be converted to a LangChain tool"""
    func._is_tool = True
    return func

def tool_manager(cls):
    """Class decorator that converts marked methods to LangChain tools"""
    original_init = cls.__init__
    
    def _new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if not hasattr(self, '_langchain_tools'):
            self._langchain_tools = []
        self._register_tools()

    def _register_tools(self):
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, '_is_tool'):
                tool = StructuredTool.from_function(func=method)
                self._langchain_tools.append(tool)
    
    
    def get_tools(self):
        """Return the list of LangChain tools"""
        return self._langchain_tools.copy()  # Return a copy to prevent

    cls.__init__ = _new_init
    cls._register_tools = _register_tools
    cls.get_tools = get_tools
    return cls


def create_react_tool_agent(
    model: str = "gpt-4.1",
    api_key: str = None,
    tools: list = [],
    return_intermediate_steps: bool = True
):
    llm = ChatOpenAI(model=model, openai_api_key=api_key)
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name = "chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name = "agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(
        llm = llm,
        tools = tools,
        prompt = prompt,
    )
    executor = AgentExecutor(
        agent = agent,
        tools = tools,
        return_intermediate_steps = return_intermediate_steps,
    )
    return executor