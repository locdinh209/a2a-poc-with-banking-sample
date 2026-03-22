import asyncio
import logging
import time
from observability.logger import A2AEventLogger
from client.monolith_orchestrator import MonolithOrchestrator

logging.basicConfig(level=logging.INFO)

async def main():
    logger = A2AEventLogger()
    # Provide a silent console logger for tools, but let's just use it
    orchestrator = MonolithOrchestrator(logger_util=logger)
    
    print("\n" + "="*50)
    print("🏦 PHASE 1: AGENT INITIALIZATION")
    print("="*50)
    # Monolith does not discover over HTTP, simply initializes in memory
    print("Instantiating agents directly in memory...")
    time.sleep(0.5)
    print("Initialized KYCAgent (Memory: Local)")
    print("Initialized TransactionAgent (Memory: Local)")
    print("Initialized LoanAgent (Memory: Local)")
    
    print("\n" + "="*50)
    print("🏦 PHASE 2: HEALTHY LOAN APPLICATION PIPELINE")
    print("="*50)
    
    # Alice meets all criteria
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
    print(f"Total Time (Alice): {dur_alice:.2f}s")
    
    print("\n" + "="*50)
    print("🏦 PHASE 3: FAILED KYC PIPELINE")
    print("="*50)
    
    # Charlie is on sanctions list
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
    print(f"Total Time (Charlie): {dur_charlie:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
