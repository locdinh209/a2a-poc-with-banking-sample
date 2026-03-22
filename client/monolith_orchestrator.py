import logging
import os
import uuid
from typing import Dict, Any, List
import time
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from agents.kyc_agent.agent import KYCAgent
from agents.transaction_agent.agent import TransactionAgent
from agents.loan_agent.agent import LoanAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache agents so we don't reinitialize ChatOpenAI often
_kyc_agent = KYCAgent()
_txn_agent = TransactionAgent()
_loan_agent = LoanAgent()

@tool("kyc_verification_tool")
def kyc_verification_tool(customer_id: str, name: str, dob: str) -> str:
    """
    Verify Know Your Customer (KYC) details.
    Always call this first before assessing loop applications.
    Returns VERIFIED or FAILED.
    """
    logger.info(f"[Monolith] Calling KYC Agent for {customer_id}")
    query = f"Verify KYC for customer {customer_id}, name {name}, dob {dob}."
    config = {'configurable': {'thread_id': uuid.uuid4().hex}}
    inputs = {'messages': [('user', query)]}
    result = _kyc_agent.graph.invoke(inputs, config)
    
    # Extract structural form
    structured = result.get('structured_response')
    if structured:
        return f"Status: {structured.status}. Message: {structured.message}"
    return result['messages'][-1].content

@tool("transaction_analyzer_tool")
def transaction_analyzer_tool(customer_id: str) -> str:
    """
    Analyze transactions and spending patterns for a customer.
    Returns a summary of their financial behavior.
    """
    logger.info(f"[Monolith] Calling Transaction Agent for {customer_id}")
    query = f"Analyze transactions and spending patterns for customer {customer_id}"
    config = {'configurable': {'thread_id': uuid.uuid4().hex}}
    inputs = {'messages': [('user', query)]}
    result = _txn_agent.graph.invoke(inputs, config)
    
    structured = result.get('structured_response')
    if structured:
        return f"Status: {structured.status}. Message: {structured.message}"
    return result['messages'][-1].content

@tool("loan_assessment_tool")
def loan_assessment_tool(customer_id: str, requested_amount: float, kyc_status: str, spending_pattern: str) -> str:
    """
    Assess the final loan application. Must provide customer_id, requested_amount,
    and the results from the KYC tool and Transaction tool.
    Returns the final loan decision.
    """
    logger.info(f"[Monolith] Calling Loan Agent for {customer_id}")
    query = (
        f"Assess loan application for customer={customer_id}. Requested loan amount is ${requested_amount}. "
        f"Note their KYC status is: {kyc_status}. Their spending pattern is: {spending_pattern}"
    )
    config = {'configurable': {'thread_id': uuid.uuid4().hex}}
    inputs = {'messages': [('user', query)]}
    result = _loan_agent.graph.invoke(inputs, config)
    
    structured = result.get('structured_response')
    if structured:
        return f"Status: {structured.status}. Message: {structured.message}"
    return result['messages'][-1].content

class MonolithOrchestrator:
    """
    A single LangGraph orchestrator that treats KYC, Transaction, 
    and Loan logic as imported sub-agent tools.
    """
    
    def __init__(self, logger_util=None):
        self.logger_util = logger_util
        self.model = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-5-mini'),
            openai_api_key=os.getenv('API_KEY', 'EMPTY'),
            openai_api_base=os.getenv('TOOL_LLM_URL', 'http://localhost:8317/v1'),
            temperature=0,
        )
        self.tools = [kyc_verification_tool, transaction_analyzer_tool, loan_assessment_tool]
        self.system_prompt = (
            "You are the Bank Loan Orchestrator Agent. "
            "You must process loan applications by utilizing your sub-agent tools in order:\n"
            "1. Run KYC verification using kyc_verification_tool.\n"
            "   If KYC fails or returns an error, stop and reject the application. Do not run any other tools.\n"
            "2. Run Transaction Analysis using transaction_analyzer_tool.\n"
            "3. Assess the loan using loan_assessment_tool, passing the KYC and transaction results.\n"
            "Return the final determination output from the loan assessment tool."
        )
        self.memory = MemorySaver()
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=self.memory,
            prompt=self.system_prompt
        )

    async def process_loan_application(self, customer_id: str, name: str, dob: str, amount: float):
        logger.info(f"Starting monolith loan processing for {customer_id}")
        start_time = time.time()
        
        query = f"Process loan for customer {customer_id}, name {name}, dob {dob}. Amount: {amount}"
        config = {'configurable': {'thread_id': uuid.uuid4().hex}}
        inputs = {'messages': [('user', query)]}
        
        steps = []
        
        # We invoke the orchestrator graph. The orchestrator will decide which tools to call.
        # But for benchmarking, we might want to manually trace the tools if possible, or just look at the final time.
        # For an apple-to-apple comparison to the A2A orchestrator (which manually orchestrates),
        # we can just use the LangGraph Orchestrator to do it, OR manually execute the tools.
        # Given "Sub-agents as tools", building a big graph or a python function with graph tools is equivalent.
        # Let's let the ReAct agent graph orchestrate it.
        
        result = await self.graph.ainvoke(inputs, config)
        
        duration = time.time() - start_time
        
        # We can extract the tool calls from the message history to simulate step tracking
        messages = result['messages']
        tool_names_called = [m.name for m in messages if isinstance(m, AIMessage) == False and hasattr(m, 'name') and m.name]
        
        for idx, tool_name in enumerate(tool_names_called):
            steps.append({"step": idx+1, "agent": tool_name, "status": "✅", "duration": "See Overal Duration"})
            
        final_message = messages[-1].content
        
        if self.logger_util:
            self.logger_util.log_workflow_summary(steps)
            
        return final_message, steps, duration
