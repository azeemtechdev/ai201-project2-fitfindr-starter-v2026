# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** Search depends on text query interpretation, and downstream tools make LLM calls. A 4/5 target accounts for occasional API timeouts, rate pacing pauses, or ambiguous natural language phrasing, while ensuring the end-to-end pipeline is fundamentally reliable.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** Branching on an empty search result is controlled by deterministic Python code (`if not results:`), not an LLM decision. There is no randomness here: if the listing list is empty, execution must halt immediately every single time.

---

### Criterion 3 (State / Data Handoff)
In 5 of 5 successful search runs, the item ID (`new_item['id']`) passed to `suggest_outfit` exactly matches the ID of the top listing produced by `search_listings`, with zero intermediate prompts to the user.

**Why this target:** Session state management is pure code logic. Once `search_listings` identifies the best candidate, passing its dictionary reference or ID into the next function call should never fail or hallucinate an ID.

---

### Criterion 4 (Fit Card Content & Formatting)
Across 5 generated fit cards from valid listings, at least 4 of 5 fit cards explicitly include the item's title, its listed price, and at least two relevant aesthetic hashtags (e.g., `#vintage`, `#streetwear`).

**Why this target:** `create_fit_card` uses an LLM, meaning the exact wording varies run to run. Setting a 4/5 threshold accommodates slight stochastic variance in formatting while enforcing that critical factual anchors (name, price) and styling elements (hashtags) are consistently generated.

---

### Criterion 5 (Price Constraint Fidelity)
Given 5 distinct search queries containing explicit price ceilings (e.g., `"under $30"`, `"under $45"`), 5 of 5 runs return exclusively listings whose `price` attribute is less than or equal to the specified `max_price`.

**Why this target:** A thrift agent that returns out-of-budget items fails its primary utility. Price filtering in `search_listings` is an exact numeric comparison (`listing['price'] <= max_price`), so zero leakage or over-budget items should occur.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
