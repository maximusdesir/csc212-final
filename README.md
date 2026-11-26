# Letting a DFA Run the Routine Turns
Finite-state dialogue manager for an LLM ordering chatbot.

CSC 212 Theory of Computing
Fall 2026
Catholic University of America. 
Maximus Desir and Roman Colaberdino.

**Question:** Can a DFA over user intents handle the routine turns of an ordering chatbot without calling the
LLM, and what fraction of LLM calls does it remove?

## Model

Accepts exactly the intent sequences that reach their first ending event: `confirm` with 1 to 3 items,
`cancel`, or `request_help`. Anything after the ending is rejected.

- Σ = {greet, add_item, remove_item, confirm, cancel, ask_question, request_help, unknown} (JFLAP: g a r c x q h u)
- Q = {C0, C1, C2, C3, Done, Dead}, start C0, F = {Done}. Ck = k items in cart.
- `add_item`: Ck → Ck+1 (C3 stays). `remove_item`: Ck → Ck−1 (C0 stays).
- `confirm`: Ck → Done for k ≥ 1, C0 stays. `cancel`, `request_help`: → Done.
- `greet`, `ask_question`, `unknown`: self-loops. The last two are the turns sent to the LLM.
- Done and Dead go to Dead on every symbol.

The cap at 3 is what keeps memory bounded; an uncapped cart is not regular.

## Files

- `dfa.py`: the DFA, a turn-by-turn runner that counts LLM calls, and the evaluation
- `test_dfa.py`: 24 accept/reject cases, completeness, 9 → 6 state minimization, LLM routing
- `dialogues.jsonl`: 50 scripted dialogues, one per line (30 routine, 10 question, 5 cancel, 5 help)

## Run

```bash
pip install -r requirements.txt
pytest -q
python dfa.py dialogues.jsonl
```

**Metric:** LLM-call reduction = 1 − (LLM turns ÷ total turns) per dialogue type, against a baseline that
sends every turn to the LLM. Turns after the ending are never sent to the LLM.

**Dialogues:** written by Maximus Desir, Roman Colaberdino, and Claude (Anthropic), with each intent label
checked by hand. All orders use one fixed menu: cheeseburger, chicken sandwich, veggie wrap, fries, onion rings,
side salad, coke, lemonade, milkshake. Requests outside the 8 intents ("make that a large", "no pickles") are
labeled `unknown`. Q07 and Q09 are abandoned orders that never reach an ending, so they are labeled reject.
These are realistic but scripted, not real user data.

**Dialogue format:**
`{"id": "R01", "type": "routine", "intents": ["greet", "add_item", "confirm"], "expected_accept": true}`

## TODO

- [x] Write all 50 dialogues
- [ ] Myhill–Nerode and non-regularity proofs in the report

## Limitations

Intents outside Σ ("make that a large") map to `unknown` and go to the LLM. The DFA tracks how many items
are in the cart, not which ones. Results assume correct intent labels.
