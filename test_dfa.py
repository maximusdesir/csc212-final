import pytest
from automata.fa.dfa import DFA

from dfa import DELTA, M, SIGMA, run_dialogue

# JFLAP letters, so cases are easy to compare with the diagram
L = dict(g="greet", a="add_item", r="remove_item", c="confirm", x="cancel",
         q="ask_question", h="request_help", u="unknown")

ACCEPT = ["gac", "aaaac", "gh", "gaqarc", "gax", "x", "gx", "ac",
          "gaaarac", "gcac", "guuuuuuuuuuac", "ggggac", "raac"]
REJECT = ["", "gr", "arc", "gaca", "gc", "axc", "gaq", "ghg", "gacc", "uuuu", "aaaa"]


@pytest.mark.parametrize("s", ACCEPT)
def test_accept(s):
    assert M.accepts_input([L[c] for c in s])


@pytest.mark.parametrize("s", REJECT)
def test_reject(s):
    assert not M.accepts_input([L[c] for c in s])


def test_complete_and_trap():
    assert all(set(row) == SIGMA for row in DELTA.values())
    assert set(DELTA["Dead"].values()) == {"Dead"}


def test_minimization_9_to_6():
    # First draft: separate Start state and three ending states.
    d = {k: dict(v) for k, v in DELTA.items() if k != "Done"}
    d["Start"] = {**d["C0"], **{s: "Start" for s in ("greet", "ask_question", "unknown", "confirm")}}
    for k in [*[f"C{i}" for i in range(4)], "Start"]:
        d[k].update(cancel="Cancelled", request_help="Handoff")
        if d[k]["confirm"] == "Done":
            d[k]["confirm"] = "Ordered"
    for end in ("Ordered", "Cancelled", "Handoff"):
        d[end] = {s: "Dead" for s in SIGMA}
    draft = DFA(states=set(d), input_symbols=SIGMA, transitions=d,
                initial_state="Start", final_states={"Ordered", "Cancelled", "Handoff"})
    assert len(draft.states) == 9
    assert len(draft.minify().states) == 6
    assert draft == M


def test_llm_routing():
    assert run_dialogue(["greet", "add_item", "confirm"]) == (True, 0)
    assert run_dialogue(["greet", "ask_question", "add_item", "unknown", "confirm"]) == (True, 2)
    assert run_dialogue(["greet", "cancel", "ask_question"]) == (False, 0)
