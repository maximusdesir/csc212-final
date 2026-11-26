# Theory

Symbols use the JFLAP letters: g greet, a add_item, r remove_item, c confirm, x cancel, q ask_question,
h request_help, u unknown. `L` is the language of the DFA in `dfa.py`.

## 1. Minimization: 9 states → 6

The first design had 9 states: Start, C0, C1, C2, C3, Ordered, Cancelled, Handoff, Dead, with
F = {Ordered, Cancelled, Handoff}.

**Round 0** (accepting vs. non-accepting): mark every pair with one state in F and one not.
Groups: {Ordered, Cancelled, Handoff} and {Start, C0, C1, C2, C3, Dead}.

**Round 1:** split the non-accepting group by where each symbol leads.

- Dead goes to Dead on every symbol; every other non-accepting state goes to F on x. Mark Dead against all of them.
- On c, Start and C0 stay non-accepting, while C1, C2, C3 go to Ordered ∈ F. Mark {Start, C0} against {C1, C2, C3}.

**Round 2:** on r, C1 → C0 and C2 → C1. (C0, C1) was marked in round 1, so mark (C1, C2). Same for
(C1, C3), since C3 → C2 and (C0, C2) is marked.

**Round 3:** on r, C2 → C1 and C3 → C2, and (C1, C2) is marked, so mark (C2, C3).

**Round 4:** nothing new is marked. The unmarked pairs are:

- (Start, C0): identical rows on every symbol.
- (Ordered, Cancelled), (Ordered, Handoff), (Cancelled, Handoff): all accepting, all go to Dead on every symbol.

Merging them gives {C0, C1, C2, C3, Done, Dead}: 6 states. `test_minimization_9_to_6` checks this with
automata-lib and confirms the 9-state draft and the final DFA accept the same language.

## 2. Myhill–Nerode: 6 states are necessary

Two strings u, v are distinguishable if some suffix z has exactly one of uz, vz in L. If n strings are
pairwise distinguishable, every DFA for L needs at least n states.

Take one representative per state:

| State | Representative |
|---|---|
| C0 | ε |
| C1 | a |
| C2 | aa |
| C3 | aaa |
| Done | ac |
| Dead | aca |

Distinguishing suffixes for all 15 pairs:

| Pair | Suffix z | In L | Not in L |
|---|---|---|---|
| Done vs. any other | ε | ac | the other |
| Dead vs. C0, C1, C2, C3 | x | ε x, a x, aa x, aaa x | aca x |
| C0 vs. C1, C2, C3 | c | a c, aa c, aaa c | c (empty cart, no ending) |
| C1 vs. C2 | rc | aa rc | a rc (cart empties) |
| C1 vs. C3 | rc | aaa rc | a rc |
| C2 vs. C3 | rrc | aaa rrc | aa rrc |

So L has at least 6 Myhill–Nerode classes. Our DFA has 6 states, so it is minimal, and L is regular
(finite index). `test_myhill_nerode_suffixes` checks every row of this table against the DFA.

## 3. The uncapped cart is not regular

Let L∞ be the same language with no cap: add_item always increments the count, remove_item on an empty
cart does nothing, and confirm ends the conversation only when the count is at least 1.

**Claim:** L∞ is not regular.

**Proof (Myhill–Nerode).** Consider the infinite set {aⁱ : i ≥ 0}. Take any i < j and the suffix z = rⁱc.

- aⁱ rⁱ c: the cart reaches 0 after the i removes, so c does not end the conversation. Not in L∞.
- aʲ rⁱ c: the cart holds j − i ≥ 1 items, so c ends the conversation. In L∞.

So aⁱ and aʲ are distinguishable for every i ≠ j. That gives infinitely many Myhill–Nerode classes, so no
DFA recognizes L∞, and L∞ is not regular. ∎

**Intuition:** to know whether confirm is legal, the machine must know whether removes have caught up
with adds, which needs an unbounded counter. Capping the cart at 3 bounds the counter, which is why the
6-state DFA works. A one-counter automaton (a PDA with a single stack symbol) recognizes L∞.
