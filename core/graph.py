from typing import cast
import os
import sys
sys.path.insert(-1,"/home/hoatien/hoa/agent_construction_quote/core")
from psycopg_pool import AsyncConnectionPool
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from agents.agent_read_blueprint import AgentState
from langgraph.types import Command
import asyncio

from agents.agent_read_blueprint import AgentReadBluePrint

from dotenv import load_dotenv
load_dotenv()

class OverallState(AgentState):
    output: str

class RootGraph:
    
    def __init__(self):
        self._graph = None
        self._connection_pool = None
        # print("Root Graph initalizing")
        # self._graph = self._create_graph()

    async def _create_graph(self):
        try:
            workflow = StateGraph(OverallState)
            graph1 = AgentReadBluePrint()
            workflow.add_node("graph1", graph1.agent_read_blueprint_graph)
            workflow.add_edge(START,"graph1")
            workflow.add_edge("graph1",END)

            connection_pool = await self._get_connection_pool()

            if connection_pool:
                checkpointer = AsyncPostgresSaver(connection_pool)
                await checkpointer.setup()
            else:
                checkpointer = None
                raise Exception("Connection pool initialization failed")

            self._graph = workflow.compile(checkpointer=checkpointer, name = "PARENT_GRAPH")
        except Exception as graph_error:
            raise graph_error
        return self._graph
    async def get_graph(self):
        if self._graph is None:
            return await self._create_graph()
        return self._graph
    async def _get_connection_pool(self):
        if self._connection_pool is None:
            try:
                max_size = int(os.getenv("POSTGRES_POOL_SIZE"))

                self._connection_pool = AsyncConnectionPool(
                    os.getenv("POSTGRES_URL",""),
                    open = False,
                    max_size = max_size,
                    kwargs={
                        "autocommit": True,
                        "connect_timeout": 5,
                        "prepare_threshold": None,                        
                    },
                )
                await self._connection_pool.open()
            except Exception as db_error:
                print("error in initalize db")
                raise db_error
        print("Connection succes")
        return self._connection_pool
    
    async def get_state_graph(self,session_id):
        config = {"configurable": {"thread_id": session_id}}
        if self._graph is not None:
            return await self._graph.aget_state(config)
        return None
    
    async def make_response(self, decision):
        if self._graph is None:
            self._graph = await self._create_graph()
        session_id = decision.get("session_id","default")
        config = {"configurable": {"thread_id": session_id}}
        a = await self._graph.ainvoke(Command(resume=decision.get("request","")), config=config)
        return a
    
    async def chat(self, request):
        try:
            if self._graph is None:
                self._graph = await self._create_graph()
            user_prompt = request.get("request","")
            session_id = request.get("session_id","default")
            response = await self._graph.ainvoke(input = {"messages":[("human",user_prompt)]}, 
                                                config = {"configurable": {"thread_id": session_id}})
            # print(response)
            return response
        except Exception as e:
            raise e
    
    async def stream_chat(self,request):
        try:
            if self._graph is None:
                self._graph = await self._create_graph()
            user_prompt = request.get("request","")
            session_id = request.get("session_id","default")
            async for token, _ in self._graph.astream(
                {"messages":[("human",user_prompt)]},
                config = {"configurable": {"thread_id": session_id}},
                stream_mode="messages",
            ):
                try:
                    print("tokennnnnnnnnnnnnnnnnnnnnnn", token)
                    yield token.content
                except Exception as token_error:
                    continue

        except Exception as e:
            print(e)
            raise e
        
# async def get_graph():
#     graph = await RootGraph().get_graph()
#     return graph

# graph = asyncio.run(get_graph())


async def main():
    a = RootGraph()
    session = "test4"
    b = await a.chat({"request":"Lên báo giá bản vẽ này "
    "https://maisoninterior.vn/wp-content/uploads/2025/01/ban-ve-van-phong-lam-viec.jpg",
                            "session_id":session})
    o = await a.get_state_graph(session)
    print(f"################## \n {o.values["final_response"]}\n ###########")
    # return b


if __name__=="__main__":
    url = "https://maisoninterior.vn/wp-content/uploads/2025/01/ban-ve-van-phong.jpg"
    try:
        a = asyncio.run(main())

    except Exception as e:
        print(e)


    print("AAAAAA")
    # print("response",a)