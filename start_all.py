import subprocess
import sys
import time

def main():
    print("Starting A2A Banking Agents...")
    
    # Start all 3 agents as subprocesses
    loan_agent = subprocess.Popen([sys.executable, "-m", "agents.loan_agent.__main__"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    txn_agent = subprocess.Popen([sys.executable, "-m", "agents.transaction_agent.__main__"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    kyc_agent = subprocess.Popen([sys.executable, "-m", "agents.kyc_agent.__main__"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("All agents started. Waiting 3 seconds for Uvicorn to initialize...")
    time.sleep(3)
    
    print("\nRunning Master Architecture Benchmark Suite...")
    try:
        subprocess.run([sys.executable, "-m", "client.run_benchmarks"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Test failed: {e}")
    finally:
        print("\nShutting down agents...")
        loan_agent.terminate()
        txn_agent.terminate()
        kyc_agent.terminate()
        
        loan_agent.wait()
        txn_agent.wait()
        kyc_agent.wait()
        print("Done.")

if __name__ == "__main__":
    main()
