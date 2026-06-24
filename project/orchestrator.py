from agents import Agent, JudgeAgent
from tools import get_wikipedia_summary

class MultiAgentOrchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.judge = JudgeAgent(llm_client)
        
        # Initialize our dynamic roles
        self.agents = {
            "Planner": Agent(
                "Planner", 
                "Task Planner", 
                "You are the Planner. Break down the user task into actionable steps for research and writing. Focus on strategy.",
                llm_client
            ),
            "Researcher": Agent(
                "Researcher", 
                "Information Gatherer", 
                "You are the Researcher. Gather actionable information based on the planner's strategy. If you need a fact, output exactly [SEARCH: your_search_keyword] to use the Wikipedia tool. Otherwise, provide detailed context to inform the writer.",
                llm_client
            ),
            "Writer": Agent(
                "Writer", 
                "Content Creator", 
                "You are the Writer. Compile the research and plan into a final cohesive, high-quality response to the user task. Ignore internal tool details in your final output.",
                llm_client
            )
        }
        
    def orchestrate(self, task):
        print(f"\n============================================")
        print(f"[Coordinator] Starting Orchestration for Task:")
        print(f"'{task}'\n============================================")
        
        # Pipeline execution order
        roles_sequence = ["Planner", "Researcher", "Writer"]
        context = ""
        stages = []
        
        for role in roles_sequence:
            agent = self.agents[role]
            passed = False
            attempts = 0
            max_attempts = 3
            final_score = 0
            tool_called = False
            tool_success = False
            
            while not passed and attempts < max_attempts:
                attempts += 1
                print(f"\n[Coordinator] -> Delegating to {role} Agent (Attempt {attempts}/{max_attempts})")
                
                output = agent.run(task, context)
                
                # Intercept for API tool integration
                if role == "Researcher" and "[SEARCH:" in output:
                    import re
                    match = re.search(r'\[SEARCH:\s*(.*?)\]', output)
                    if match:
                        query = match.group(1)
                        print(f"   [{role}] Requested Tool Call -> Wikipedia Search for: '{query}'")
                        search_result = get_wikipedia_summary(query)
                        tool_called = True
                        tool_success = not (isinstance(search_result, str) and search_result.startswith("Tool Error (Wikipedia API):"))
                        # Append search result to context and let agent try again
                        context += f"\n[System] Result of Wikipedia search for '{query}': {search_result}\n"
                        # Run agent again with the new context that includes the tool observation
                        output = agent.run(task, context)
                
                print(f"\n   [{role} Output First 300 chars]:\n   {output[:300].strip()}...\n")
                
                print(f"[Coordinator] -> Passing {role} output to Judge Agent for evaluation...")
                evaluation = self.judge.evaluate(agent.name, agent.role, task, output)
                
                score = evaluation.get('score', 0)
                final_score = score
                passed = evaluation.get('passed', False)
                feedback = evaluation.get('feedback', 'No feedback provided.')
                
                print(f"   [Judge Evaluation]: Score = {score}/10, Passed = {passed}")
                print(f"   [Judge Feedback]: {feedback}")
                
                if passed:
                    context += f"\n--- Output from {role} ---\n{output}\n"
                    print(f"[Coordinator] -> {role} succeeded. Advancing pipeline.")
                else:
                    print(f"[Coordinator] -> Output rejected by Judge. Feedback added to context. Re-assigning to {role}.")
                    context += f"\n[Judge Feedback to {role} for previous attempt]: Your output was rejected, feedback: '{feedback}'. Please revise and try again.\n"
                    
            if not passed:
                print(f"\n[Coordinator] FATAL ERROR: {role} Agent failed {max_attempts} times and could not satisfy the Judge. Aborting to maintain project safety (Fault Tolerance mechanism).")
                stages.append({
                    "role": role,
                    "attempts": attempts,
                    "final_score": int(final_score) if isinstance(final_score, int) else 0,
                    "passed": False,
                    "tool_called": bool(tool_called),
                    "tool_success": bool(tool_success),
                })
                return {
                    "final_context": context,
                    "stages": stages,
                }

            stages.append({
                "role": role,
                "attempts": attempts,
                "final_score": int(final_score) if isinstance(final_score, int) else 0,
                "passed": bool(passed),
                "tool_called": bool(tool_called),
                "tool_success": bool(tool_success),
            })
                
        print("\n============================================")
        print("[Coordinator] Pipeline Completed successfully.")
        print("Final Output Document generated by Writer.")
        print("============================================\n")
        
        return {
            "final_context": context,
            "stages": stages,
        }
