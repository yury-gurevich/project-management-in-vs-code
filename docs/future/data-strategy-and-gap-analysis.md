# Data Strategy and Gap Analysis

Date: 2026-04-19
Status: adopted framing — informs sprint and backfill priorities

> **The key reframe.** The composite score algorithm is replaceable. The data
> corpus accumulated over years of real operation is not. Build for the corpus
> first; the algorithms improve themselves once the corpus exists.

---

## 1. Three classes of data

Every decision the system makes touches three distinct data streams. You need
all three for the learning loops to close.

### Class 1 — Execution data (what happened)
Answers: what did the system do, and what were the realized outcomes?

**Currently captured (strong):**
- `Recommendation` — every approved/rejected recommendation
- `Position` / `Trade` — entry/exit price, dates, P&L
- `AnalystDiagnostic` — per-candidate signal breakdown, reject reason
- `SimulationRun` / `SimulationScenario` / `SimulationOutcome` — ABIDES shadow runs
- `AgentEvent` / observability log — every pipeline stage event
- `ScanResult` — every scanned candidate

**Gaps:**
- No explicit `PositionAttribution` row at exit time — when a position closes,
  the active signal weights and their marginal contribution are not snapshotted.
  Without this, post-hoc attribution requires replaying history.
- No daily `RegimeLabel` row — regime is computed per-pipeline but not persisted
  as a standalone time series. Regime-conditioned analysis is messy without it.

### Class 2 — Reasoning data (why it happened)
Answers: what was the system's (and operator's) stated rationale at decision time?

**Currently captured (thin):**
- `rationale_json` on `Recommendation` — structured but terse
- Control-plane events (approval, rejection, override) — status flags, no text

**Gaps — all of these need to be built:**
- **Per-decision narration** (Gemma sprint) — plain-language explanation of
  every accept/reject/override, persisted and later joined to outcomes
- **Operator-action reason** — when the operator approves/rejects/overrides,
  a free-text or selected-from-list reason should persist. This is the corpus
  that eventually trains a model that knows *your* judgment.
- **Regime-conditioned rationale** — why this regime label at this time?
  Currently inferred from raw VIX/breadth; a persisted explanation would close
  the loop for future audits.

### Class 3 — Counterfactual data (what would have happened)
Answers: under varied conditions, what was the distribution of possible outcomes?

**Currently captured (absent):**
- ABIDES PM shadow and research shadow run, but they produce one scenario per
  recommendation, not a distribution of scenarios.

**What the ABIDES distribution sprint builds:**
- N=24 replica scenarios per approved candidate, varying seed, news timing,
  queue depth, and latency profile
- One `RecommendationDistribution` aggregate row per candidate: P(profit),
  E[drawdown], tail_loss_p99, time_to_target
- Raw replicas persisted via existing simulation tables for later calibration

This data class is the only one that cannot be collected from live trading
alone — it requires simulation. That makes it uniquely valuable over time.

---

## 2. Volume and retention estimates

Based on a single-user system with moderate selectivity and full market coverage.

| Stream | Per day | Per year | Bytes/row est. | Year-1 storage |
|---|---|---|---|---|
| Diagnostics (all surveyed candidates) | ~50 | ~12,500 | ~5 KB | ~60 MB |
| Recommendations (survivors) | ~5 | ~1,250 | ~3 KB | ~4 MB |
| Closed positions with outcomes | ~1–3 | ~250–750 | ~3 KB | ~2 MB |
| Distribution replicas (new, N=24/candidate) | ~120 | ~30,000 | ~2 KB | ~60 MB |
| Narrations (new, ~10/day once live) | ~10 | ~2,500 | ~1 KB | ~2.5 MB |
| Gemma call audit (prompt + output verbatim) | ~10 | ~2,500 | ~4 KB | ~10 MB |
| News articles + embeddings | ~200 | ~50,000 | ~10 KB | ~500 MB |
| Agent events / observability | ~500 | ~125,000 | ~0.5 KB | ~60 MB |

**Total year-1: under 1 GB.** On modern hardware, this is trivial.

**Retention policy: keep everything, forever.** The value of the corpus
compounds over time. The cost of keeping it is negligible. Never age out
decision data — it is the ground truth you cannot reconstruct.

---

## 3. Time-to-useful thresholds

Different learning applications need different minimum corpus sizes.

| Application | Minimum rows needed | Estimated time to reach |
|---|---|---|
| First signal-weight retraining from outcomes | ~300 closed positions | 4–12 months live |
| Distribution calibration check (sim vs reality) | ~200 (distribution, outcome) pairs | 4–8 months after dist sprint ships |
| Regime-conditioned signal analysis | ~500 (diagnostic, outcome) per regime | 12–18 months live |
| Causal DAG (Moonshot #4) | ~1,000–5,000 (signal_state, outcome) tuples | 18–24 months live |
| Fine-tune narration model on own corpus (Moonshot #5 phase 2) | ~2,000–7,000 narrations | 12–24 months at 10/day |
| Self-evolving signal proposals (Moonshot #3) | ~1,000 diagnostics with regime labels | 3–6 months live |

**The implication:** start the plumbing (narration + distribution) now. Every
month that passes without them is a month of corpus you cannot recover by
waiting. The algorithms can be improved later; the corpus cannot be backdated.

---

## 4. What 2 years of historical data unlocks

Historical market data (OHLCV, news, filings) for the past 2 years can be
replayed against the current pipeline logic to backfill the corpus, compressing
2 years of waiting into ~1–2 weeks of engineering + compute.

### What backfills cleanly

| Stream | Source | Notes |
|---|---|---|
| All technical signals (RSI, MACD, ATR, etc.) | Historical OHLCV | Trivial — pure functions of price history |
| VIX → regime labels | Historical VIX | Trivial |
| News + FinBERT polarity | Finnhub historical news API | Embeddings and scores are computable retroactively |
| ABIDES distributions | Synthetic, deterministic | Replay against historical context; same seeds = same outcomes |
| **Realized outcomes** | Forward-looking returns from any historical entry date | This is the gold. Every backfilled recommendation instantly has known N-day returns. |
| Composite scores and weighted fusion | Derived from the above | Compute on demand |

With a 2-year backfill, you start with ~750–1,500 closed-position outcomes
on day 1 instead of month 12. That unlocks ML-2 retraining, distribution
calibration, and causal DAG work *immediately* rather than after a year of
live operation.

### What does NOT backfill

| Stream | Why not |
|---|---|
| Operator decisions (approve/reject/override reason) | There is no record of what *you* would have done in 2023–2024. Has to accumulate live. |
| Real fill slippage and partial-fill behaviour | Simulation is a proxy; authentic execution data is live-only. |
| Authentic at-the-time narrations | Gemma can generate narrations against historical diagnostics, but they reflect *today's* model, not the system's voice at the time. Still useful for fine-tuning; just not temporally authentic. |
| Intraday news-spike timing | Daily-bar news loses within-session timing. Requires minute-bar data + intraday news timestamps. |

### The look-ahead bias trap (the real engineering challenge)

The engineering cost of backfill is not compute — it is **point-in-time
correctness**. The pipeline reads "now." Backfill must read "as of date X"
without leaking future data:

- **Price:** easy — truncate at the as-of date.
- **Fundamentals:** hard. Today's P/E reflects today's earnings. Using it on
  a 2023 historical date is look-ahead bias. Requires a point-in-time
  fundamental source (Sharadar, EDGAR with filing-date timestamps, or accept
  that fundamental signals carry residual bias in the backfill corpus).
- **News:** use the original publication timestamp, not the latest revision
  date. Articles get edited and re-tagged.
- **EDGAR filings:** safe — each filing has an exact submission date.

---

## 5. Gap analysis — the punch list

### Gaps that block data accumulation (fix now)

| Gap | Impact | Effort |
|---|---|---|
| No Gemma narration plumbing | Reasoning corpus never starts | Sprint 1 (Gemma track) |
| No ABIDES per-candidate distribution | Counterfactual corpus never starts | Sprint 1 (ABIDES track) |
| No daily `RegimeLabel` row | Regime-conditioned analysis fragile | ~2 days |
| No `PositionAttribution` at exit | Attribution requires full history replay | ~3 days |
| No operator-action reason field | Operator-judgment corpus never starts | ~1 day |

### Gaps that block the learning loops (fix in Phase B+)

| Gap | Impact | Effort |
|---|---|---|
| No (distribution, outcome) join table | Cannot calibrate sim vs reality | ~1 sprint after distribution ships |
| No training-set assembler | ML-2 retraining stays manual | ~3 days — a nightly job building a flat Parquet from (recommendation, distribution, narration, outcome) |
| No historical backfill harness | 2 years of potential corpus sits untapped | ~2–4 weeks engineering + 1 week compute |
| ML-2 weights not outcome-fitted | Composite score is hand-tuned, not learned | Unblocked once ~300 outcomes exist |

### Gaps that block the consumption layer (Sprint 2+)

| Gap | Impact | Effort |
|---|---|---|
| PM does not consume distributions | Kelly / CVaR sizing not available | Sprint 2 ABIDES track |
| No portfolio-level joint distribution | MPT apparatus unavailable | Sprint 2–3 |
| No Operator Confidence Ledger | PRD §11.1 remains Level 0 | Phase B+ |

---

## 6. Recommended sequencing

```
Now
│
├── Sprint 1 (parallel tracks)
│     ├── Gemma narration plumbing — starts reasoning corpus
│     └── ABIDES per-candidate distribution — starts counterfactual corpus
│
├── +1 week alongside the sprints (cheap additions)
│     ├── Daily RegimeLabel row (2 days)
│     ├── PositionAttribution at exit (3 days)
│     └── Operator-action reason field on approve/reject/override (1 day)
│
├── +1 month
│     └── Training-set assembler: nightly job → Parquet
│           (recommendation, distribution, narration, outcome joined flat)
│
├── +2 months (if historical data available)
│     └── Backfill harness: run pipeline as-of(date) for 2 years
│           → ~750–1500 outcomes on day 1
│           → unlocks first distribution calibration check
│
├── +3 months
│     └── Distribution calibration: does P(profit) match realized win-rate?
│           If yes: distributions are honest → PM can start consuming them
│           If no: you know exactly which signals mislead → fix them
│
├── +6 months
│     └── ML-2 weight retraining from realized outcomes
│           (replaces current hand-tuned defaults)
│
├── +12 months
│     ├── Causal DAG (Moonshot #4) becomes viable — enough rows
│     └── Narration fine-tuning corpus reaches useful size
│
└── +18–24 months
      ├── Self-evolving signal proposals (Moonshot #3)
      └── Local fine-tuned narration model (Moonshot #5 phase 2)
```

The two things you still must wait for regardless of backfill:
- **Operator-action corpus** — requires live operation
- **Live execution data** — simulation is a proxy, not a substitute

Everything else is recoverable from 2 years of historical data. The backfill
harness is worth building.
