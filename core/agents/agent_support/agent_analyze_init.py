from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from agentic_rag import AgenticRag
from langchain_core.messages import HumanMessage,ToolMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """
Bạn là 1 trợ lý có tác vụ đọc bản vẽ kỹ thuật về nhà cửa. Nhiệm vụ của bạn bao gồm: trích xuất thông tin trong bản vẽ, Đưa ra 1 số phong cách, vật liệu có thể dược sử dụng trong bản vẽ. 
Các thông tin bạn cần trích xuất bao gồm: Có những phòng nào trong bản vẽ, tỉ lệ bản vẽ là bao nhiêu(nếu có).
Đối với việc đưa ra phong cách, vật liệu: Bạn cần truy xuất tài liệu được cung cấp và đưa ra kết luận.
"""

class ResponseForAgentAnalyzeInit(BaseModel):
    """Format the information of category in the quotation. Donot format the response of agent to user"""

    STT: list[int] = Field(description="The number id of room")
    category: list[str] = Field(
        description="Name of Room"
    )
    location: list[str] = Field(description="The location of the room in the blueprint")

class ResponseOfStyle(BaseModel):
    style: list[str] = Field(description="The styles in the extracted documents")
    material: list[str] = Field(description="The materials can use which are extracted from documents")
    


class AgentAnalyzeInitState(MessagesState):
    response_of_room: ResponseForAgentAnalyzeInit
    response_of_style: ResponseOfStyle
    link_of_document: str = Field(description="the link of the document source")
    link_of_imnage: str = Field(description="The link of the blueprint")

class AgentAnalyzeInit:
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
        self._graph = None
            


    async def extracted_knowledge(self, state: AgentAnalyzeInitState):
        format_llm = self.llm.with_structured_output(ResponseOfStyle)
        knowledge = """
                    Phong cách có thể sử dụng: Cổ điển, Tân cổ điển,hiện đại.
                    Vật liệu có thể sử dụng: gỗ
                    """
        
        response = AIMessage(content = knowledge)
        format_response = await format_llm.ainvoke([HumanMessage(content=knowledge)])
        state["messages"].append(response)
        state["response_of_style"] = format_response
        return state
    

    async def extracted_room(self, state:AgentAnalyzeInitState):
        format_llm = self.llm.with_structured_output(ResponseForAgentAnalyzeInit)
        rooms = "Trong bản vẽ có phòng ngủ master (nằm ở hướng tây, cạnh bên trái phòng khách) phòng khách, " \
                "năm ở trung tâm của bản vẽ. " \
                "Phòng ngủ 2 nằm ở cạnh bên phải phòng khách"
        
        response = AIMessage(content = rooms)
        format_response = await format_llm.ainvoke([HumanMessage(content=rooms)])
        state["messages"].append(response)
        state["response_of_room"] = format_response
        return state
    

    async def _create_graph(self):
        workflow = StateGraph(AgentAnalyzeInitState)

        workflow.add_node("room_count", self.extracted_room)
        workflow.add_node("knowledge", self.extracted_knowledge)

        workflow.set_entry_point("room_count")
        workflow.add_edge("room_count","knowledge")
        workflow.add_edge("knowledge",END)

        graph = workflow.compile()
        return graph

    async def invoke(self, url_of_image, url_of_document):
        if self._graph is None:
            self._graph = await self._create_graph()
            print("succes")
            print(self._graph)
        state = AgentAnalyzeInitState(link_of_document = url_of_document,
                                      link_of_imnage = url_of_image,
                                      messages = [])
        state["messages"].append(HumanMessage(content = ""))
        response = await self._graph.ainvoke(state) 
        return response


async def main():
    llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-preview-05-20",
                temperature=0.1,
                max_retries=1,
            )
    agent = AgentAnalyzeInit(llm = llm,
                         system_prompt=SYSTEM_PROMPT,
                         name = "InitAgent",
                         description="")
    a = await agent.invoke("","")
    return a

if __name__=="__main__":

    import asyncio
    a = asyncio.run(main())
    print("response",a)
        