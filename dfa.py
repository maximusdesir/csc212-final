"""6-state dialogue DFA, turn-by-turn wrapper, and LLM-call metric.

Accepts exactly the intent sequences that reach their first ending event
(confirm with 1-3 items, cancel, or request_help). Anything after the ending is rejected.
"""

import json
import sys
from collections import defaultdict

from automata.fa.dfa import DFA

SIGMA = {"greet", "add_item", "remove_item", "confirm", "cancel",
         "ask_question", "request_help", "unknown"}
LLM_SYMBOLS = {"ask_question", "unknown"}
CAP = 3


def cart_row(k):
    row = {s: f"C{k}" for s in SIGMA}  # greet, ask_question, unknown self-loop
    row["add_item"] = f"C{min(k + 1, CAP)}"
    row["remove_item"] = f"C{max(k - 1, 0)}"
    row["confirm"] = "Done" if k >= 1 else "C0"
    row["cancel"] = row["request_help"] = "Done"
    return row


DELTA = {f"C{k}": cart_row(k) for k in range(CAP + 1)}
DELTA["Done"] = {s: "Dead" for s in SIGMA}
DELTA["Dead"] = {s: "Dead" for s in SIGMA}

M = DFA(states=set(DELTA), input_symbols=SIGMA, transitions=DELTA,
        initial_state="C0", final_states={"Done"})


def run_dialogue(intents, llm=lambda turn: "[LLM reply]"):
    """Run turn by turn. Returns (accepted, llm_calls). Only routes to the LLM before the ending."""
    state, calls = "C0", 0
    for s in intents:
        if s in LLM_SYMBOLS and state.startswith("C"):
            llm(s)
            calls += 1
        state = DELTA[state][s]
    return state == "Done", calls


def evaluate(path):
    """Returns {type: {n, turns, llm, agree, reduction}} plus an 'overall' row, and the disagreeing ids."""
    rows = defaultdict(lambda: {"n": 0, "turns": 0, "llm": 0, "agree": 0})
    disagree = []
    for line in open(path):
        d = json.loads(line)
        accepted, calls = run_dialogue(d["intents"])
        for key in (d["type"], "overall"):
            r = rows[key]
            r["n"] += 1
            r["turns"] += len(d["intents"])
            r["llm"] += calls
            r["agree"] += accepted == d["expected_accept"]
        if accepted != d["expected_accept"]:
            disagree.append(d["id"])
    for r in rows.values():
        r["reduction"] = 1 - r["llm"] / r["turns"]
    return dict(rows), disagree


def to_markdown(rows, disagree):
    order = [k for k in ("routine", "question", "cancel", "help") if k in rows] + ["overall"]
    lines = ["| Type | Dialogues | Turns | LLM turns | LLM-call reduction | Label agreement |",
             "|---|---|---|---|---|---|"]
    for k in order:
        r = rows[k]
        lines.append(f"| {k} | {r['n']} | {r['turns']} | {r['llm']} | {r['reduction']:.1%} | {r['agree']}/{r['n']} |")
    lines.append("")
    lines.append("Baseline sends every turn to the LLM (0% reduction). "
                 f"Disagreements: {', '.join(disagree) or 'none'}.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "dialogues.jsonl"
    table = to_markdown(*evaluate(path))
    print(table)
    with open("results.md", "w") as f:
        f.write("# Results\n\n" + table)
