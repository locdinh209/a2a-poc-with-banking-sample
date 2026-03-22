import asyncio
import logging
import time
from observability.logger import A2AEventLogger
from client.subgraph_orchestrator import SubgraphOrchestrator

logging.basicConfig(level=logging.INFO)

async def main():
    logger = A2AEventLogger()
    orchestrator = SubgraphOrchestrator(logger_util=logger)
    
    print("\n" + "="*50)
    print("🏦 PHASE 1: AGENT INITIALIZATION")
    print("="*50)
    print("Wiring agents deterministically via StateGraph edges...")
    time.sleep(0.5)
    
    print("\n" + "="*50)
    print("🏦 PHASE 2: HEALTHY LOAN APPLICATION PIPELINE")
    print("="*50)
    
    start_alice = time.time()
    result, steps, dur1 = await orchestrator.process_loan_application(
        customer_id="CUST-001",
        name="Alice Smith",
        dob="1985-04-12",
        amount=5000
    )
    dur_alice = time.time() - start_alice
    
    print("\n🏁 FINAL DECISION:")
    print("-" * 30)
    print(result)
    print("-" * 30)
    print(f"Total Time (Alice - Healthy): {dur_alice:.2f}s")
    
    print("\n" + "="*50)
    print("🏦 PHASE 3: FAILED KYC PIPELINE")
    print("="*50)
    
    start_charlie = time.time()
    result2, steps2, dur2 = await orchestrator.process_loan_application(
        customer_id="CUST-003",
        name="Charlie Danger",
        dob="1978-08-30",
        amount=1000
    )
    dur_charlie = time.time() - start_charlie
    
    print("\n🏁 FINAL DECISION:")
    print("-" * 30)
    print(result2)
    print("-" * 30)
    print(f"Total Time (Charlie - Failed KYC): {dur_charlie:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
