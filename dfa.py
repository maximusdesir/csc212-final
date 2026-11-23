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
    by_type = defaultdict(lambda: {"n": 0, "turns": 0, "llm": 0, "agree": 0})
    for line in open(path):
        d = json.loads(line)
        accepted, calls = run_dialogue(d["intents"])
        t = by_type[d["type"]]
        t["n"] += 1
        t["turns"] += len(d["intents"])
        t["llm"] += calls
        t["agree"] += accepted == d["expected_accept"]
    for name, t in sorted(by_type.items()):
        print(f"{name:10} n={t['n']:3} reduction={1 - t['llm'] / t['turns']:.1%} "
              f"label_agreement={t['agree']}/{t['n']}")


if __name__ == "__main__":
    evaluate(sys.argv[1] if len(sys.argv) > 1 else "dialogues.jsonl")
