from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage,ToolMessage, AIMessage, SystemMessage\


class CheckResponse(BaseModel):
    result: str = Field(description="Consistent score: 'YES' if 2 reponses are consistent, or 'NO' if 2 responses are not consistent")

class AgentCheckConsistent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.1,
            max_retries=1,
        )
        self.llm = self.llm.with_structured_output(CheckResponse)

    async def check(self, input_):
        format_input = f"Here is the 2 output from llm, You need to check the consistency of these:\n{input_}"
        result = await self.llm.ainvoke([
            SystemMessage(content = "You need to check the consistency of the output of llm. You will recieve two responses and check them"),
            HumanMessage(content = format_input)
        ])

        return result["result"]