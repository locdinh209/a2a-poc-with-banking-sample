import os
from typing import Any, Literal
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from collections.abc import AsyncIterable
from dotenv import load_dotenv

from .tools import verify_identity, check_sanctions_list

load_dotenv()

memory = MemorySaver()

class ResponseFormat(BaseModel):
    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str
    
class KYCAgent:
    """Agent for KYC (Know Your Customer) verification."""

    SYSTEM_INSTRUCTION = (
        'You are a strict compliance agent responsible for Know Your Customer (KYC) verification. '
        'To verify a customer, you need their customer_id, name, and date of birth (DOB). '
        'If any of these are missing from the request, set status to input_required and ask for the missing details. '
        'Use verify_identity tool first. If identity is verified, then use check_sanctions_list tool to ensure they are clear. '
        'If identity verification fails OR they are on a sanctions list, the overall KYC status is FAILED. '
        'If both pass, the KYC status is VERIFIED. '
        'Once complete, set status to completed and provide the final status and reasoning.'
    )

    FORMAT_INSTRUCTION = (
        'Set response status to input_required if you need name or DOB to verify the ID. '
        'Set response status to error if there is an error. '
        'Set response status to completed if the verification and sanction check are complete.'
    )

    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-5-mini'),
            openai_api_key=os.getenv('API_KEY', 'EMPTY'),
            openai_api_base=os.getenv('TOOL_LLM_URL', 'http://localhost:8317/v1'),
            temperature=0,
        )
        self.tools = [verify_identity, check_sanctions_list]

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
                    'content': f"Running compliance check: {message.tool_calls[0]['name']}...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f"Compliance check {message.name} yielded results.",
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
            'content': 'Unable to process KYC request. Please try again.'
        }
