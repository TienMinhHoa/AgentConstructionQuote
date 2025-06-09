from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import Annotated
from supervise_agent import Supervise_graph
from langchain.tools import tool
from langchain_core.messages import HumanMessage,ToolMessage, AIMessage, SystemMessage
from tools.file_handdle_tools import encode_image_from_url


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


class FinalResponse(BaseModel):
    """Format the information of category in the quotation. Donot format the response of agent to user"""

    STT: list[int] = Field(description="The number id of category")
    category: list[str] = Field(
        description="Name of category"
    )
    amount: list[int] = Field(description="The amount of the category")
    size: list[str] = Field(description="The size of the category")
    unit: list [str] = Field(description="The unit of the size")


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
                 duty = ""
                 ):
        self.llm = llm
        self.system_prompt = system_prompt
        self.description = description
        self.tools = tools
        self.name = name
        self.supervisor = Supervise_graph()
        self.duty = duty



    async def call_model(self, state):
        context = ""
        for tool in self.tools:
            context+=f"{tool.name}, description; {tool.description}\n"
        response = await self.model_with_tools.ainvoke([
            SystemMessage(content = self.system_prompt.format(context = context)),
            *state["messages"]
        ],)
        return {"messages": [response]}

    async def read_quotation(self, state):
        url = state["messages"][-1].tool_calls[0]["args"]["url"]
        base64_image = await encode_image_from_url(url)
        message = HumanMessage(
            content=[
                {"type": "text", "text": self.duty},
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
    
    async def format_response(self, state):
        content = state["messages"][-1].tool_calls[0]["args"]["message"]
        format_llm = self.llm.with_structured_output(FinalResponse)
        response = await format_llm.ainvoke([HumanMessage(content = content)])

        tool_message = ToolMessage(
            content= f"Đã format lại kết quả , bạn hãy thông báo đến người dùng đi ",
            tool_call_id=state["messages"][-1].tool_calls[0]["id"]
        )

        state["messages"].append(tool_message)
        # breakpoint()
        return state
    
    async def check_consistent(self, state)


    def _create_graph(self):
        pass

    def _router(self):
        pass

    def _emmit_state(self,state:SpecialistAgentState):
        pass

    def invoke(self, message, config):
        pass


if __name__=="__main__":
    duty =  "bạn là 1 agent chuyên đọc bản vẽ về phòng ngủ, dựa vào bản vẽ này, với nhứng thông tin đã được cung cấp như sau: " \
            "Phòng ngủ 1 nằm ở góc trái trên cùng."\
            " Bạn hãy liệt kê các hạng  mục nội thất bên trong phòng ngủ này, đếm sôs lượng, đưa ra kích thước các hạng mục đó "
    