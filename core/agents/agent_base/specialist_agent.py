from abc import ABC, abstractmethod
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class FinalResponse(BaseModel):
    """Format the information of category in the quotation. Donot format the response of agent to user"""

    STT: list[int] = Field(description="The number id of category")
    category: list[str] = Field(
        description="Name of category"
    )
    amount: list[int] = Field(description="The amount of the category")
    size: list[str] = Field(description="The size of the category")
    unit: list [str] = Field(description="The unit of the size")
    material: list[str] = Field(description="The material of the category")
    cost: list[int] = Field(description="The cost of category")
    location: list[str] = Field(description="The location of that category belongs to")


class SpecialistAgentState(MessagesState):
    final_response: FinalResponse
    status_step: dict
    retry: int

class SpecialistAgent:
    
    def __init__(self,
                 llm = None,
                 system_prompt:str = "",
                 name: str = "",
                 description: str = "",
                 tools:list = [],
                 ):
        self.llm = llm
        self.system_prompt = system_prompt
        self.description = description
        self.tools = tools
        self.name = name


    def _create_graph(self):
        pass

    def _router(self):
        pass

    def _emmit_state(self,state:SpecialistAgentState):
        pass

    def invoke(self, message, config):
        pass


