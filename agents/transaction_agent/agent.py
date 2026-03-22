import os
from typing import Any, Literal
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from collections.abc import AsyncIterable
from dotenv import load_dotenv

from .tools import get_recent_transactions, summarize_spending_patterns

load_dotenv()

memory = MemorySaver()

class ResponseFormat(BaseModel):
    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str
    
class TransactionAgent:
    """Agent for analyzing customer transactions."""

    SYSTEM_INSTRUCTION = (
        'You are a financial analysis agent that analyzes customer transactions and spending patterns. '
        'You must use get_recent_transactions to view the transaction history '
        'and summarize_spending_patterns to provide a high-level overview. '
        'If the user did not provide a customer_id, set status to input_required and ask for it. '
        'Provide a detailed, helpful summary of their financial behavior based on the tools.'
        'Once complete, set status to completed.'
    )

    FORMAT_INSTRUCTION = (
        'Set response status to input_required if you need the customer ID. '
        'Set response status to error if there is an error. '
        'Set response status to completed if the analysis is complete.'
    )

    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-5-mini'),
            openai_api_key=os.getenv('API_KEY', 'EMPTY'),
            openai_api_base=os.getenv('TOOL_LLM_URL', 'http://localhost:8317/v1'),
            temperature=0,
        )
        self.tools = [get_recent_transactions, summarize_spending_patterns]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.FORMAT_INSTRUCTION, ResponseFormat)
        )

    async def stream(self, query: str, context_id: str) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage) and message.tool_calls:
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f"Querying transaction database via {message.tool_calls[0]['name']}...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f"Analyzed data from {message.name}.",
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == 'input_required':
                return {'is_task_complete': False, 'require_user_input': True, 'content': structured_response.message}
            if structured_response.status == 'error':
                return {'is_task_complete': False, 'require_user_input': True, 'content': structured_response.message}
            if structured_response.status == 'completed':
                return {'is_task_complete': True, 'require_user_input': False, 'content': structured_response.message}

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'Unable to process transaction request. Please try again.'
        }
