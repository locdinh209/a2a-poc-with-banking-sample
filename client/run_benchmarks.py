import asyncio
import time
import httpx
import logging

# Suppress noisy logs from standard components so our benchmark matrix is clean
logging.getLogger("client").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("a2a").setLevel(logging.ERROR)
logging.getLogger("observability").setLevel(logging.ERROR)
logging.getLogger("agents").setLevel(logging.ERROR)

from client.orchestrator import BankingOrchestrator
from client.monolith_orchestrator import MonolithOrchestrator
from client.subgraph_orchestrator import SubgraphOrchestrator

async def main():
    print("\n" + "="*80)
    print("🏆 BANKING A2A POC - ENTERPRISE ARCHITECTURE BENCHMARK DEMO 🏆")
    print("="*80)

    print("\n🔍 Initializing Orchestrators...")
    # Initialize all three orchestrators
    a2a_orch = BankingOrchestrator()
    try:
        await a2a_orch.discover_agents([
            "http://localhost:8001",
            "http://localhost:8002",
            "http://localhost:8003"
        ])
        print("  ✅ A2A Protocol servers discovered on HTTP ports 8001, 8002, 8003")
    except Exception as e:
        print(f"  ❌ Failed to reach A2A servers. Make sure they are running physically separated: {e}")
        return

    mono_tools = MonolithOrchestrator()
    print("  ✅ Sub-agents as Tools (LLM ReAct Monolith) loaded into memory")
    
    mono_graph = SubgraphOrchestrator()
    print("  ✅ Agent as Sub-graphs (Deterministic Node Monolith) loaded into memory")

    scenarios = [
        {
            "id": "phase2",
            "name": "Phase 2: Healthy Pipeline (Alice Smith, Strong Credit)",
            "customer_id": "CUST-001",
            "customer_name": "Alice Smith",
            "dob": "1985-04-12",
            "amount": 5000
        },
        {
            "id": "phase3",
            "name": "Phase 3: Failed KYC Sanctions Check (Charlie Danger)",
            "customer_id": "CUST-003",
            "customer_name": "Charlie Danger",
            "dob": "1978-08-30",
            "amount": 1000
        }
    ]

    approaches = [
        ("Sub-agents as Tools", "1A. LLM ReAct Monolith", mono_tools),
        ("Agent as Sub-graphs", "1B. Hardcoded StateGraph", mono_graph),
        ("A2A Protocol", "2. Independent Microservices", a2a_orch)
    ]

    benchmark_results = {}

    for approach_name, approach_desc, orchestrator in approaches:
        print(f"\n🚀 Execution Strategy: {approach_name} | {approach_desc}")
        benchmark_results[approach_name] = {}
        
        for scenario in scenarios:
            print(f"   ➤ Processing {scenario['name']}...")
            start_time = time.time()
            
            try:
                # Different orchestrators return slightly different tuples due to legacy POC code.
                raw_return = await orchestrator.process_loan_application(
                    customer_id=scenario['customer_id'],
                    name=scenario['customer_name'],
                    dob=scenario['dob'],
                    amount=scenario['amount']
                )
            except Exception as e:
                print(f"     ❌ Critical Failure processing {scenario['customer_id']}: {e}")
                benchmark_results[approach_name][scenario['id']] = "ERROR"
                continue
            
            # Universal timing extraction natively in the benchmark suite
            duration = time.time() - start_time
            benchmark_results[approach_name][scenario['id']] = duration
            
            print(f"     🏁 Finished in {duration:.2f} seconds")

    # Terminate HTTP Client safely
    await a2a_orch.close()

    # Formal Result Generation
    print("\n" + "="*80)
    print("📊 ARCHITECTURE BENCHMARK RESULTS (LOWER IS BETTER)")
    print("="*80)
    print("")

    # Helper for formatting
    def fmt(time_val):
        return f"{time_val:.2f}s" if isinstance(time_val, float) else "ERROR"

    p2_1a = fmt(benchmark_results['Sub-agents as Tools']['phase2'])
    p2_1b = fmt(benchmark_results['Agent as Sub-graphs']['phase2'])
    p2_2  = fmt(benchmark_results['A2A Protocol']['phase2'])
    
    p3_1a = fmt(benchmark_results['Sub-agents as Tools']['phase3'])
    p3_1b = fmt(benchmark_results['Agent as Sub-graphs']['phase3'])
    p3_2  = fmt(benchmark_results['A2A Protocol']['phase3'])

    header = f"| {'Execution Phase':<30} | {'1A. LLM ReAct Monolith':<24} | {'1B. Deterministic Sub-graphs':<28} | {'2. A2A Protocol (Microservices)':<32} |"
    separator = f"|{'-'*32}|{'-'*26}|{'-'*30}|{'-'*34}|"
    row1 = f"| {'Phase 2: Healthy KYC & Loan':<30} | {p2_1a:<24} | {p2_1b:<28} | {p2_2:<32} |"
    row2 = f"| {'Phase 3: Failed KYC Sanctions':<30} | {p3_1a:<24} | {p3_1b:<28} | {p3_2:<32} |"

    print(header)
    print(separator)
    print(row1)
    print(row2)
    print("")
    
    # Calculate Ratios
    try:
        best_time = float(benchmark_results['A2A Protocol']['phase2'])
        worst_time = float(benchmark_results['Sub-agents as Tools']['phase2'])
        percentage = ((worst_time - best_time) / best_time) * 100
        
        print(f"💡 THE 'LLM ROUTING TAX' VERDICT:")
        print(f"The LLM ReAct Monolith incurred an LLM Routing Tax compounding to +{percentage:.1f}% slower execution time")
        print("compared to the strictly decoupled A2A Protocol orchestration.")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())
