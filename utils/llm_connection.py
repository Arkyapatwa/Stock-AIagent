import logging
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from threading import Lock
from dotenv import load_dotenv
import os
load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
MODEL_ENDPOINT=os.getenv("MODEL_ENDPOINT")
LLM_MODEL=os.getenv("LLM_MODEL")

GEMINI_API_KEY=os.environ["GOOGLE_API_KEY"]=os.getenv("GEMINI_API_KEY")
GEMINI_MODEL=os.getenv("GEMINI_MODEL")

LLM_TYPE=os.getenv("LLM_TYPE")

class LLMConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info("Initializing LLMConnection instance...")
                    cls._instance = super().__new__(cls)
                    if LLM_TYPE == "openai":
                        cls._instance.llm = ChatOpenAI(
                            api_key=OPENAI_API_KEY,
                            model=LLM_MODEL,
                            base_url=MODEL_ENDPOINT,
                            temperature=0,
                            top_p=1,
                            max_retries=2
                        )
                    else:
                        print("gemini")
                        cls._instance.llm = ChatGoogleGenerativeAI(
                            model=GEMINI_MODEL,
                            temperature=0,
                            top_p=1,
                            max_retries=2
                        )

                    logger.info("LLMConnection instance initialized.")
        return cls._instance
    
    def get_llm(self):
        logger.debug("Retrieving LLM model.")
        return self._instance.llm
    
    def ask_llm(self, query: str):
        return self._instance.llm.invoke(query)