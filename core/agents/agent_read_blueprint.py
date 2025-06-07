import sys
sys.path.insert(-1,"/home/hoatien/hoa/agent_construction_quote/core")

from pydantic import BaseModel, Field
import uuid
from langgraph.graph import MessagesState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import List, cast, Literal, Annotated, Optional
from langgraph.types import interrupt, Command
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage,ToolMessage, AIMessage, SystemMessage
from tools.file_handdle_tools import encode_image_from_url
import asyncio
from system_prompt.read_blue_print_prompt import *
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()
# llm = ChatOpenAI(model = 'gpt-4o-mini')

@tool
def read_images(
    url: Annotated[str, "The url links to the resource that \
                            Agent need to handdle",]
):
    """
    This tool is used for reading image of user
    """

@tool
def format_repond(
    message: Annotated[str,"The content of reponse of agent that need to be reformated"]
):
    """
    Format the information about the quotation  
    """

class WeatherResponse(BaseModel):
    """Format the information of category in the quotation. Donot format the response of agent to user"""

    STT: list[int] = Field(description="The number id of category")
    category: list[str] = Field(
        description="Name of category"
    )
    amount: list[int] = Field(description="The amount of the category")
    size: list[str] = Field(description="The size of the category")
    unit: list [str] = Field(description="The unit to measure size")
    material: list[str] = Field(description="the material of the category")
    cost: list[int] = Field(description="The cost of category")
    location: list[str] = Field(description="The location of that category belongs to")

class AgentState(MessagesState):
    final_response: WeatherResponse

class AgentReadBluePrint:
    
    def __init__(self, planning = None):
        self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-preview-05-20",
                temperature=0.1,
                max_retries=1,
            )
        self.planning = planning
        # self.llm = ChatOpenAI(model = 'gpt-4o-mini')
        self.tools = [read_images, format_repond]
        self.model_with_tools = self.llm.bind_tools(self.tools)
        self.model_with_structured_output = self.llm.with_structured_output(WeatherResponse)
        self.planning_prompt = PLANNING_PROMPT
        self.initialize()


    
    
    def initialize(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self.call_model)
        workflow.add_node("respond", self.respond)
        workflow.add_node("file_process",self.file_process_node)
        workflow.add_node("analyze",self.analyze_blueprint_node)
        workflow.add_node("humman",self.human_approval)
       

        workflow.set_entry_point("humman")
        workflow.add_edge("humman","agent")
        workflow.add_edge("agent",END)
        workflow.add_edge("file_process", "analyze")
        
        # workflow.add_conditional_edges(
        #     "agent",
        #     self.route,
        #     ["file_process","agent","respond",END]
        # )
        workflow.add_edge("analyze","agent")
        workflow.add_edge("respond", "agent")
        self.agent_read_blueprint_graph = workflow.compile()
    


    async def call_model(self,state: AgentState):
        context = ""
        for tool in self.tools:
            context+=f"{tool.name}, description; {tool.description}\n"
        response = await self.model_with_tools.ainvoke([
            SystemMessage(content = SYSTEM_PROMPT.format(context = context)),
            *state["messages"]
        ],)
        return {"messages": [response]}
    

    async def human_approval(self,state: AgentState):
        print("hellp")
        is_approved = interrupt(
            {
                "question": "Is this correct?",
                # Surface the output that should be
                # reviewed and approved by the human.
                "llm_output": state["messages"]
            }
        )
        print("#############",is_approved)

        if is_approved == "YES":
            print("############ approve ############\n")
            return Command(goto='agent')
        else:
            print("############ not approve ############\n")
            return Command(goto=END)
    
    
    async def analyze_blueprint_node(self, state: AgentState):
        response = await self.model_with_tools.ainvoke(
            [
                SystemMessage(content = self.planning_prompt),
                *state["messages"]
            ]
        )
        content = f"Đây là định hướng của bản báo giá lần này: {response.content}."

        state["messages"].append(HumanMessage(content = content))
        
        print("This is analyze ######## \n",response)
        return state
        

    async def file_process_node(self,state:AgentState):
        print("#################\n file processing \n ##############")
        url_file = state["messages"][-1].tool_calls[0]["args"]["url"]
        base64_image = await encode_image_from_url(url_file)

        message = HumanMessage(
        content=[
            {"type": "text", "text": "Đọc bản vẽ này cho tôi "},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
            ],
        )

        response = await self.llm.ainvoke([message])
        tool_message = ToolMessage(
            content= response.content,
            tool_call_id=state["messages"][-1].tool_calls[0]["id"]
        )
        state["messages"].append(tool_message)
        return state


    async def respond(self,state: AgentState):
        content = state["messages"][-1].tool_calls[0]["args"]["message"]
        response = await self.model_with_structured_output.ainvoke(
            [HumanMessage(content=content)]
        )
        print(f"##########formating##########\n {response}\n #####################\n")
        state["final_response"] = response
        tool_message = ToolMessage(
            content= f"Đã format lại kết quả , bạn hãy thông báo đến người dùng đi ",
            tool_call_id=state["messages"][-1].tool_calls[0]["id"]
        )
        state["messages"].append(tool_message)
        # breakpoint()
        return state

    def route(self,state: AgentState):
        messages = state.get("messages", [])
        if messages and isinstance(messages[-1], AIMessage):
            ai_message = cast(AIMessage, messages[-1])
            if ai_message.tool_calls:
                tool_name = ai_message.tool_calls[0]["name"]
                if tool_name in ["read_images", "format_repond"]:
                    if tool_name == "read_images":
                        return "file_process"
                    if tool_name == "format_repond":
                        return "respond"
        if messages and isinstance(messages[-1], ToolMessage):
            return "agent"
    
        return END



async def main():
    agent = AgentReadBluePrint()
    config = {"configurable": {"thread_id": "1"}}
    a = await agent.agent_read_blueprint_graph.ainvoke(input={"messages": [("human", "hello")]}, config = config)
    print(a["__interrupt__"])
    return a

if __name__ == "__main__":
    import asyncio
    a = asyncio.run(main())
    print("response",a)