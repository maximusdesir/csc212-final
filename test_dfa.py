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


def test_jflap_matches_code():
    # JFLAP reads each label as a literal string, so every transition must be one letter.
    import xml.etree.ElementTree as ET
    auto = ET.parse("chatbot_dfa.jff").getroot().find("automaton")
    names = {s.get("id"): s.get("name") for s in auto.iter("state")}
    edges = [(names[t.findtext("from")], t.findtext("read"), names[t.findtext("to")])
             for t in auto.iter("transition")]
    assert all(r in L for _, r, _ in edges)
    assert sorted((q, L[r], d) for q, r, d in edges) == sorted(
        (q, s, d) for q, row in DELTA.items() for s, d in row.items())


def test_llm_routing():
    assert run_dialogue(["greet", "add_item", "confirm"]) == (True, 0)
    assert run_dialogue(["greet", "ask_question", "add_item", "unknown", "confirm"]) == (True, 2)
    assert run_dialogue(["greet", "cancel", "ask_question"]) == (False, 0)


MN_REPS = {"C0": "", "C1": "a", "C2": "aa", "C3": "aaa", "Done": "ac", "Dead": "aca"}


def test_myhill_nerode_suffixes():
    # Every pair of representatives is separated by one of these suffixes (THEORY.md section 2).
    suffixes = ["", "x", "c", "rc", "rrc"]
    acc = lambda s: M.accepts_input([L[c] for c in s])
    reps = list(MN_REPS.values())
    for i, u in enumerate(reps):
        for v in reps[i + 1:]:
            assert any(acc(u + z) != acc(v + z) for z in suffixes), (u, v)


def test_uncapped_family_distinguished():
    # THEORY.md section 3: a^i and a^j differ on r^i c. Simulate an uncapped counter.
    def uncapped_accepts(s):
        n, done = 0, False
        for ch in s:
            if done:
                return False
            if ch == "a": n += 1
            elif ch == "r": n = max(n - 1, 0)
            elif ch == "c" and n >= 1: done = True
            elif ch in "xh": done = True
        return done
    for i in range(8):
        for j in range(i + 1, 9):
            z = "r" * i + "c"
            assert not uncapped_accepts("a" * i + z) and uncapped_accepts("a" * j + z)
