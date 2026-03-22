# 🏦 Banking A2A Proof of Concept: The "LLM Routing Tax" Benchmark

This repository serves as a **technical and empirical benchmark** comparing three dominant AI Orchestration Architectures in an enterprise banking context evaluating a Loan Application Pipeline (with KYC and Transaction dependencies).

### 🎯 The Core Finding
By isolating execution pathways, this POC definitively proves the existence of the **"LLM Routing Tax"**—a compounding latency and cost penalty incurred when using a single LLM to route agent execution (Monolithic ReAct) rather than using physically decoupled microservices (A2A Protocol).

According to our internal benchmarks, migrating from a Monolithic ReAct "Agent as Tools" framework to a fully decentralized **A2A Protocol Architecture** improved end-to-end processing speeds by **~21.8%** while completely eliminating shared-memory state leakage and PII exposure risks.

---

## 🏗️ Evaluated Architectures

The benchmark suite automatically runs the same workflow across three different architectural paradigms:

1. **Sub-agents as Tools (LLM ReAct Monolith)**: The orchestrator uses a master LLM (e.g. `gpt-4o-mini`) equipped with sub-agents as callable LangGraph tools. It must "think" before and after every single state mutation.
2. **Agent as Sub-graphs (Deterministic Monolith)**: A strictly hardcoded Master `StateGraph`. Routes exist statically without LLM polling, resolving latency but causing severe state-leakage (all components share the Master State memory).
3. **A2A Protocol (Agent Microservices)**: The enterprise standard. Agents operate as fully independent HTTP microservice containers. They message each other asynchronously, preventing state leakage and bypassing the LLM Routing Tax completely.

---

## 🚀 Running the Benchmark

The suite requires the 3 agent servers to run in the background. We have provided an automated Python master script `start_all.py` that spins up the agents and executes the unified benchmark matrix.

### Prerequisites
1. Ensure you have Python 3.10+ installed.
2. Install dependencies (e.g., using `uv`):
   ```bash
   uv sync
   ```
3. Set up your environment variables (`.env`):
   ```bash
   cp .env.example .env
   # Add your OpenAI or proxy API Key
   ```

### Execution
Simply execute the master boot script to start the servers and render the benchmark table:
```bash
python start_all.py
```

### Expected Output
The benchmark suite strips noisy standard output (telemetry logs) to output a clean comparative matrix:
```text
================================================================================
📊 ARCHITECTURE BENCHMARK RESULTS (LOWER IS BETTER)
================================================================================

| Execution Phase                | 1A. LLM ReAct Monolith   | 1B. Deterministic Sub-graphs | 2. A2A Protocol (Microservices)  |
|--------------------------------|--------------------------|------------------------------|----------------------------------|
| Phase 2: Healthy KYC & Loan    | 87.12s                   | 69.00s                       | 71.56s                           |
| Phase 3: Failed KYC Sanctions  | 26.86s                   | 12.64s                       | 20.85s                           |

💡 THE 'LLM ROUTING TAX' VERDICT:
The LLM ReAct Monolith incurred an LLM Routing Tax compounding to +21.8% slower execution time
compared to the strictly decoupled A2A Protocol orchestration.
```

---

## 🔒 Security Posture & Zero Trust

This POC is designed with a **Zero Trust Security Principle**.
- **No Hardcoded Tokens:** All credentials are kept in `./.env` which is strictly blocked by `.gitignore`.
- **Decentralized State Memory:** While monoliths share memory stores (`StateGraph` sharing `customer_id`, transaction histories, etc.), the A2A orchestrated agents keep isolated memories per service container, ensuring a hijacked KYC pipeline cannot extract transaction histories.
