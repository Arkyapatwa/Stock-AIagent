import logging
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import END

from typing import List
from utils.agent_prompts import SUPERVISOR_AGENT_PROMPT
from models.agent_state import AgentState
from models.structured_agent_response import SupervisorDecision
from utils.llm_connection import LLMConnection
import datetime
from typing import Any

logger = logging.getLogger(__name__)
llm_model = LLMConnection().get_llm()

class SupervisorAgent():
    def __init__(self):
        self.prompt = SUPERVISOR_AGENT_PROMPT
        self.temp = ""
        self.agent = None

    def create_agent(self, model, options):
        if not self.agent:
            logger.info("Creating Supervisor Agent...")
            self.agent = create_react_agent(
                model=model,
                prompt=self.prompt.replace('Enum-Options', options),
                response_format=SupervisorDecision,
                tools=[],
                # callbacks=[delay_execution_10]
            )
        
    def ask_agent(self, state: AgentState) -> dict[str, Any] | Any:
        logger.info("Invoking Supervisor Agent...")
        return self.agent.invoke(state)
    
supervisor_agent = SupervisorAgent()

def supervisor_node(state: AgentState) -> AgentState:
    logger.info("Supervisor Node: Determining next agent.")
    options = "fundamental_analysis_agent,technical_analysis_agent,final_analysis_agent,FINISH"
    supervisor_agent.create_agent(llm_model, options)
    
    final_recommendation = state['final_recommendation']
    if 'action' in final_recommendation:
        return {
            'next_agent': "FINISH"
        }

    response = supervisor_agent.ask_agent(state)
    logger.info(f"Supervisor Node: Response: {response}")
    
    if response['structured_response'].next_agent in options.split(","):
        next_agent = response['structured_response'].next_agent
        logger.info(f"Supervisor Node: Next agent determined: {next_agent}")
    else:
        next_agent = 'FINISH'
        logger.info("Supervisor Node: No specific next agent, finishing.")
    state['next_agent'] = next_agent
    return {
        'next_agent': next_agent
    }