#!/usr/bin/env python3
"""
检查评测门禁是否通过
"""
import json
import argparse
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--threshold", type=float, default=0.7)
    args = parser.parse_args()

    summary = json.loads(open(args.summary).read())
    score = summary.get("overall_score", 0)

    print(f"Overall Score: {score}")
    print(f"Threshold: {args.threshold}")
    print(f"Passed: {score >= args.threshold}")

    if score < args.threshold:
        print(f"::error::评测未通过门禁: {score} < {args.threshold}")
        sys.exit(1)
    else:
        print(f"::notice::评测通过门禁: {score} >= {args.threshold}")
        sys.exit(0)


if __name__ == "__main__":
    main()
