import json
import re

class Agent:
    def __init__(self, name, role, system_prompt, llm_client):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm = llm_client
    
    def run(self, task, context=""):
        prompt = f"Task: {task}\n\nCurrent Context from previous agents:\n{context}\n\nPlease perform your role, advance the state of the task, and provide your output."
        response = self.llm.generate(self.system_prompt, prompt)
        return response

class JudgeAgent(Agent):
    def __init__(self, llm_client):
        system_prompt = """You are the structural Judge Agent of a Multi-Agent system. 
Your job is to read the output of another Agent and score it based on:
1. Role Adherence: Did the agent act within its role?
2. Relevancy: Did the agent meaningfully process the task?
3. Fault Tolerance: Does the output contain errors, hallucinations, or unhandled exceptions?

You must output ONLY valid JSON in this exact format, with no other conversational text:
{
    "score": <int between 1 and 10>,
    "feedback": "<string explanation of the score and what needs to change if anything>",
    "passed": <boolean, true if score >= 7 else false>
}"""
        super().__init__("Judge", "Evaluator and Fault Catcher", system_prompt, llm_client)
        
    def evaluate(self, agent_name, agent_role, task, output):
        prompt = f"""
Evaluate the following output from the '{agent_name}' acting as the role of '{agent_role}'.
The overall Task is: {task}

Agent's Output:
---
{output}
---

Provide your JSON evaluation according to the system prompt rules.
"""
        response = self.llm.generate(self.system_prompt, prompt)
        # Attempt to parse json
        try:
            # simple regex to extract json block in case it wrapped it in ```json
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                return json.loads(response)
        except Exception as e:
            # Fallback if judge hallucinates format
            return {"score": 5, "feedback": f"Judge failed to return valid JSON. Raw output: {response}", "passed": False}
