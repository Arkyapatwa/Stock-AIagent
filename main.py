from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator
import json
from datetime import datetime
import logging
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.chatQuery import ChatQuery

from services.query_service import run_query, run_query_streaming

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def test():
    logger.info("Test endpoint called.")
    return "hello world"


@app.post(
    "/predict_signal"
)
@limiter.limit("1/minute")
def predict_signal(query: str, request: Request) -> JSONResponse:
    logger.info(f"Predict signal endpoint called with query: {query}")
    response = run_query(query)
    logger.info(f"Predict signal endpoint returned response: {response}")
    return JSONResponse(content=response, status_code=200)

@app.post(
    "/predict_signal_stream"
)
@limiter.limit("1/minute")
async def predict_signal_stream(chatQuery: ChatQuery, request: Request) -> StreamingResponse:
    query = chatQuery.query
    logger.info(f"Streaming predict signal endpoint called with query: {query}")
    
    async def generate_prediction_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response for signal prediction"""
        
        try:
            # Start streaming
            logger.info("Starting streaming prediction...")
            
            async for chunk in run_query_streaming(query):
                # Format as Server-Sent Events (SSE)
                chunk_json = json.dumps(chunk, default=str)
                logger.info(f"Streaming chunk: {chunk_json}")
                yield f"data: {chunk_json}\n\n"
            
            # Send final completion signal
            yield f"data: {json.dumps({'type': 'stream_end', 'message': 'Stream completed'})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming prediction error: {str(e)}")
            error_chunk = {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_prediction_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)