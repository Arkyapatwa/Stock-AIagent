from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from agents.fundamental_analysis_agent import fundamental_agent_node
from agents.prediction_agent import final_analysis_node
from agents.supervisor_agent import supervisor_node
from agents.technical_analysis_agent import technical_agent_node
from models.agent_state import AgentState

from typing import Optional
from datetime import datetime
from typing import Any
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)

class AgentWorkflow():
    def __init__(self, agent_memory: InMemorySaver):
        self.workflow = None
        self.memory = agent_memory
        self.compiled_workflow = None

    def create_workflow(self):
        self.workflow = StateGraph(AgentState)
    
        # Add nodes
        self.workflow.add_node("supervisor", supervisor_node)
        self.workflow.add_node("fundamental_analysis", fundamental_agent_node)
        self.workflow.add_node("technical_analysis", technical_agent_node)
        self.workflow.add_node("final_analysis", final_analysis_node)
        
        
        self.workflow.add_edge(START, "supervisor")
        self.workflow.add_conditional_edges(
            "supervisor",
            self.route_next_agent,
            {
                "fundamental_analysis": "fundamental_analysis",
                "technical_analysis": "technical_analysis", 
                "final_analysis": "final_analysis",
                END: END
            }
        )
        
        self.workflow.add_edge("fundamental_analysis", "supervisor")
        self.workflow.add_edge("technical_analysis", "supervisor")
        self.workflow.add_edge("final_analysis", "supervisor")
        self.workflow.add_edge("supervisor", END)
        
        self.compiled_workflow = self.workflow.compile(checkpointer=self.memory)
    
    def execute_workflow(self, state: AgentState, config):
        return self.compiled_workflow.invoke(state, config=config)
        
    def route_next_agent(self, state: AgentState):
        """Route to next agent based on supervisor decision"""
        next_agent = state.get("next_agent")
        
        if "fundamental_analysis_agent" in next_agent:
            return "fundamental_analysis"
        elif "technical_analysis_agent" in next_agent:
            return "technical_analysis"
        elif "final_analysis_agent" in next_agent:
            return "final_analysis"
        else:
            return END
        
        
agent_workflow = AgentWorkflow(InMemorySaver())
agent_workflow.create_workflow()


    
def run_query(query: str, config: Optional[dict] = None, session_id: Optional[str] = None) -> dict:
    """Execute the agent workflow"""

    start_time = datetime.now()
        
    # Generate config if not provided
    if config is None:
        thread_id = session_id or f"session_{start_time.strftime('%Y%m%d_%H%M%S')}"
        config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Starting financial analysis: {query}")
    
    try:
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "analysis_results": {},
            "metadata": {
                "start_time": start_time.isoformat(),
                "query": query,
                "session_id": config.get("configurable", {}).get("thread_id")
            }
        }
        
        result = agent_workflow.execute_workflow(initial_state, config=config)

        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
                "final_recommendation": result.get("final_recommendation"),
                "analysis_results": result.get("analysis_results"),
                "messages": [msg.content for msg in result.get("messages", [])],
                "metadata": {
                    **result.get("metadata", {}),
                    "execution_time": execution_time,
                    "end_time": datetime.now().isoformat()
                }
            }
    except Exception as e:
        return {"error": str(e)}