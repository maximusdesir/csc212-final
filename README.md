# Finite-State Dialogue Manager for an LLM Ordering Chatbot

CSC 212 Theory of Computing, Fall 2026, The Catholic University of America
Maximus Desir and Roman Colaberdino

## Question

Can a DFA over user intents handle the routine steps of an ordering chatbot (greet, add item, remove item, confirm, cancel) without calling the LLM, and what fraction of LLM calls does it remove across 50 scripted ordering dialogues?

## The model

A complete 6-state DFA with the cart capped at 3 items.

- States: `C0`-`C3` (items in the cart), `Done` (accepting), `Dead` (trap)
- Start state: `C0`
- Alphabet: 8 intent events, written as single letters in JFLAP

| Symbol | Event | Symbol | Event |
|---|---|---|---|
| `g` | greet | `x` | cancel |
| `a` | add_item | `q` | ask_question |
| `r` | remove_item | `h` | request_help |
| `c` | confirm | `u` | unknown |

The DFA accepts exactly the sequences that reach a first ending: confirm with 1 to 3 items, cancel, or request_help. Anything after the ending goes to `Dead`. Turns where the DFA reads `q` or `u` are the ones sent to the LLM.

Without the cap, the language is not regular (Myhill-Nerode argument in the report).

## Repository layout

```
chatbot_dfa.jff      JFLAP 7 file for the DFA
docs/                outline, model checklist, report
src/                 Python DFA and wrapper (automata-lib)
tests/               pytest suite (24+ cases)
data/                50 scripted dialogues with intent labels
figures/             Graphviz diagrams
```

## Running it

```bash
pip install automata-lib pytest
pytest tests/
python src/run_dialogues.py data/dialogues.json
```

The last command prints accept/reject per dialogue and the LLM-call reduction, 1 - (q and u turns / total turns), by dialogue type.

To open the model, load `chatbot_dfa.jff` in JFLAP 7 and use Input > Multiple Run with strings such as `gac` (accept) and `gc` (reject).

## Status

- [x] Topic proposal (M1)
- [x] Outline and model checklist (M2, 11/12)
- [ ] Literature review, formal model, implementation and tests
- [ ] Final report and repository (12/08)
