import logging
from langchain_openai import ChatOpenAI
from threading import Lock
from dotenv import load_dotenv
import os
load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
MODEL_ENDPOINT=os.getenv("MODEL_ENDPOINT")
LLM_MODEL=os.getenv("LLM_MODEL")

class LLMConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info("Initializing LLMConnection instance...")
                    cls._instance = super().__new__(cls)
                    cls._instance.llm = ChatOpenAI(
                        api_key=OPENAI_API_KEY,
                        model=LLM_MODEL,
                        base_url=MODEL_ENDPOINT,
                    )
                    logger.info("LLMConnection instance initialized.")
        return cls._instance
    
    def get_llm(self):
        logger.debug("Retrieving LLM model.")
        return self._instance.llm
    
    def ask_llm(self, query: str):
        return self._instance.llm.invoke(query)