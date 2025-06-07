from abc import ABC, abstractmethod
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field





class SpecialistAgentState(MessagesState):
    final_response:

class SpecialistAgent(ABC):
    
    def __init__(self,
                 llm = None,
                 system_prompt:str = "",
                 name: str = "",
                 description: str = "",
                 tools:list = [],
                 agent_state = MessagesState
                 ):
        self.llm = llm
        self.system_prompt = system_prompt
        self.description = description
        self.tools = tools
        self.name = name
        self.agent_state = agent_state

    @abstractmethod
    def _create_graph(self):
        pass

    @abstractmethod
    def _router(self, )