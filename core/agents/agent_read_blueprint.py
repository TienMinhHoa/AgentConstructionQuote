import sys
sys.path.insert(-1,"/home/hoatien/hoa/agent_construction_quote/core")

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import List, cast, Literal, Annotated
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage,ToolMessage, AIMessage, SystemMessage
from tools.file_handdle_tools import encode_image_from_url
import asyncio
import grpc
load_dotenv()
# llm = ChatOpenAI(model = 'gpt-4o-mini')
@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It is cloudy in NYC, with 5 mph winds in the North-East direction and a temperature of 70 degrees"
    elif city == "sf":
        return "It is 75 degrees and sunny in SF, with 3 mph winds in the South-East direction"
    else:
        raise AssertionError("Unknown city")
    
@tool
def handdle_links(
    url: Annotated[str, "The url links to the resource that \
                            Agent need to handdle",],
    user_request: Annotated[str, "The user's request"]
):
    """
    Recieve an url of a image and process the request of user
    """


class WeatherResponse(BaseModel):
    """Respond to the user with this"""

    STT: list[int] = Field(description="The number id of category")
    category: list[str] = Field(
        description="Name of category"
    )
    cost: list[int] = Field(description="The cost of category")


class AgentState(MessagesState):
    final_response: WeatherResponse

class AgentReadBluePrint:
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0,
                max_retries=1,
            )
        self.tools = [get_weather,handdle_links]
        self.model_with_tools = self.llm.bind_tools(self.tools)
        self.model_with_structured_output = self.llm.with_structured_output(WeatherResponse)
        self.initailize()
    
    def initailize(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self.call_model)
        workflow.add_node("respond", self.respond)
        workflow.add_node("file_process",self.file_process_node)
        # workflow.add_node("tools", ToolNode(tools))

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            self.route,
            ["file_process","agent","respond",END]
        )

        # workflow.add_edge("tools", "agent")
        workflow.add_edge("file_process","respond")
        workflow.add_edge("respond", END)
        self.agent_read_blueprint_graph = workflow.compile()

    async def call_model(self,state: AgentState):
        system_message = f"""
                            Your are an assistant that can help user analyze image, use these tools: {self.tools}
                        """
        response = await self.model_with_tools.ainvoke([
            SystemMessage(content = system_message),
            *state["messages"]
        ],)
        return {"messages": [response]}

    async def file_process_node(self,state:AgentState):
        url_file = state["messages"][-1].tool_calls[0]["args"]["url"]
        user_request = state["messages"][-1].tool_calls[0]["args"]["user_request"]
        base64_image = await encode_image_from_url(url_file)

        message = HumanMessage(
        content=[
            {"type": "text", "text": user_request},
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
        response = await self.model_with_structured_output.ainvoke(
            [HumanMessage(content=state["messages"][-1].content)]
        )
        
        return {"final_response": response}


    def route(self,state: AgentState):
        messages = state.get("messages", [])
        if messages and isinstance(messages[-1], AIMessage):
            ai_message = cast(AIMessage, messages[-1])
            print("True")
            if ai_message.tool_calls:
                tool_name = ai_message.tool_calls[0]["name"]
                if tool_name in ["handdle_links", "get_weather"]:
                    if tool_name == "handdle_links":
                        return "file_process"

        if messages and isinstance(messages[-1], ToolMessage):
            return "agent"
        
        return END




async def main():
    agent = AgentReadBluePrint()
    a = await agent.agent_read_blueprint_graph.ainvoke(input={"messages": [("human", "describe the image in this link? https://maisoninterior.vn/wp-content/uploads/2025/01/ban-ve-van-phong.jpg")]})
    return a

if __name__ == "__main__":
    import asyncio
    url = "https://maisoninterior.vn/wp-content/uploads/2025/01/ban-ve-van-phong.jpg"
    a = asyncio.run(main())
    print("response",a)