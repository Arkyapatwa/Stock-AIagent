from pydantic import BaseModel, Field
from typing import Literal

class SupervisorDecision(BaseModel):
    next_agent: Literal[
        "fundamental_analysis_agent", 
        "technical_analysis_agent", 
        "final_analysis_agent", 
        "FINISH"
    ] = Field(description="The next agent to execute in the workflow")
    
class PredictionDecision(BaseModel):
    action: Literal[
        "BUY",
        "SELL",
        "HOLD",
    ] = Field(description="The decision to take on ticker")
    confidence: float = Field(description="The confidence in the decision")
    explanation: str = Field(description="The explanation for the decision")