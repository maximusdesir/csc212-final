"""Shape checks on dialogues.jsonl. These never compute expected_accept, so
label agreement in the evaluation is still a real check on the hand labels."""
import json
from collections import Counter

import pytest

from dfa import DELTA, SIGMA

with open("dialogues.jsonl") as f:
    DIALOGUES = [json.loads(line) for line in f if line.strip()]

ENDINGS = {"routine": "confirm", "question": "confirm", "cancel": "cancel", "help": "request_help"}


def test_type_counts():
    assert Counter(d["type"] for d in DIALOGUES) == {"routine": 30, "question": 10, "cancel": 5, "help": 5}


def test_unique_ids():
    assert len({d["id"] for d in DIALOGUES}) == len(DIALOGUES)


@pytest.mark.parametrize("d", DIALOGUES, ids=lambda d: d["id"])
def test_dialogue_shape(d):
    intents = d["intents"]
    assert 6 <= len(intents) <= 10
    assert set(intents) <= SIGMA
    assert len(d.get("utterances", intents)) == len(intents)
    if d["type"] == "routine":
        assert "ask_question" not in intents
    if d["type"] == "question":
        assert "ask_question" in intents

    # No turns after the first ending, and the ending matches the type.
    state = "C0"
    for i, s in enumerate(intents):
        state = DELTA[state][s]
        if state == "Done":
            assert i == len(intents) - 1, f"turns after ending at turn {i}"
            assert s == ENDINGS[d["type"]]
