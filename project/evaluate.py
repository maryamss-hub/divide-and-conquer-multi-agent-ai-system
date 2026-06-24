import json
import time
from typing import Any, Dict, List

from llm_client import GroqLLM
from orchestrator import MultiAgentOrchestrator


TEST_TASKS = [
    "Write a report on the causes and effects of climate change",
    "Explain the pros and cons of nuclear energy",
    "Summarize the economic impact of COVID-19",
    "Describe the history and future of artificial intelligence",
    "Analyze the causes of World War I",
]


def _stage_map(stages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {s.get("role"): s for s in stages}


def _fmt_score(stage: Dict[str, Any] | None) -> str:
    if not stage:
        return "-"
    val = stage.get("final_score", "-")
    return str(val)


def _total_retries(stages: List[Dict[str, Any]]) -> int:
    # retries = attempts - 1 per stage (min 0)
    total = 0
    for s in stages:
        attempts = int(s.get("attempts", 0) or 0)
        total += max(0, attempts - 1)
    return total


def main():
    llm = GroqLLM()
    orchestrator = MultiAgentOrchestrator(llm)

    results: List[Dict[str, Any]] = []

    for task in TEST_TASKS:
        start = time.time()
        run_result = orchestrator.orchestrate(task)
        elapsed_s = time.time() - start

        stages = (run_result or {}).get("stages", []) if isinstance(run_result, dict) else []
        stage_by_role = _stage_map(stages)

        tool_called_any = any(bool(s.get("tool_called")) for s in stages)

        results.append(
            {
                "task": task,
                "time_seconds": elapsed_s,
                "final_context": (run_result or {}).get("final_context", "") if isinstance(run_result, dict) else "",
                "stages": stages,
                "planner_score": stage_by_role.get("Planner", {}).get("final_score"),
                "researcher_score": stage_by_role.get("Researcher", {}).get("final_score"),
                "writer_score": stage_by_role.get("Writer", {}).get("final_score"),
                "planner_passed": stage_by_role.get("Planner", {}).get("passed"),
                "researcher_passed": stage_by_role.get("Researcher", {}).get("passed"),
                "writer_passed": stage_by_role.get("Writer", {}).get("passed"),
                "planner_attempts": stage_by_role.get("Planner", {}).get("attempts"),
                "researcher_attempts": stage_by_role.get("Researcher", {}).get("attempts"),
                "writer_attempts": stage_by_role.get("Writer", {}).get("attempts"),
                "tool_called": tool_called_any,
                "tool_success": stage_by_role.get("Researcher", {}).get("tool_success", False),
            }
        )

    # Print summary table
    headers = ["Task", "Planner", "Researcher", "Writer", "Total retries", "Tool called"]
    rows = []
    for r in results:
        stages = r.get("stages", [])
        stage_by_role = _stage_map(stages)
        rows.append(
            [
                r["task"],
                _fmt_score(stage_by_role.get("Planner")),
                _fmt_score(stage_by_role.get("Researcher")),
                _fmt_score(stage_by_role.get("Writer")),
                str(_total_retries(stages)),
                "Y" if r.get("tool_called") else "N",
            ]
        )

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def print_row(values):
        line = " | ".join(str(values[i]).ljust(col_widths[i]) for i in range(len(values)))
        print(line)

    print("\n=== EVALUATION SUMMARY ===\n")
    print_row(headers)
    print("-+-".join("-" * w for w in col_widths))
    for row in rows:
        print_row(row)

    # Save JSON results
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save human-readable summary
    lines = []
    lines.append("EVALUATION SUMMARY\n")
    lines.append(" | ".join(headers))
    lines.append("-" * 80)
    for row in rows:
        lines.append(" | ".join(row))
    lines.append("")
    lines.append("Per-task details are saved in eval_results.json")

    with open("eval_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()

