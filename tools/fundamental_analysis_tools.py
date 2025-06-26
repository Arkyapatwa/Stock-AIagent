import logging
import yfinance as yf
from typing import Dict, List, Tuple, Union
from pydantic import BaseModel
from langchain.tools import tool

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the client


@tool("get_financial_statements")
def get_financial_statements(ticker: str) -> dict:
    """
    Returns a dictionary of financial statements for a given ticker.
    
    Args:
        ticker: The stock ticker symbol.

    Returns:
        A dictionary of financial statements.
    """
    logger.info(f"Fetching financial statements for {ticker}")
    
    stock = yf.Ticker(ticker)

    income_statement = stock.income_stmt
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    
    revenue_details_for_last_3_years = "Revenue Details for the Last 3 Years: "
    expenses_details_for_last_3_years = "Expenses Details for the Last 3 Years: "
    net_profit_details_for_last_3_years = "Net Profit Details for the Last 3 Years: "
    
    net_debt_details_for_last_3_years = "Net Debt Details for the Last 3 Years: "
    total_Debt_details_for_last_3_years = "Total Debt Details for the Last 3 Years: "
    debt_to_equity_ratio_details_for_last_3_years = "Debt-to-Equity Ratio Details for the Last 3 Years: "
    
    free_cash_flow_details_for_last_3_years = "Free Cash Flow Details for the Last 3 Years: "
    operating_cash_flow_details_for_last_3_years = "Operating Cash Flow Details for the Last 3 Years: "
    
    for year in income_statement.columns[:3]:
        # Income Statement
        revenue_details_for_last_3_years += f"{year}: {income_statement.loc['Total Revenue', year]}, "
        expenses_details_for_last_3_years += f"{year}: {income_statement.loc['Total Expenses', year]}, "
        net_profit_details_for_last_3_years += f"{year}: {income_statement.loc['Gross Profit', year]}, "
        
        # Balance Sheet
        net_debt_details_for_last_3_years += f"{year}: {balance_sheet.loc['Net Debt', year]}, "
        total_Debt_details_for_last_3_years += f"{year}: {balance_sheet.loc['Total Debt', year]}, "
        
        debt_to_equity_ratio = balance_sheet.loc['Total Debt', year] / balance_sheet.loc['Tangible Book Value', year]
        debt_to_equity_ratio_details_for_last_3_years += f"{year}: {debt_to_equity_ratio}, "
        
        # cash flow
        free_cash_flow_details_for_last_3_years += f"{year}: {cash_flow.loc['Free Cash Flow', year]}, "
        operating_cash_flow_details_for_last_3_years += f"{year}: {cash_flow.loc['Operating Cash Flow', year]}, "
    
    response = {
        "income_statement": {
            "revenue_details_for_last_3_years": revenue_details_for_last_3_years[:-2],
            "expenses_details_for_last_3_years": expenses_details_for_last_3_years[:-2],
            "net_profit_details_for_last_3_years": net_profit_details_for_last_3_years[:-2],
            },
        "balance_sheet": {
            "net_debt_details_for_last_3_years": net_debt_details_for_last_3_years[:-2],
            "total_Debt_details_for_last_3_years": total_Debt_details_for_last_3_years[:-2],
            "debt_to_equity_ratio_details_for_last_3_years": debt_to_equity_ratio_details_for_last_3_years[:-2],
            },
        "cash_flow": {
            "free_cash_flow_details_for_last_3_years": free_cash_flow_details_for_last_3_years[:-2],
            "operating_cash_flow_details_for_last_3_years": operating_cash_flow_details_for_last_3_years[:-2],
            },
    }
    
    system_instruction = f"Analyse the Financial Statements for {ticker} and give a summarized analysis of the company's financial performance in the last 3 years. \n\n"
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )
    config = types.GenerateContentConfig(
        max_output_tokens=200,
        system_instruction= system_instruction,
        temperature=0.9
    )
    summarized_response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=f"Financial Data: {response} \n Use Maximum of 200 words.",
        config=config,
    )
    
    logger.info(f"Successfully fetched financial statements for {ticker}: {summarized_response.text}")
    return summarized_response.text
    
    
@tool("get_valuation_ratios")
def get_valuation_ratios(ticker: str) -> dict:
    """
    Returns a dictionary of valuation ratios for a given ticker.
    
    Args:
        ticker: The stock ticker symbol.
    Returns:
        A dictionary of valuation ratios.
    """
    logger.info(f"Fetching valuation ratios for {ticker}")
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    
    
    valuation_ratios = {
        "P/E": stock_info.get("trailingPE"),
        "Forward P/E": stock_info.get("forwardPE"),
        "P/B": stock_info.get("priceToBook"),
        "ROE": stock_info.get("returnOnEquity"),
        "EPS (TTM)": stock_info.get("trailingEps"),
        "EPS (Forward)": stock_info.get("forwardEps"),
        "D/E": stock_info.get("debtToEquity"),
        "Current Ratio": stock_info.get("currentRatio"),
    }
    system_instruction = f"Analyse the Valuation Ratios for {ticker} and give a summarized analysis of the company's valuation performance in the last 3 years. \n\n"
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )
    config = types.GenerateContentConfig(
        max_output_tokens=200,
        system_instruction=system_instruction,
        temperature=0.9
    )
    
    summarized_response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=f"Valuation Ratios Data: {valuation_ratios} \n Use Maximum of 200 words.",
        config=config,
    )
    
    logger.info(f"Successfully fetched valuation ratios for {ticker}: {summarized_response.text}")
    return summarized_response.text


@tool("get_company_overview")
def get_management_and_business_details(ticker: str) -> str:
    """
    Returns a string of management and business details for a given ticker.

    Args:
        ticker: The stock ticker symbol.
    Returns:
        A string of management and business details.
    """
    logger.info(f"Fetching company overview for {ticker}")


    # Define the grounding tool
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    system_instruction = """
    You are a stock market analyst. Analyse the given stock on these topics only:

    1. Management Quality: Are the leaders experienced, ethical, and capable? - 100 words maximum
    2. Competitive Advantage (Moat): Does the company have a unique selling proposition, strong brand, patents, or a dominant market share that protects it from competitors? - 100 words maximum
    3. Products/Services and Demand: Are its products or services in high demand? Is there potential for future growth in its offerings? - 100 words maximum
    4. Growth Prospects: Does the company have plans for expansion, new products, or entering new markets? - 100 words maximum

    Answer under 500 words. Keep your answers short and crisp.
    """
    # Configure generation settings
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        max_output_tokens=500,
        system_instruction= system_instruction,
        temperature=0.9
    )
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Stock: {ticker}",
        config=config,
    )
    logger.info(f"Successfully fetched company overview for {ticker}: {response.text}")
    return response.text


@tool("get_industry_analysis")
def get_industry_analysis(ticker: str) -> str:
    """
    Returns a string of industry analysis for a given ticker.

    Args:
        ticker: The stock ticker symbol.
    Returns:
        A string of industry analysis.
    """
    logger.info(f"Fetching industry analysis for {ticker}")
    
    # Define the grounding tool
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    system_instruction = """
    You are a stock's Industry analyst. Analyse the given stock Industry on these topics only:

    1. Industry Growth: Is the industry itself growing or declining? - 50 words maximum
    2. Competition: How intense is the competition? - 50 words maximum
    3. Regulatory Environment: Are there any government policies or regulations that could significantly impact the company? - 50 words maximum
    5. Economic Cycles: How does the industry perform during different economic cycles (boom, recession)? - 100 words maximum

    Answer under 500 words. Keep your answers short and crisp.
    """
    # Configure generation settings
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        max_output_tokens=500,
        system_instruction= system_instruction,
        temperature=0.9
    )
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Stock: {ticker}",
        config=config,
    )
    logger.info(f"Successfully fetched industry analysis for {ticker}: {response.text}")
    return response.text


@tool("get_macroeconomic_conditions")
def get_macroeconomic_conditions(ticker: str) -> str:
    """
    Returns a string of global macroeconomic conditions for a given ticker.
    
    Args:
        ticker: The stock ticker symbol.
    Returns:
        A string of macroeconomic conditions.
    """
    logger.info(f"Fetching macroeconomic conditions for {ticker}")
    # Define the grounding tool
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    system_instruction = """
    You are a Macroeconomic analyst. Analyse the given stock with respective country and global Macroeconomic on these topics only:

    1. Interest Rates: Rising interest rates can make borrowing more expensive for companies and make bonds more attractive than stocks. - 50 words maximum
    2. Inflation: High inflation can erode purchasing power and company profits. - 50 words maximum
    3. GDP Growth: A strong economy generally supports higher corporate earnings. - 50 words maximum
    4. Geopolitical Factors: Global events, trade wars, or political instability can affect market sentiment and company performance. - 50 words maximum
    5. Monetary Policies: Decisions by central banks (like the RBI in India) on interest rates and money supply can have a significant impact. - 50 words maximum

    Answer under 1000 words. Keep your answers short and crisp.
    """
    # Configure generation settings
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        max_output_tokens=1000,
        system_instruction= system_instruction,
        temperature=0.9
    )
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Stock: {ticker}",
        config=config,
    )
    
    logger.info(f"Successfully fetched macroeconomic conditions for {ticker}: {response.text}")
    return response.text


fundamental_tools = [
    get_financial_statements,
    get_valuation_ratios,
    get_management_and_business_details,
    get_industry_analysis,
    get_macroeconomic_conditions,
]