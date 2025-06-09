from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_chroma import Chroma
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition


from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from typing import Literal


GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)

GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \n"
    "Context: {context}"
)

class GradeDocument(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class AgenticRag:
    def __init__(self,
                 name = "Agentic rag",
                 description = "This agent is used for Retrival information about devops knowledge"):
        retriever = self._init_db()
        self.graph = None
        self.retriever_tool = create_retriever_tool(
            retriever,
            "retrieve_devops_knowledge",
            "Search and return information about knowledge of devops",
        )
        self.name = name
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.description = description
        self.chat_model = self.llm.bind_tools([self.retriever_tool])
        self.grade_model = self.llm.with_structured_output(GradeDocument)
        if self.graph is None:
            self.graph = self._create_graph()
    
    def _init_db(self):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db",
        )
        retriever = vector_store.as_retriever()
        return retriever
    
    def generate_query_or_respond(self,state: MessagesState):
        """Call the model to generate a response based on the current state. Given
        the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
        """
        response = self.chat_model.invoke(state["messages"])
        return {"messages": [response]}
    
    def _grade_documents(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = GRADE_PROMPT.format(question=question, context=context)
        response = (
            self.grade_model.invoke(
                [{"role": "user", "content": prompt}]
                )
            )
        score = response.binary_score

        if score == "yes":
            return "generate_answer"
        else:
            return "rewrite_question"
        
    def rewrite_question(self,state: MessagesState):
        """Rewrite the original user question."""
        messages = state["messages"]
        question = messages[0].content
        prompt = REWRITE_PROMPT.format(question=question)
        response = self.chat_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [{"role": "user", "content": response.content}]}
    
    def generate_answer(self,state: MessagesState):
        """Generate an answer."""
        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self.chat_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    def _create_graph(self):
        workflow = StateGraph(MessagesState)

        # Define the nodes we will cycle between
        workflow.add_node("generate_query_or_respond",self.generate_query_or_respond)
        workflow.add_node("retrieve", ToolNode([self.retriever_tool]))
        workflow.add_node("rewrite_question",self.rewrite_question)
        workflow.add_node("generate_answer",self.generate_answer)
        workflow.add_edge(START, "generate_query_or_respond")
        # Decide whether to retrieve
        workflow.add_conditional_edges(
            "generate_query_or_respond",
            tools_condition,
            {
                "tools": "retrieve",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "retrieve",
            self._grade_documents,
        )
        workflow.add_edge("generate_answer", END)
        workflow.add_edge("rewrite_question", "generate_query_or_respond")
        
        graph = workflow.compile()
        return graph
        

if __name__=="__main__":
    a = AgenticRag()