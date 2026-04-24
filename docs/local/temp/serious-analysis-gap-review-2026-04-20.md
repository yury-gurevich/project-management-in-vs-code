# "Serious Business Analyst" Gap Review

**Date:** 2026-04-20
**Status:** scratch review — not load-bearing; delete at sprint closeout
**Question it answers:** do we have enough *deterministic* financial methods
to present our output as serious business analysis, not hobbyist trading?
**Context:** respects [docs/PRD-v2.md](../../PRD-v2.md) and
[docs/future/](../../future/) — this file only flags gaps that are *not
already* on those roadmaps. Where a gap is on the roadmap, it is linked, not
re-specified.

---

## 1. What is already credible

The stack an outside quant reviewer would acknowledge as serious:

| Category | What exists | Module |
|---|---|---|
| Technical signals | RSI, RSI2, MACD, Bollinger, trend, SMA200, EMA crossover, ATR, OBV, Stochastic, Williams %R, Choppiness, Golden Cross, Turnaround Tuesday, Nadaraya-Watson, swing/geometric patterns, support/resistance, relative strength | [analyst.py:555-1166](../../../src/trading/agents/analyst.py#L555-L1166) |
| Fundamentals | EDGAR (point-in-time filings), Finnhub basics, growth fallback merge, provider snapshotting | [analyst.py:283-412](../../../src/trading/agents/analyst.py#L283-L412), [services/edgar.py](../../../src/trading/services/edgar.py) |
| Sentiment | FinBERT polarity over Finnhub articles, news embeddings, news-impact model | [services/finbert.py](../../../src/trading/services/finbert.py), [ml/news_impact.py](../../../src/trading/ml/news_impact.py) |
| Macro / regime | FRED series, VIX-based regime, regime-gated execution | [services/fred.py](../../../src/trading/services/fred.py), [services/regime.py](../../../src/trading/services/regime.py) |
| Research rigor | Sharpe, **Deflated Sharpe (López de Prado)**, skew, kurtosis, **Probability of Backtest Overfitting (CSCV)**, **purged CV** | [research/metrics.py](../../../src/trading/research/metrics.py), [research/validation.py:100-183](../../../src/trading/research/validation.py#L100-L183) |
| Backtest / shadow | Replay harness, shadow forecasts, evidence tables, forward-outcome tracking | [research/backtest.py](../../../src/trading/research/backtest.py), [ml/shadow_forecast.py](../../../src/trading/ml/shadow_forecast.py) |
| PM checks | R/R ratio, position sizing (rule-based), sector concentration, duplicate-ticker, cash, regime-gated | [portfolio_manager.py:332-497](../../../src/trading/agents/portfolio_manager.py#L332-L497) |
| Microstructure (scaffolded) | ABIDES simulation harness | [simulation/abides/](../../../src/trading/simulation/abides/) |

**Verdict on the existing layer:** Deflated Sharpe + PBO + purged CV alone
puts you ahead of 95% of retail systems and most junior buy-side desks.
Foundation is serious.

---

## 2. What is already on the roadmap (do NOT re-spec)

The following items a serious reviewer will ask for are already planned and
sequenced. This review does **not** duplicate them.

| Expected by reviewer | Where it is planned |
|---|---|
| Distribution-based outputs (P(profit), E[drawdown], tail_loss_p99) | Moonshot #1 / Group B — [integration-map.md §4.2](../../future/integration-map.md#42-what-is-missing--the-left-to-cover-our-needs-list); shipped via 0b95d32 (archived at [docs/del/sprint-abides-distribution.md](../../del/sprint-abides-distribution.md)) |
| CVaR-budget portfolio construction | Group B4 |
| Kelly-fraction sizing from distributions | Group B4 |
| Per-candidate ABIDES counterfactual corpus | Sprint 1 ABIDES track |
| Regime-conditioned analysis data | [data-strategy-and-gap-analysis.md §5](../../future/data-strategy-and-gap-analysis.md#5-gap-analysis--the-punch-list) — *daily `RegimeLabel` row* already listed as a cheap gap |
| Position attribution at exit | Same doc — *`PositionAttribution` at exit* already listed |
| Operator-judgment corpus | Same doc — *operator-action reason field* already listed |
| Point-in-time fundamentals / look-ahead discipline | Same doc §4, "The look-ahead bias trap" |
| Causal DAG replacing weighted-sum fusion | Moonshot #4 / Group G (Phase E) |
| ML-2 outcome-fitted weight retraining | [data-strategy-and-gap-analysis.md §6](../../future/data-strategy-and-gap-analysis.md#6-recommended-sequencing) — +6 months |

**If these ship as planned, the reviewer's distributional and data-corpus
questions are answered.** The remainder of this document is only about
methods a reviewer would still ask for *even after* the above ships.

---

## 3. Net-new gaps (not on any current roadmap)

Each gap lists: what a serious reviewer expects, why it isn't solved by
what's already planned, the concrete landing-zone module, and rough effort.

### 3.1 Portfolio-level risk metrics panel

**Reviewer expects:** VaR (parametric + historical), CVaR/Expected Shortfall,
max drawdown, **Sortino**, **Calmar**, **Ulcer Index**, rolling 63-day vol,
beta vs SPY, downside-deviation. Displayed as a table with rolling windows
(30d / 90d / 252d / inception).

**Why not covered:** Group B's CVaR is *per-candidate* (distributional,
forward-looking). The gap here is *portfolio-level, realized, historical* —
computable deterministically from existing `Position` / `Trade` tables
today, no ABIDES needed, no model needed.

**Landing zone:** new `src/trading/research/risk.py` +
`research/metrics.py` additions. Consumed by a new Reporter section and a
dashboard panel.

**Effort:** ~3 days code, ~1 day dashboard wiring.

**Priority: high.** Cheap, deterministic, moves the "serious analyst" needle
the most per hour of work. Ship alongside or immediately after Sprint 1.

---

### 3.2 Transaction-cost and slippage model in backtests

**Reviewer expects:** every backtested return net of realistic costs —
commission (modeled or zero for Alpaca), **half-spread slippage**, **market
impact** as a function of ADV participation, and borrow costs if shorting is
ever enabled.

**Why not covered:** `simulate_trade_return` today
([research/backtest.py:155-191](../../../src/trading/research/backtest.py#L155-L191))
uses frictionless fills. ABIDES will eventually give per-candidate
distributional costs (Group B), but the *research backtest path* — used for
indicator proposals, replay evidence, PBO computation — stays frictionless
forever unless we build this.

**Landing zone:** new `src/trading/research/costs.py` with a pluggable
`CostModel` protocol; `simulate_trade_return` takes a cost model.
Default = Almgren-Chriss-lite or the common "10 bps + 0.1 × sqrt(size/ADV)"
heuristic. Calibrate against any real fills once live.

**Effort:** ~2 days code, plus a one-time PBO re-run to confirm nothing
previously-accepted flips to rejected under cost pressure.

**Priority: high.** PBO and Deflated Sharpe are theater without costs.

---

### 3.3 Walk-forward validation protocol

**Reviewer expects:** **anchored walk-forward** or **rolling walk-forward**
as a first-class protocol, not just purged CV. Every strategy/weight change
should ship with an anchored-walk-forward scorecard.

**Why not covered:** `evaluate_candidate_strategies` in
[research/validation.py:184-289](../../../src/trading/research/validation.py#L184-L289)
uses purged CV. That controls leakage but doesn't simulate the *temporal
discovery process* an out-of-sample reviewer wants to see.

**Landing zone:** extend `research/validation.py` with
`walk_forward_evaluate(strategies, anchor_date, step, windows)`.
Output consumed by the existing evidence tables.

**Effort:** ~2 days. Shares most infrastructure with purged CV.

**Priority: medium.** PBO + purged CV covers the hardest statistical sin
(cherry-picking). Walk-forward is the thing that wins arguments with
reviewers but adds less actual safety.

---

### 3.4 Factor attribution of returns

**Reviewer expects:** closed positions decomposed into market-beta,
size/value (Fama-French), momentum, sector, and *signal-specific* alpha.
Answers "did we make money from exposure or from skill?"

**Why not covered:** `PositionAttribution` at exit (already on the roadmap)
captures *signal-weight* contribution. It does not capture *factor*
contribution. These are complementary and the reviewer wants both.

**Landing zone:** new `src/trading/research/attribution.py`. Daily rolling
regression of strategy returns on factor returns (SPY, IWM-IWB size proxy,
momentum proxy, sector ETFs). Fully deterministic, no ML.

**Effort:** ~3 days. Requires a factor-returns data pipeline (cheap — Stooq
or Finnhub ETF history).

**Priority: medium.** Land after §3.1 and after the `PositionAttribution`
row exists, so both attribution types populate the same exit event.

---

### 3.5 Regime-conditioned performance scorecard

**Reviewer expects:** per-regime Sharpe, hit-rate, average-win/average-loss,
drawdown. Answers "does this system actually work in every regime it
claims to gate on, or just one?"

**Why not covered:** regime is computed per-pipeline and gates execution,
but no scorecard is published per-regime. Once the daily `RegimeLabel` row
ships (already listed on the roadmap as a 2-day gap), this becomes cheap.

**Landing zone:** reporter / dashboard addition. Pure SQL aggregation on
`(Position, RegimeLabel)` once the label row exists.

**Effort:** ~1 day *after* the RegimeLabel row ships.

**Priority: medium.** Depends on the already-planned RegimeLabel row.

---

### 3.6 Monte Carlo on equity curve

**Reviewer expects:** bootstrap the sequence of realized trade returns N=10k
times to publish confidence intervals on CAGR, max drawdown, Calmar, and
ruin probability. Standard hedge-fund-grade report item.

**Why not covered:** distinct from ABIDES (which is microstructure
per-trade). This is portfolio-level, post-hoc, deterministic.

**Landing zone:** new function in `research/risk.py` (created in §3.1).
Consumes the closed-position table.

**Effort:** ~1 day.

**Priority: medium.** Pairs naturally with §3.1; add in the same panel.

---

### 3.7 Higher-moment reporting surfacing

**Reviewer expects:** skewness and kurtosis of trade-return and daily-P&L
distributions, surfaced on the reporter / dashboard alongside Sharpe.

**Why not covered:** `_compute_skewness` / `_compute_kurtosis` already exist
in [research/metrics.py:32-59](../../../src/trading/research/metrics.py#L32-L59)
but are only used inside Deflated Sharpe. They are never surfaced.

**Landing zone:** reporter enhancement. No new code — just call sites.

**Effort:** half a day.

**Priority: quick win.** Cheap credibility lift; bundle with §3.1.

---

## 4. What is still out of scope on principle

These are methods a reviewer might ask for that should be declined because
they conflict with the PRD-v2 principles, not because of effort:

| Method | Why declined |
|---|---|
| Leverage, shorting, options, futures strategies | PRD-v2 §6.1 — US equities, long-only implicit; expansion is market-pack, not instrument-class |
| Intraday / HFT signals | PRD-v2 §4 implies daily cadence; sub-daily changes the whole control loop |
| Multi-asset optimizer (fixed income, FX, crypto) | PRD-v2 principle 8 — expansion is architectural, not ad hoc |
| Full Black-Litterman with subjective views | BL wants operator *views* as input; that conflicts with the "quiet by default" principle. Risk-parity or min-variance is the honest local-first choice |
| Fama-MacBeth cross-sectional regression framework | Overkill for single-user S&P 500 scope; revisit if multi-universe ships |

---

## 5. Suggested ordering

Respects the Sprint 1 lock (Gemma narration + ABIDES distribution) in
[integration-map.md §11](../../future/integration-map.md#11-first-sprint--locked-scope).

```
Sprint 1 (locked):
  Gemma narration MVP + ABIDES distribution MVP

Sprint 1.5 (cheap additions, 1 week, fits between sprints):
  §3.1 Portfolio-level risk metrics panel    (3d)
  §3.7 Higher-moment surfacing               (0.5d — bundled)
  §3.6 Monte Carlo equity curve              (1d — bundled)
  Dashboard panel: "Risk" tab                (1d wiring)
  → Outcome: reviewer sees VaR / CVaR / Sortino / Calmar / Ulcer /
    skew / kurtosis / MC-MaxDD CI on day one of inspection.

Sprint 2 (alongside planned Group B4 PM rewrite):
  §3.2 Cost model in research backtests      (2d + 1d PBO re-run)
  → Outcome: all future evidence tables and PBO runs are net of costs.

Sprint 3 (after RegimeLabel row ships, already planned):
  §3.5 Regime-conditioned performance scorecard   (1d)

Sprint 4 (after PositionAttribution row ships, already planned):
  §3.4 Factor attribution                    (3d)
  §3.3 Walk-forward validation protocol      (2d)
  → Outcome: every strategy change ships with anchored-WF +
    factor-decomposed evidence.
```

Total net-new engineering to reach "serious business analyst" bar, on top
of what's already roadmapped: **~13 engineering days** plus ~2 days of
dashboard/reporter wiring. Fits inside Phase B without displacing anything.

---

## 6. One-line answer to the user's question

Today: foundation is serious, surface is not. The numerics are there;
they're just hidden in internal helpers or never joined to the outcome
tables. Ship §3.1 + §3.7 + §3.6 (≈5 days) and the same codebase presents
as serious business analysis to an outside reviewer — *before* the
distribution or causal work even lands.
