import logging
import yfinance as yf
import numpy as np
import pandas as pd
import pandas_ta as ta
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool("get_chart_patterns")
def get_chart_patterns(ticker: str) -> str:
    """
    Returns a string of chart patterns for a given ticker for last 20 days.
    
    Args:
        ticker: The stock ticker symbol.
    Returns:
        A string of chart patterns.
    """
    logger.info(f"Fetching chart patterns for {ticker}")
    df = yf.download(ticker, period="1y", multi_level_index=False, interval="1d")
    cdl = df.ta.cdl_pattern(name="all", append=True)
    
    # SMA
    df["SMA_50"] = df.ta.sma(length=50)
    df["SMA_200"] = df.ta.sma(length=200)
    
    # Support Resistance
    df["SR_high"] = df["High"].rolling(20).max()
    df["SR_low"] = df["Low"].rolling(20).min()
    
    # trend
    df["trend"] = np.where(df["SMA_50"] > df["SMA_200"], "up", "down")

    logger.info(f"Successfully fetched chart patterns for {ticker}")
    return df[-20:].to_string()


technical_tools = [
    get_chart_patterns
]