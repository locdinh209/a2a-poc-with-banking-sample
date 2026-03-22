import logging
import os
import uuid
from typing import Dict, Any, List, TypedDict, Literal
import time
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from agents.kyc_agent.agent import KYCAgent
from agents.transaction_agent.agent import TransactionAgent
from agents.loan_agent.agent import LoanAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache agents locally
_kyc_agent = KYCAgent()
_txn_agent = TransactionAgent()
_loan_agent = LoanAgent()

class MasterState(TypedDict):
    customer_id: str
    name: str
    dob: str
    amount: float
    kyc_status: str
    txn_summary: str
    final_decision: str

def kyc_node(state: MasterState):
    logger.info(f"[Sub-graph] Executing KYC Node for {state['customer_id']}")
    query = f"Verify KYC for customer {state['customer_id']}, name {state['name']}, dob {state['dob']}."
    config = {'configurable': {'thread_id': uuid.uuid4().hex}}
    inputs = {'messages': [('user', query)]}
    result = _kyc_agent.graph.invoke(inputs, config)
    
    structured = result.get('structured_response')
    status_msg = f"Status: {structured.status}. Message: {structured.message}" if structured else result['messages'][-1].content
    
    return {"kyc_status": status_msg}

def kyc_router(state: MasterState) -> Literal["txn_node", "__end__"]:
    # If the LLM response contains FAILED, route to end
    if "FAILED" in state["kyc_status"].upper():
        logger.warning(f"[Sub-graph] KYC Failed. Terminating workflow.")
        return "__end__"
    return "txn_node"

def txn_node(state: MasterState):
    logger.info(f"[Sub-graph] Executing Transaction Node for {state['customer_id']}")
    query = f"Analyze transactions and spending patterns for customer {state['customer_id']}"
    config = {'configurable': {'thread_id': uuid.uuid4().hex}}
    inputs = {'messages': [('user', query)]}
    result = _txn_agent.graph.invoke(inputs, config)
    
    structured = result.get('structured_response')
    status_msg = f"Status: {structured.status}. Message: {structured.message}" if structured else result['messages'][-1].content
    return {"txn_summary": status_msg}

def loan_node(state: MasterState):
    logger.info(f"[Sub-graph] Executing Loan Node for {state['customer_id']}")
    query = (
        f"Assess loan application for customer={state['customer_id']}. Requested loan amount is ${state['amount']}. "
        f"Note their KYC status is: {state['kyc_status']}. Their spending pattern is: {state['txn_summary']}"
    )
    config = {'configurable': {'thread_id': uuid.uuid4().hex}}
    inputs = {'messages': [('user', query)]}
    result = _loan_agent.graph.invoke(inputs, config)
    
    structured = result.get('structured_response')
    status_msg = f"Status: {structured.status}. Message: {structured.message}" if structured else result['messages'][-1].content
    return {"final_decision": status_msg}

class SubgraphOrchestrator:
    """
    A unified deterministic LangGraph where sub-agents run as simple graph nodes.
    This bypasses LLM task-routing latency entirely.
    """
    def __init__(self, logger_util=None):
        self.logger_util = logger_util
        
        workflow = StateGraph(MasterState)
        workflow.add_node("kyc_node", kyc_node)
        workflow.add_node("txn_node", txn_node)
        workflow.add_node("loan_node", loan_node)
        
        workflow.add_edge(START, "kyc_node")
        workflow.add_conditional_edges("kyc_node", kyc_router)
        workflow.add_edge("txn_node", "loan_node")
        workflow.add_edge("loan_node", END)
        
        self.graph = workflow.compile()

    async def process_loan_application(self, customer_id: str, name: str, dob: str, amount: float):
        logger.info(f"Starting subgraph loan processing for {customer_id}")
        start_time = time.time()
        
        initial_state = {
            "customer_id": customer_id,
            "name": name,
            "dob": dob,
            "amount": amount,
            "kyc_status": "",
            "txn_summary": "",
            "final_decision": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        duration = time.time() - start_time
        steps = [] # Omitted detailed step logs for brevity as state routing handles it.
        
        # If final_decision is empty, it means we terminated early (e.g. KYC failed)
        final_msg = result.get("final_decision")
        if not final_msg:
            final_msg = f"Workflow Terminated Early. Reason: {result.get('kyc_status')}"
            
        return final_msg, steps, duration
