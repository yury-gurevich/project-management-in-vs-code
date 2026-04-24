# Vision and Scope — The Privacy-First Edge

Date: 2026-04-19
Status: adopted direction, informing all sprint work

---

## The one-sentence version

Build a stock trading system where **nothing leaves the operator's machine by
default**, every decision is explainable in plain language, and the system gets
smarter over time by learning from its own history.

---

## The target operator

A single privacy-wary individual investor who:

- Wants institutional-grade analysis on consumer hardware (16 GB RAM, no GPU)
- Does not trust SaaS trading platforms with their data
- Will only expand their trust if the system *proves* it before automating
- Needs to understand why before they will act

This is not a hedge fund. It is not a retail brokerage app. It is the personal
quant desk of a suspicious, diligent individual who happens to know the right
questions to ask.

---

## Why distributions, not scores

Today the system emits a single `composite_score` per candidate. That is a
reasonable first approximation, but it lies by omission — it gives the operator
a point when they need a shape.

A score of 72 could mean "this trade almost always makes a small gain" or
"this trade usually loses but occasionally wins big". Those are not the same
trade. The operator cannot tell them apart from the number.

When the system emits a distribution — `P(profit > 0)`, `E[drawdown]`,
`tail_loss_p99`, `time_to_target` — the operator can see the shape, not just
the centre. The Portfolio Manager can then size positions to a **risk budget
over the distribution**, not a threshold over a score. That is the change of
unit of analysis this direction bets on.

---

## Why narration

A system that explains itself in plain language per decision builds operator
trust faster than one that does not. More practically: every explanation
persisted against a decision outcome becomes the training corpus for a future
local model trained on this system's own reasoning.

The corpus accumulates while the system runs. In 12 months it is valuable.
In 24 months it is a moat.

---

## Why privacy-first is the differentiator

The five moonshots could all be implemented with cloud APIs. The insight is
that they do **not need to be**:

| Moonshot | Cloud needed? |
|---|---|
| #1 Distributions | No — pure simulation on local hardware |
| #4 Causal DAG | No — pure statistics |
| #5 Narration | No for narration (4B local sufficient); cloud is opt-in upgrade |
| #2 Multi-agent debate | Yes for quality — but quality gap is small enough to offer as opt-in "Pro Mode" |
| #3 Self-evolving loop | No — agent SDK runs locally |

The architecture therefore is:

```
Local, always on:
  - ABIDES microstructure simulations (distributions, #1)
  - Causal DAG over signals (#4)
  - FinBERT polarity (existing)
  - Gemma 3 4B via Ollama — narration, command parsing (#5, GEM-02..08)

Cloud, explicit opt-in only (Pro Mode):
  - Gemma 31B+ — multi-agent debate (#2)
  - UX: "this sends ticker, news, and analysis data to {provider}"

Never:
  - Open-internet web search by any model
  - Open-ended "tell me about X" prompts to local models
  - Any external telemetry (no Sentry, PostHog, Datadog)
```

The privacy story is the headline feature, not a constraint.

---

## What "the data is the edge" means

The composite score algorithm is replaceable. A competitor could fork the
codebase and run the same signals. What they cannot replicate:

1. **Your execution corpus** — years of (decision, outcome) pairs generated
   by your specific operator profile against your specific universe
2. **Your reasoning corpus** — every narration persisted against a decision,
   eventually joined to realized outcomes
3. **Your counterfactual corpus** — synthetic distribution outcomes from
   ABIDES replicas, which let you study scenarios that never happened in
   live trading
4. **Your operator-action corpus** — every approve/reject/override with a
   stated reason, which eventually trains a model that knows *your* judgment

Start collecting all four streams as early as possible. Volume estimates,
gap analysis, and historical backfill strategy are in
[data-strategy-and-gap-analysis.md](data-strategy-and-gap-analysis.md).

---

## Sequencing (high level)

The full sequencing with phases and work groups is in
[integration-map.md](integration-map.md). The short version:

1. **Phase B (now):** Ship Gemma plumbing + narration MVP. Ship ABIDES
   distribution shadow cycle. These start the reasoning and counterfactual
   data streams without touching live trading paths.
2. **Phase B+ (next):** Distributions consumed by PM for sizing. Portfolio-level
   CVaR budget. Operator Confidence Ledger populated.
3. **Phase C:** Phone-first — made viable by Phase B narrations and distributions
   (compact, trustworthy surfaces to show on mobile).
4. **Phase D:** Market-pack expansion. Cloud Pro Mode optional.
5. **Phase E:** Causal DAG replaces ML-2 weighted sum, once distributional
   outcomes provide the ground truth for causal fitting.
6. **Phase F (possibly never):** Self-evolving loop. Only if the system has
   run trustworthily for 6+ months and operator chooses to delegate.
