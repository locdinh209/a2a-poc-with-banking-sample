import asyncio
import logging
from observability.logger import A2AEventLogger
from client.orchestrator import BankingOrchestrator

logging.basicConfig(level=logging.INFO)

async def main():
    logger = A2AEventLogger()
    orchestrator = BankingOrchestrator(logger_util=logger)
    
    agent_urls = [
        "http://localhost:8001",  # Loan Agent
        "http://localhost:8002",  # Transaction Agent
        "http://localhost:8003"   # KYC Agent
    ]
    
    print("\n" + "="*50)
    print("🏦 PHASE 1: AGENT DISCOVERY")
    print("="*50)
    await orchestrator.discover_agents(agent_urls)
    
    if len(orchestrator.agents) < 3:
        print("Failed to discover all agents. Please ensure the servers are running.")
        return
        
    print("\n" + "="*50)
    print("🏦 PHASE 2: HEALTHY LOAN APPLICATION PIPELINE")
    print("="*50)
    
    # Alice meets all criteria
    result, steps = await orchestrator.process_loan_application(
        customer_id="CUST-001",
        name="Alice Smith",
        dob="1985-04-12",
        amount=5000
    )
    print("\n🏁 FINAL DECISION:")
    print("-" * 30)
    print(result)
    print("-" * 30)
    
    print("\n" + "="*50)
    print("🏦 PHASE 3: FAILED KYC PIPELINE")
    print("="*50)
    
    # Charlie is on sanctions list
    result2, steps2 = await orchestrator.process_loan_application(
        customer_id="CUST-003",
        name="Charlie Danger",
        dob="1978-08-30",
        amount=1000
    )
    print("\n🏁 FINAL DECISION:")
    print("-" * 30)
    print(result2)
    print("-" * 30)
    
    await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(main())
