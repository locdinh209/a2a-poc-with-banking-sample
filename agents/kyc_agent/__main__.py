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

from .agent_executor import KYCAgentExecutor
from observability.tracing import setup_tracing

def create_app():
    # Setup open telemetry tracing
    tracer = setup_tracing("kyc-agent")
    
    skill = AgentSkill(
        id="kyc-verification",
        name="Customer KYC Verification",
        description="Verify a customer's identity using their name and DOB and check if they are on any sanctions lists.",
        examples=["Verify KYC for customer CUST-001, name Alice Smith, dob 1985-04-12"],
        tags=["banking", "compliance", "kyc", "identity", "sanctions"]
    )

    agent_card = AgentCard(
        name="Banking KYC Verification Agent",
        description="Ensures customers pass identity verification and are not present on any sanctions watchlists.",
        url="http://localhost:8003",
        version="1.0.0",
        skills=[skill],
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities={"streaming": True}
    )

    executor = KYCAgentExecutor()
    
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
    uvicorn.run(app, host="0.0.0.0", port=8003)
