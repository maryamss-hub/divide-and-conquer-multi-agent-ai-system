# Divide and Conquer Multi-Agent AI System

This repository contains the code for the Divide and Conquer Multi-Agent AI System — an Agentic AI final semester project fulfilling the requirements of a Complex Computing Problem. 
It resolves the problems identified in **CourseProject_part1_Group#7.pdf** with advanced mechanisms:

## Key Features & Gap Solving:
- **No fault tolerance (Solved):** A `Judge Agent` evaluates outputs before they advance down the pipeline. If an agent hallucinates or produces poor responses, it's flagged and resolved.
- **Rigid roles (Solved):** The `Coordinator` runs an observation loop and re-assigns or retries execution when failures are detected, creating dynamic robustness.
- **Role drift (Solved):** The `Judge` strictly enforces role adherence based on the initial system prompt of the agent.
- **No evaluation metric (Solved):** The `Judge` gives a quantifiable integer score (1-10) for every generation turn, allowing for empirical testing and data collection for the paper.

## NCEAC Complex Computing Requirements:
- **Multi-step reasoning or planning:** The system runs through a Planner -> Researcher -> Writer sequence.
- **Tool usage or API integration:** The Researcher agent utilizes a real Wikipedia API extraction tool autonomously when knowledge gaps arise.
- **Autonomy beyond simple prompting:** Orchestrator controls the failure loop, re-tries, and intercepts custom tool tags automatically.

## Setup
1. Create a `.env` file in the `agentic_system` directory and add your key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the system:
   ```bash
   python main.py
   ```
