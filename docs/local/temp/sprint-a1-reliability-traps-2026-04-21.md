# Sprint A1 — Close the remaining reliability traps

> **Audience:** an autonomous coding agent (or human engineer) picking this
> up cold. This document is self-contained. You should not need to ask
> questions before starting; if you do, that's a defect in the plan —
> record it at the bottom under §9 and answer it conservatively.
>
> **Target branch:** create a new feature branch from `main` named
> `feat/a1-reliability-traps`.
>
> **Precondition:** `main` must be clean (CI run 24715710993 green) and
> tagged past v0.8.0 before starting. See STATE.md.
>
> **Estimated size:** one focused sprint, ~3–5 work days, ~800–1200 LOC
> including tests. No schema changes expected. No new dependencies.

---

## 1. Mission

Close the remaining silent-failure traps in PRD-v2 §10 Phase A so
Workstream 1 can advance from Level 3 to Level 4:

1. **FinBERT retry / recovery** — break out of sticky fallback mode; a
   transient inference or load failure must not permanently pin the
   system to the heuristic sentiment path.
2. **Dependency degradation → incident rule** — every transition of a
   data provider (Stooq / Yahoo / Finnhub / Edgar / FinBERT) into a
   "degraded" state opens or appends to a durable `Incident` with a
   stable dependency tag. An operator must be able to reconstruct the
   timeline from the incident stream alone, without reading logs.
3. **Sweep silent `_logger.warning(` calls on fallback paths** across
   monitor / analyst / scanner and convert to structured `issue_code`
   evidence paired with `record_agent_event`.

This is hardening of existing code, not new surface area. Conform to
existing patterns.

## 2. Why this matters (so you can make judgement calls)

The product is a single-user, self-managed trading system built on the
principle **"fails loudly when trust would otherwise be damaged"** (PRD-v2
§3 Principle 4). A silent fallback is the single most trust-damaging
behavior possible: the system keeps producing outputs, but the outputs
are lower-fidelity, and the operator has no signal to distrust them.

### 2.1 Architectural principle (owner decision, 2026-04-21)

**Quiet user-facing, LOUD inward-facing.** The eventual end-user of this
product is non-technical and cannot act on a raw error. Therefore:

- **Internally** (incident stream, structured events, audit logs, trade
  provenance): maximum fidelity. Record every degradation, every
  recovery, every fallback path. This surface is consumed by the
  operator, the support distributor, and a future supervisor agent
  (moonshots.md #6) — not by the end-user.
- **User-facing**: a dashboard badge while incidents are open, and a
  `[Send to support]` button that forwards a pre-formatted bundle to a
  configured distributor address. The button and email are Stage A5
  scope, not A1. A1's job is to produce an incident stream rich enough
  to populate those bundles.
- **No push notifications, no alerts, no email from A1.** Escalation is
  pull-model: the user clicks, or the supervisor agent pulls. Never a
  notification that assumes the recipient can interpret it.

This principle is what makes the A1 acceptance criteria stricter than
they might otherwise seem: we are not just "logging better," we are
producing the substrate for automated recovery and support escalation.

Specifically:

- A FinBERT model that fails to load once should not lock the system
  into heuristic sentiment for the rest of the process's lifetime.
- A Stooq outage that shifts the provider chain to Yahoo should produce
  an *incident record*, not a log line that nobody reads.
- Code paths that swallow a failure with `logger.warning("...")` and move
  on violate the principle at the smallest scale.

If a design decision is ambiguous, prefer the option that makes the
failure more visible to the operator, even if it is noisier.

## 3. Background — what already exists

### FinBERT — [src/trading/services/finbert.py](../../src/trading/services/finbert.py)

Already has partial infrastructure you will extend, not replace:

- `_load_model()` at [line 90](../../src/trading/services/finbert.py#L90) — lazy-loads the transformer pipeline; returns `None` on failure.
- `_record_load_failure()` at [line 48](../../src/trading/services/finbert.py#L48) and `_load_retry_backoff_seconds()` at [line 32](../../src/trading/services/finbert.py#L32) — exponential-backoff retry on model load. This is good and should keep working. **Your job is to make sure it actually gets re-entered after a failure window, not bypassed.**
- `_note_degradation()` at [line 57](../../src/trading/services/finbert.py#L57) and `_clear_degradation()` at [line 79](../../src/trading/services/finbert.py#L79) — already call the observability dependency helpers. Extend these semantics; do not replace them with a parallel mechanism.
- `analyze_text()` at [line 151](../../src/trading/services/finbert.py#L151) and `analyze_batch()` at [line 186](../../src/trading/services/finbert.py#L186) — the two public entry points. Both call `_load_model()` and fall back to `_headline_heuristic()` on any exception. The fallback is correct; the observability around it is not.

The "sticky zero-vector" phrase in the completion plan refers to the
degenerate state where `_load_model()` has failed enough times that the
backoff window keeps returning `None`, and every subsequent call silently
uses the heuristic without emitting further evidence. Your acceptance test
must prove the system can *recover* from this state within the same
process.

### Provider chain

Source files:
- [src/trading/services/stooq.py](../../src/trading/services/stooq.py) (1612 LOC)
- [src/trading/services/finnhub.py](../../src/trading/services/finnhub.py) (610 LOC)
- [src/trading/services/edgar.py](../../src/trading/services/edgar.py) (203 LOC)

Each provider already has some form of retry and fallback, and
`stooq.py`, `finnhub.py`, and `edgar.py` already call dependency
degradation helpers in several branches. What is still missing is a
*uniform first-failure incident semantic*, recovery classification, and
full coverage of the remaining silent fallback branches. Grep each for
`logger.warning(` on the fallback path and you will find the gaps.

### Incident machinery — [src/trading/observability/service.py](../../src/trading/observability/service.py)

- `Incident` model imported at line 43. Already has `pipeline_run_id`,
  `correlation_id`, serialization helpers (`_serialize_incident` at [line 305](../../src/trading/observability/service.py#L305)).
- Existing dependency helpers already exist:
  `note_dependency_degradation()` at [line 4560](../../src/trading/observability/service.py#L4560),
  `clear_dependency_degradation()` at [line 4686](../../src/trading/observability/service.py#L4686),
  plus `_open_or_update_incident()` at [line 2450](../../src/trading/observability/service.py#L2450)
  and `_resolve_incident()` at [line 2502](../../src/trading/observability/service.py#L2502).
- `record_agent_event()` — this is the call you pair with incident
  open/close to create navigable evidence. Already used in 11+ files.

Do **not** add a second parallel dependency-incident API unless the
existing helpers truly cannot express the needed semantics. Thin wrappers
around the current helpers are acceptable; duplicate lifecycle logic is
not.

### Tests

- Unit tests live in [tests/unit/](../../tests/unit/), one file per module
  (`test_finbert.py`, `test_stooq.py`, etc.).
- Integration tests that exercise the provider chain live in
  [tests/integration/](../../tests/integration/) — run against a real
  (Azure) Postgres, not a mock. See the saved `pydantic_env_leak` memory
  for the env-isolation pattern used in `conftest.py`.
- Existing relevant unit coverage already exists in
  [tests/unit/test_finbert.py](../../tests/unit/test_finbert.py),
  [tests/unit/test_stooq.py](../../tests/unit/test_stooq.py), and
  [tests/unit/test_observability.py](../../tests/unit/test_observability.py).
  Extend those before creating new test files.

## 4. Pre-flight checks (run these first)

```powershell
# 1. You're in the repo root
if (-not (Test-Path pyproject.toml)) { Write-Output "WRONG DIRECTORY" }

# 2. Main is clean, CI green, tagged past v0.8.0
git status --short  # must be empty
git log -1 --oneline origin/main
git tag --sort=-v:refname | Select-Object -First 3

# 3. Baseline: full suite currently passes
uv run pytest -q

# 4. Grep the silent-warning population you need to shrink
rg -n "_logger\.warning\(" src/trading/agents src/trading/services src/trading/dashboard src/trading/pipeline |
  Measure-Object |
  Select-Object -ExpandProperty Count
# Record this number in §9. Acceptance requires it to drop to zero on
# *fallback* paths specifically. Not every warning is a fallback.
```

## 5. Implementation work (ordered)

### 5.1 — Incident helper for dependency degradation

Start by deciding whether to evolve the existing dependency helpers in
`src/trading/observability/service.py` (`note_dependency_degradation`,
`clear_dependency_degradation`) or add thin wrappers around them. Do not
create a second parallel incident lifecycle API unless the existing
helpers truly cannot express the needed semantics. One acceptable public
shape is:

```python
def open_dependency_incident(
    dependency_tag: str,                       # e.g. "finbert", "stooq"
    summary: str,
    reason: str,
    error_class: str | None = None,
    error_message: str | None = None,
    details: dict[str, object] | None = None,
) -> Incident: ...

def close_dependency_incident(
    dependency_tag: str,
    resolution: str,
    recovery_method: str,            # NEW — see semantics below
    details: dict[str, object] | None = None,
) -> Incident | None: ...
```

Semantics:
- **Stable tag.** The same `dependency_tag` is used across process
  restarts; open + close are matched on the tag, not on a UUID.
- **Open is idempotent.** If an incident is already open for this tag,
  append a new event to it (don't open a second one).
- **Close is idempotent.** If no incident is open, no-op; do not raise.
- **No silent threshold for A1-scoped runtime fallback paths.** The
  current helper opens dependency incidents only after 3 consecutive
  unhealthy checks. That is too slow for FinBERT / Stooq / Yahoo /
  Finnhub / Edgar runtime fallback paths. For A1, incident evidence must
  exist on the first confirmed degradation transition, not after a
  hidden 2-failure window.
- **No time-based auto-close.** An incident stays open until a genuine
  recovery signal fires. If Stooq is dead overnight, the incident stays
  open overnight (owner decision: you want to wake up and see "Stooq has
  been broken for 9 hours," not an auto-closed mystery).
- **Append-only lifecycle.** Close is a transition, not a deletion. The
  incident row remains in the table after close; `closed_at`,
  `recovery_method`, and resolution details are written alongside the
  existing open-time fields. Nothing about an open incident is mutated
  destructively on close. This is the A1 expression of the PRD-v2 §6.3
  *acquisition-grade traceability* principle — a future auditor must be
  able to read every past incident in full fidelity.
- **`recovery_method` is mandatory on close.** Allowed values (extend as
  needed): `"automatic_retry"` (the next call simply succeeded),
  `"backoff_elapsed"` (backoff window expired and a new attempt
  succeeded), `"provider_recovered"` (an upstream health check
  confirmed), `"operator_manual"` (a human intervened). A future
  `"master_agent"` value is reserved for when Moonshot #6 ships. This
  field is the training signal for the future supervisor agent — if you
  cannot classify the recovery, raise, do not silently pass a
  placeholder. Store it in `Incident.detail_json` unless you discover an
  existing dedicated field; do not add a schema migration just for this.
- **Fallback operation is not recovery.** If Stooq is down and Yahoo is
  carrying the load, the Stooq incident stays *open*. Do not close it
  just because a fallback provider is working. Close only when the
  primary itself recovers, or when an operator explicitly resolves it.
  Owner decision: this preserves the truth that the primary is broken
  and prevents the system from quietly drifting onto a fallback that
  becomes permanent without anyone deciding it should.
- Every open/close emits a `record_agent_event` with kind
  `dependency_degraded` / `dependency_recovered`. If you route through
  the existing dependency helpers, extend them or wrap them so this
  event emission still happens.

### 5.2 — Wire FinBERT into incidents

In `src/trading/services/finbert.py`:

- `_note_degradation(...)` (line 57) — call
  the dependency-incident open path in addition to its current
  `DependencyCheck` write.
- `_clear_degradation(...)` (line 79) — call
  the dependency-incident close path with an explicit
  `recovery_method`.
- `_load_model()` — ensure the backoff window is respected but a successful
  load after a backoff interval *triggers* `_clear_degradation` even if
  the next `analyze_*` call is the one that observed recovery.
- In `analyze_text()` (line 151) and `analyze_batch()` (line 186):
  replace the bare `_logger.warning("FinBERT inference failed", ...)` with
  a structured incident + event. The heuristic fallback itself is fine.

### 5.3 — Wire provider chain into incidents

Apply the same pattern to each of:

- `src/trading/services/stooq.py` — tag `"stooq"`
- `src/trading/services/finnhub.py` — tag `"finnhub"`
- `src/trading/services/edgar.py` — tag `"edgar"`
- Any Yahoo fallback — tag `"yahoo"` (confirm where it lives; search for
  `yahoo` before assuming)

For each provider: every point where the code currently degrades to a
next-tier source or to a cached/synthetic value must open an incident;
every point where the primary source recovers must close it.

Audit the existing helper calls first. `stooq.py`, `finnhub.py`, and
`edgar.py` already emit degradation evidence in several branches; the
job is to close the remaining gaps and fix the incident semantics, not
to replace working hooks blindly.

### 5.4 — Degraded-provenance propagation (existing JSON-bearing records)

When *any* dependency-degradation `Incident` is open, the existing
JSON-bearing decision records written during that window carry a
`provenance` block referencing the open incident ID(s) and the degraded
`dependency_tag`(s).

Scope is deliberately wide (owner decision, 2026-04-21 — option B over
tight):

- analyst diagnostics (accepts *and* rejects) via
  `AnalystDiagnostic.provider_status_json`
- recommendations via `Recommendation.rationale_json`
- PM queue rows / approval payloads via `ApprovalQueueItem.payload_json`
- execution / observability events tied to approval, submit, or fill via
  `ExecutionEvent.detail_json`
- position-side JSON already persisted at entry when you are already
  writing it (for example `entry_signals_json` or
  `analysis_regime_policy_json`)

Rationale: the silent 95% (rejects on degraded data) is where the
retrospective question "in the last Stooq outage, how many rejects were
actually sound?" lives. Losing provenance there contradicts the
*loud-internal* principle. Storage cost per row is one boolean + one
pointer — acceptable.

- Do **not** interpret this as "add provenance columns to every table".
  Current tables such as `ScanResult`, `TransactionLog`,
  `SignalAccuracyLog`, `ExitShadowLog`, and `ExitTimingShadowLog` do not
  have an existing JSON payload column to extend. Pulling those rows into
  scope would require a schema change and is therefore out of scope for
  A1 unless explicitly escalated in §9.
- No user-facing surface in A1. This is for forensics, backtesting, and
  the future supervisor agent (moonshots.md #6).
- Implementation hint: a thin helper in observability that returns the
  set of currently-open incident tags, called at diagnostic-write time.
  Do not introduce a new table; extend the existing JSON-bearing record
  payloads.

### 5.5 — Silent-warning sweep

Grep scope: `src/trading/agents/`, `src/trading/services/`,
`src/trading/dashboard/`, `src/trading/pipeline/`.

For every `_logger.warning(` on a fallback path (i.e. one where the code
continues after the warning), either:

1. Pair it with a `record_agent_event(...)` using an `issue_code` that
   makes the fallback navigable from the dashboard, **or**
2. Confirm it is *not* a fallback (e.g. it's a warning about
   configuration being re-read) and leave it.

Warnings on `*_test.py` paths are out of scope.

The grep will also surface fallback-like warnings in files such as
`fred.py` and `sp500.py`. Even if they are not named in §1, classify
them explicitly rather than assuming they are out of scope.

## 6. Acceptance criteria (for the whole sprint)

All six must be true:

1. **FinBERT recovery test.** A pytest case that forces `_load_model()` to
   fail N times (enough to enter the sticky fallback state), then
   un-blocks the model and calls `analyze_text`. The call must succeed
   with a real label, not the heuristic; the test must assert exactly
   one `Incident` was opened and exactly one closed, both tagged
   `"finbert"`.
2. **Provider degradation reproducible from incidents alone.** A test
   fixture forces Stooq to fail, asserts the chain moves to the next
   provider, and asserts an `Incident` tagged `"stooq"` is present with
   a readable `reason`. A second step restores Stooq and asserts the
   incident is closed. The test must not read any log output to make
   these assertions.
3. **`_logger.warning(` sweep.** Grep of
   `_logger.warning(` across
   `src/trading/{agents,services,dashboard,pipeline}/` returns zero hits
  that lack paired structured operator-visible evidence on the
  fallback path (`record_agent_event` directly, or a dependency helper
  path that you have extended to emit it). Record the before/after
  count in §9.
4. **Full suite green.** `uv run pytest -q` passes locally and in CI.
   Coverage is ≥79% (saved memory: don't stress 80%).
5. **Recovery-method populated.** Every closed incident has a non-empty
   `recovery_method` drawn from the allowed vocabulary. A test forces a
   close with a missing / unknown value and asserts it raises.
6. **Degraded-provenance flows through existing JSON-bearing decision
  records.** A test forces a FinBERT incident open, triggers an analyst
  decision during that window, and asserts
  `AnalystDiagnostic.provider_status_json` carries
  `provenance.degraded_dependencies = ["finbert"]` with a pointer to
  the incident ID. If the same path writes a `Recommendation`, assert
  that `Recommendation.rationale_json` carries the same block. Second
  step: close the incident, trigger another decision, and assert the
  `provenance` field is absent or empty.

## 7. Out of scope (do NOT do these)

- Changing FinBERT's model choice or the heuristic fallback logic itself.
- Adding a new data provider. If Yahoo doesn't exist in the current
  chain, do not add it — document its absence in §9.
- UI / dashboard changes to surface incidents. A separate stage (A5 —
  Evidence surface completion) owns that. You only need to make sure the
  incidents exist and are queryable.
- Schema migrations. If you believe a schema change is required, stop
  and record the reason in §9.
- Any Gemma, narration, or command-layer work. That's Phase B.

## 8. References

- Completion plan: [`docs/local/prd-v2-completion-plan-2026-04-20.md`](prd-v2-completion-plan-2026-04-20.md) §3 Stage A1
- PRD-v2 §10: [`docs/PRD-v2.md`](../PRD-v2.md)
- Sprint workflow: [`docs/sprint-loop.md`](../sprint-loop.md)
- Observability runbook: [`docs/local/analyst-runbook.md`](analyst-runbook.md) (incident stream section)
- Prior sprint precedent (format reference only, already shipped):
  `docs/del/sprint-gemma-narration.md` on `main`

## 9. Open questions (filled in at plan time, 2026-04-21)

- **Baseline `_logger.warning(` count in scope dirs:** 38 across
  `src/trading/{agents,services,dashboard,pipeline}/` as of 2026-04-21.
  Not all 38 are fallbacks — the sweep in §5.4 must classify and convert
  only fallback-path warnings. Non-fallback warnings (e.g. configuration
  re-read) stay.
- **Final `_logger.warning(` count on fallback paths:** _TBD at acceptance
  — must be 0 per §6 criterion 3._
- **Yahoo as a live provider:** Yes, but not as a standalone service
  file. It lives inside [src/trading/services/stooq.py](../../src/trading/services/stooq.py):
  `_fetch_yahoo_single_ticker` at [line 803](../../src/trading/services/stooq.py#L803),
  `_fetch_yahoo_batch` at [line 981](../../src/trading/services/stooq.py#L981). It
  is used as a Stooq fallback / cross-check. Use dependency tag `"yahoo"`
  for incidents.
- **Existing incident helpers:** Yes. `note_dependency_degradation()` at
  [line 4560](../../src/trading/observability/service.py#L4560) and
  `clear_dependency_degradation()` at [line 4686](../../src/trading/observability/service.py#L4686)
  already persist `DependencyCheck` rows and can open / resolve
  incidents through the runtime. The current limitation is semantic:
  runtime dependency incidents open only after 3 consecutive unhealthy
  checks, and close without `recovery_method` metadata.
- **Any schema change believed necessary:** No for incident helpers or
  recovery metadata if `recovery_method` is stored in
  `Incident.detail_json`. The provenance requirement must stay scoped to
  existing JSON-bearing records unless a migration is explicitly
  approved.
