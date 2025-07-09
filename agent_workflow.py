from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from agents.fundamental_analysis_agent import fundamental_agent_node
from agents.prediction_agent import final_analysis_node
from agents.supervisor_agent import supervisor_node
from agents.technical_analysis_agent import technical_agent_node
from models.agent_state import AgentState

from typing import Optional
from datetime import datetime
from typing import Any, Dict, AsyncGenerator
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
                "FINISH": END
            }
        )
        
        self.workflow.add_edge("fundamental_analysis", "supervisor")
        self.workflow.add_edge("technical_analysis", "supervisor")
        self.workflow.add_edge("final_analysis", "supervisor")
        
        self.compiled_workflow = self.workflow.compile(checkpointer=self.memory)
    
    def execute_workflow(self, state: AgentState, config):
        return self.compiled_workflow.invoke(state, config=config)
    
    async def execute_workflow_streaming(
        self, 
        state: AgentState, 
        config: dict
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute workflow with streaming using astream"""
        
        try:
            async for chunk in self.compiled_workflow.astream(state, config=config, stream_mode="values"):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming workflow error: {str(e)}")
            yield {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "type": "error"
            }
        
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
            return "FINISH"
        
        
agent_workflow = AgentWorkflow(InMemorySaver())
agent_workflow.create_workflow()
