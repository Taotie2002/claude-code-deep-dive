#!/usr/bin/env python3
"""
生成评测汇总报告
"""
import json
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    summary = {
        "overall_score": 0.0,
        "pass_rate": "0%",
        "passed": False,
        "dimensions": {},
        "details": [],
    }

    scores = []
    for json_file in results_dir.glob("*.json"):
        if json_file.name == "summary.json":
            continue
        try:
            data = json.loads(json_file.read_text())
            dim = json_file.stem  # correctness, safety, style
            summary["dimensions"][dim] = {
                "score": data.get("score", 0),
                "passed": data.get("passed", False),
                "reasoning": data.get("reasoning", "")[:200],
            }
            scores.append(data.get("score", 0))
        except (json.JSONDecodeError, KeyError):
            pass

    if scores:
        summary["overall_score"] = round(sum(scores) / len(scores), 3)
        passed_count = sum(1 for s in scores if s >= 0.7)
        summary["pass_rate"] = f"{passed_count}/{len(scores)}"
        summary["passed"] = summary["overall_score"] >= 0.7

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
