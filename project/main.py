import os
from llm_client import GroqLLM
from orchestrator import MultiAgentOrchestrator

def main():
    print("Initializing Agentic AI System - Multi-Agent Orchestrator with Judge Layer...")
    try:
        llm = GroqLLM()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        print("Please set your GROQ_API_KEY inside a .env file or as a system environment variable.")
        return

    orchestrator = MultiAgentOrchestrator(llm)
    
    # Ask the user to input the task
    task = input("\nPlease enter the complex task or problem you want the agents to solve:\n> ")
    
    final_result = orchestrator.orchestrate(task)
    
    if final_result:
        final_context = final_result["final_context"] if isinstance(final_result, dict) else final_result
        print("\n=== SYSTEM EXECUTION LOG AND FINAL CONTEXT ===\n")
        print(final_context)
        
        import time
        # Generate a unique filename using a timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.txt"
        
        # Save output to file for demonstration
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_context)
        print(f"\nSaved full pipeline output to {filename}")
    else:
        print("\nPipeline aborted due to persistent agent failures caught by the Judge.")

if __name__ == "__main__":
    main()
