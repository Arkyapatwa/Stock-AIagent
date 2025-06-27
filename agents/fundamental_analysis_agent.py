import logging
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from typing import List
from utils.agent_prompts import FUNDAMENTAL_AGENT_PROMPT
from models.agent_state import AgentState
from tools.fundamental_analysis_tools import fundamental_tools
from utils.llm_connection import LLMConnection
import datetime
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)
llm_model = LLMConnection().get_llm()

class FundamentalAnalysisAgent():
    def __init__(self):
        self.prompt = FUNDAMENTAL_AGENT_PROMPT
        self.temp = ""
        self.agent = None
        
    def create_agent(self, model):
        if not self.agent:
            logger.info("Creating Fundamental Analysis Agent...")
            self.agent = create_react_agent(
                model=model,
                tools=fundamental_tools,
                prompt=self.prompt
            )
        
    def ask_agent(self, state: AgentState) -> dict[str, Any] | Any:
        logger.info("Invoking Fundamental Analysis Agent...")
        return self.agent.invoke(state)
        
fundamental_analysis_agent = FundamentalAnalysisAgent()
    
def fundamental_agent_node(state: AgentState) -> AgentState:
    logger.info("Fundamental Analysis Node: Creating and invoking agent.")
    fundamental_analysis_agent.create_agent(llm_model)
    
    response = fundamental_analysis_agent.ask_agent(state)
    logger.info(f"Fundamental Analysis Node Response: {response}")
    
    fundamental_result = {
        "timestamp": datetime.now().isoformat(),
        "agent": "fundamental_analysis",
        "status": "completed"
    }
    state["next_agent"] = "supervisor"
    logger.info("Fundamental Analysis Node: Completed.")
    
    return {
        'messages': [response['messages'][-1]],
        'analysis_results': {
            **state.get("analysis_results", {}),  
            "fundamental": fundamental_result      
        },
        'next_agent': 'supervisor'
    }