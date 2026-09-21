#!/usr/bin/env python3
"""Topic scoring and Campaign Brief generator based on W8 Growth OS decision layer."""

import argparse
import datetime
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"


def calculate_topic_score(relevance: float, timing: float, discussion: float, evidence: float, risk: float) -> float:
    risk = max(1.0, float(risk))
    score = (relevance * timing * discussion * evidence) / risk
    return round(score, 2)


def main():
    parser = argparse.ArgumentParser(description="5-Dimensional Topic Scoring Engine")
    parser.add_argument("--title", required=True, help="Topic proposition or title")
    parser.add_argument("--relevance", type=float, default=4.0, help="Relevance to ICP (1-5)")
    parser.add_argument("--timing", type=float, default=4.0, help="Timing & trend urgency (1-5)")
    parser.add_argument("--discussion", type=float, default=3.5, help="Social engagement & debate potential (1-5)")
    parser.add_argument("--evidence", type=float, default=4.5, help="Hard facts & data evidence (1-5)")
    parser.add_argument("--risk", type=float, default=1.0, help="Compliance/reputation risk level (1-5)")
    parser.add_argument("--mode", default="Demand-Led", choices=["Demand-Led", "Launch-Spike", "Case-Study", "Thought-Leadership"])
    parser.add_argument("--out", help="Output path for generated brief (optional)")

    args = parser.parse_args()

    score = calculate_topic_score(args.relevance, args.timing, args.discussion, args.evidence, args.risk)
    decision = "立项执行 (GO)" if score >= 40.0 else ("观察待定 (WATCH)" if score >= 20.0 else "放弃 (DROP)")

    print(f"==========================================")
    print(f" Topic Decision Score: {score} -> {decision}")
    print(f"==========================================")
    print(f" Title:        {args.title}")
    print(f" Mode:         {args.mode}")
    print(f" Relevance:    {args.relevance} / 5.0")
    print(f" Timing:       {args.timing} / 5.0")
    print(f" Discussion:   {args.discussion} / 5.0")
    print(f" Evidence:     {args.evidence} / 5.0")
    print(f" Risk Factor:  {args.risk} / 5.0")
    print(f"==========================================")

    if args.out:
        tmpl = (TEMPLATES_DIR / "campaign-brief.template.md").read_text(encoding="utf-8")
        today = datetime.date.today().strftime("%Y%m%d")
        filled = tmpl.replace("TOPIC-YYYYMMDD-01", f"TOPIC-{today}-01")
        filled = filled.replace("[Demand-Led 需求驱动 / Launch Spike 版本首发 / Case Study 深度案例 / Thought Leadership 行业反思]", args.mode)
        filled = filled.replace("[一句话概括本期内容要向用户传达的最关键判断或事实]", args.title)
        filled = filled.replace("[Score]", str(score))
        filled = filled.replace("[立项执行 / 纳入观察 / 放弃]", decision)
        filled = filled.replace("YYYY-MM-DD", datetime.date.today().isoformat())
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(filled, encoding="utf-8")
        print(f"[GENERATED] Campaign Brief written to {out_p}")


if __name__ == "__main__":
    main()
