import logging
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from typing import List
from utils.agent_prompts import TECHNICAL_AGENT_PROMPT
from models.agent_state import AgentState
from tools.technical_analysis_tools import technical_tools
from utils.llm_connection import LLMConnection
import datetime
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)
llm_model = LLMConnection().get_llm()

class TechnicalAnalysisAgent():
    def __init__(self):
        self.prompt = TECHNICAL_AGENT_PROMPT
        self.temp = ""
        self.agent = None
        
    def create_agent(self, model):
        if not self.ask_agent:
            logger.info("Creating Technical Analysis Agent...")
            self.agent = create_react_agent(
                model=model,
                tools=technical_tools,
                prompt=self.prompt
            )
        
    def ask_agent(self, state: AgentState) -> dict[str, Any] | Any:
        logger.info("Invoking Technical Analysis Agent...")
        return self.agent.invoke(state)
        
technical_analysis_agent = TechnicalAnalysisAgent()

def technical_agent_node(state: AgentState) -> AgentState:
    logger.info("Technical Analysis Node: Creating and invoking agent.")
    technical_analysis_agent.create_agent(llm_model)

    response = technical_analysis_agent.ask_agent(state)
    logger.info(f"Technical Analysis Node: Agent response: {response}")
    
    state["analysis_results"]["technical"] = {
        "timestamp": datetime.now().isoformat(),
        "agent": "technical_analysis",
        "status": "completed"
    }
    logger.info("Technical Analysis Node: Completed.")
    return {
        'messages': [response['messages'][-1]],
        'next_agent': 'supervisor'
    }