from typing import cast

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from agents.agent_read_blueprint import AgentState

from agents.agent_read_blueprint import AgentReadBluePrint


class OverallState(AgentState):
    output: str

class RootGraph:
    # def __new__(cls):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(RootGraph, cls).__new__(cls)
    #     return cls.instance
    
    def __init__(self):
        workflow = StateGraph(OverallState)
        graph1 = AgentReadBluePrint()
        workflow.add_node("graph1", graph1.agent_read_blueprint_graph)
        # memory = MemorySaver()

        workflow.add_edge(START,"graph1")
        workflow.add_edge("graph1",END)

        self.graph = workflow.compile()
    
    async def chat(self, request):
        response = await self.graph.ainvoke(input = {"messages":[("human",request)]})
        return response




async def main():
    a = RootGraph()
    b = await a.chat("describe the image in this link? https://maisoninterior.vn/wp-content/uploads/2025/01/ban-ve-van-phong.jpg")
    # return b
import asyncio

if __name__=="__main__":
    url = "https://maisoninterior.vn/wp-content/uploads/2025/01/ban-ve-van-phong.jpg"
    try:
        a = asyncio.run(main())
    except Exception as e:
        print(e)


    print("AAAAAA")
    # print("response",a)