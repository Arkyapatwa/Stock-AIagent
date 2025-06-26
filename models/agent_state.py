from typing import Annotated, List, TypedDict, Union, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_agent: str
    analysis_results: dict
    final_recommendation: Optional[str]
    metadata: dict