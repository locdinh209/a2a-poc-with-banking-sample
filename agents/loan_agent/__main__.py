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

from .agent_executor import LoanAgentExecutor
from observability.tracing import setup_tracing

def create_app():
    # Setup open telemetry tracing
    tracer = setup_tracing("loan-agent")
    
    skill = AgentSkill(
        id="loan-assessment",
        name="Loan Eligibility Assessment",
        description="Evaluate customer loan eligibility based on their credit, DTI and requested amount.",
        examples=["Assess Customer CUST-001 for a 3000 loan"],
        tags=["banking", "loan", "credit", "assessment"]
    )

    agent_card = AgentCard(
        name="Banking Loan Assessment Agent",
        description="Evaluates loan applications based on credit score, income, and debt-to-income ratio. Ask it to evaluate a loan for a specific customer ID.",
        url="http://localhost:8001",
        version="1.0.0",
        skills=[skill],
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities={"streaming": True}
    )

    executor = LoanAgentExecutor()
    
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
