from langchain_openai import ChatOpenAI
from typing import Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END



class State(MessagesState):
    next: str

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: str

class Supervise_graph():

    def __init__(self,llm = ChatOpenAI(model = "gpt-4o-mini"), 
                 agent_members = [],
                 job_description ="", 
                 prompt = ""):
        self.member_names = [member.name for member in agent_members]
        self.member_nodes = [member.graph for member in agent_members]
        self.job_description = [member.description for member in agent_members]
        self.llm = llm
        default_promt = (
    "You are a team supervisor tasked with managing a conversation between the"
    f" following workers: {self.member_names}."
    f"The purpose of them are {self.job_description} respestively "
    "Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status."
)
        if prompt is None or len(prompt) == 0:
            self.prompt = default_promt
        else:
            self.prompt = prompt
        
        self.main_node = self.make_choice()
        self.graph = self.build_graph()
        

    def get_member_names(self):
        return self.member_names
    
    
    def make_choice(self):
        member_names = list(self.member_names)
        def supervisor_node(state: State) -> Command[Literal["__end__",*member_names]]:
            messages = [
                {"role": "system", "content": self.prompt},
                *state["messages"]
            ]
            response = self.llm.with_structured_output(Router).invoke(messages)
            goto = response["next"]
            if goto == "FINISH":
                goto = END
            print(f"The agent with name {goto}")
            return Command(goto=goto, update={"next": goto})   
        return supervisor_node
    
    def build_graph(self):
        builder = StateGraph(State)
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", self.main_node)
        for i in range(len(self.member_nodes)):
            builder.add_node(self.member_names[i],self.member_nodes[i])
        graph = builder.compile()
        return graph
    
    def invoke(self,querry):
        response = self.graph.invoke(input={"messages":[("human",querry)]})
        return response
    
    
# if __name__=="__main__":
#     a1 = AgenticRag(name = "Agent For Nothing", description="This is a agent for nothing, it cannot do anything")
#     a2 = AgenticRag(name="AgenticRag")
    
#     supervisor = Supervise_graph(agent_members=[a1,a2])
#     a = supervisor.invoke("What is devops")
#     print(a)