from fastapi import FastAPI, Request
import logging
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from agent_workflow import run_query

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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)