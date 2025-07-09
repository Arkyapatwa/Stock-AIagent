from typing import Optional
from datetime import datetime
from typing import Any
from langchain_core.messages import HumanMessage
import logging
from agent_workflow import agent_workflow
from typing import AsyncGenerator, Dict

logger = logging.getLogger(__name__)


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
            },
            "next_agent": "supervisor",
            "final_recommendation": {}
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
    
    
    
    
async def run_query_streaming(
    query: str, 
    config: Optional[dict] = None, 
    session_id: Optional[str] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute the agent workflow with streaming"""
    
    start_time = datetime.now()
    
    # Generate config if not provided
    if config is None:
        thread_id = session_id or f"session_{start_time.strftime('%Y%m%d_%H%M%S')}"
        config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Starting streaming financial analysis: {query}")
    
    try:
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "analysis_results": {},
            "metadata": {
                "start_time": start_time.isoformat(),
                "query": query,
                "session_id": config.get("configurable", {}).get("thread_id")
            },
            "next_agent": "supervisor",
            "final_recommendation": {}
        }
        
        # Stream the workflow execution
        final_result = None
        chunk_count = 0
        
        async for chunk in agent_workflow.execute_workflow_streaming(initial_state, config=config):
            chunk_count += 1
            
            # Process and yield each chunk
            logger.info(f"Processing chunk {chunk_count}: {chunk}")
            processed_chunk = chunk
            logger.info(f"Processed chunk {chunk_count}: {processed_chunk}")
            yield processed_chunk
            
            # Store the final result
            if chunk.get("type") != "error":
                final_result = chunk
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Yield final summary
        yield {
            "type": "completion",
            "message": "Analysis completed successfully",
            "final_recommendation": final_result.get("final_recommendation") if final_result else None,
            "analysis_results": final_result.get("analysis_results") if final_result else None,
            "execution_time": execution_time,
            "total_chunks": chunk_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Streaming query error: {str(e)}")
        yield {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def process_workflow_chunk(chunk: Dict[str, Any], chunk_number: int) -> Dict[str, Any]:
    """Process each workflow chunk for streaming"""
    
    try:
        # Extract node information
        node_name = None
        for key in chunk.keys():
            if key in ['supervisor', 'fundamental_analysis', 'technical_analysis', 'final_analysis']:
                node_name = key
                break
        
        if node_name:
            node_data = chunk[node_name]
            
            # Determine chunk type and message
            if node_name == "supervisor":
                next_agent = node_data.get("next_agent", "unknown")
                message = f"Supervisor routing to: {next_agent}"
                chunk_type = "routing"
                
            elif node_name == "fundamental_analysis":
                message = "Performing fundamental analysis..."
                chunk_type = "analysis"
                
            elif node_name == "technical_analysis":
                message = "Performing technical analysis..."
                chunk_type = "analysis"
                
            elif node_name == "final_analysis":
                message = "Generating final recommendation..."
                chunk_type = "synthesis"
                
            else:
                message = f"Processing {node_name}..."
                chunk_type = "processing"
            
            return {
                "type": chunk_type,
                "node": node_name,
                "message": message,
                "chunk_number": chunk_number,
                "data": node_data,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            # Handle other chunk types
            return {
                "type": "update",
                "message": "Processing workflow step...",
                "chunk_number": chunk_number,
                "data": chunk,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Chunk processing error: {str(e)}")
        return {
            "type": "error",
            "error": f"Error processing chunk: {str(e)}",
            "chunk_number": chunk_number,
            "timestamp": datetime.now().isoformat()
        }
