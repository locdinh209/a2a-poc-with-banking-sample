import uvicorn
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
)
from a2a.types import AgentCard, AgentSkill
import httpx

from .agent_executor import TransactionAgentExecutor
from observability.tracing import setup_tracing

def create_app():
    # Setup open telemetry tracing
    tracer = setup_tracing("transaction-agent")
    
    skill = AgentSkill(
        id="transaction-analysis",
        name="Transaction Analysis and Summary",
        description="Analyze a customer's requested transaction history and summarize spending patterns.",
        examples=["Analyze transactions for customer CUST-001"],
        tags=["banking", "transactions", "spending", "analysis"]
    )

    agent_card = AgentCard(
        name="Banking Transaction Analyzer Agent",
        description="Analyzes spending patterns based on recent transaction data. Provides summaries and categorizations of cash flows.",
        url="http://localhost:8002",
        version="1.0.0",
        skills=[skill],
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities={"streaming": True}
    )

    executor = TransactionAgentExecutor()
    
    httpx_client = httpx.AsyncClient()
    push_config_store = InMemoryPushNotificationConfigStore()
    push_sender = BasePushNotificationSender(httpx_client=httpx_client, config_store=push_config_store)
    
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        push_config_store=push_config_store,
        push_sender=push_sender
    )
    
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler).build()
    
    # Instrument the built FastAPI/Starlette app
    FastAPIInstrumentor.instrument_app(app)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
