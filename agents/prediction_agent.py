import logging
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from typing import List
from utils.agent_prompts import PREDICTION_AGENT_PROMPT
from models.agent_state import AgentState
from models.structured_agent_response import PredictionDecision
from utils.llm_connection import LLMConnection
import datetime
from typing import Any

logger = logging.getLogger(__name__)
llm_model = LLMConnection().get_llm()

class PredictionAgent():
    def __init__(self):
        self.prompt = PREDICTION_AGENT_PROMPT
        self.temp = ""
        self.agent = None
        
    def create_agent(self, model):
        if not self.agent:
            logger.info("Creating Prediction Agent...")
            self.agent = create_react_agent(
                model=model,
                prompt=self.prompt,
                response_format=PredictionDecision,
                tools=[]
            )
        
    def ask_agent(self, state: AgentState) -> dict[str, Any] | Any:
        logger.info("Invoking Prediction Agent...")
        return self.agent.invoke(state)
        
prediction_agent = PredictionAgent()

def final_analysis_node(state: AgentState) -> AgentState:
    """Generate final comprehensive analysis"""
    logger.info("Prediction Node: Generating final comprehensive analysis.")
    
    fundamental_completed = state.get("analysis_results", {}).get("fundamental", {}).get("status") == "completed"
    technical_completed = state.get("analysis_results", {}).get("technical", {}).get("status") == "completed"
    
    if fundamental_completed or technical_completed:
        logger.info("Prediction Node: Fundamental or technical analysis completed. Creating and invoking agent.")
        prediction_agent.create_agent(llm_model)
        
        prediction = prediction_agent.ask_agent(state)
        logger.info(f"Prediction Node Response: {prediction}")
        
        if "final_recommendation" not in state:
            state["final_recommendation"] = {}
            
        state["final_recommendation"] = {
            "action": prediction['structured_response'].action,
            "confidence": prediction['structured_response'].confidence,
            "explanation": prediction['structured_response'].explanation
        }
        logger.info("Prediction Node: Final recommendation generated.")
        
        state['next_agent'] = 'supervisor'
        return {
            **state,
            'messages': [prediction['messages'][-1]],
            'next_agent': 'supervisor'
        }
    else:
        logger.warning("Prediction Node: Analysis incomplete. Skipping prediction.")
        return {
            'messages': [
                HumanMessage(content="Analysis incomplete. Either fundamental or technical analysis required.")
            ],
            'next_agent': 'supervisor'
        }