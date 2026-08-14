---
name: mathodology-award-gates
description: Use when running Mathodology award-workflow phase gates, judge panels, structured handoffs, figure QA, or rendered-PDF QA in a contest run.
---

# Mathodology Award Gates

Canonical home for the runtime contracts of the Mathodology award workflow: the
structured run blocks, the severity ladder, the judge-panel aggregation rule,
the iteration budgets, the run layout, the blind seat protocol, and the QA
scripts. Agents and workflows point here instead of redefining these formats.

Role-specific extra keys (e.g. a coder's deviations note) live in the agent
definitions; this skill owns the shared schema every role must satisfy.

## 1. Structured Run Blocks

Every specialist ends with a `handoff:` block. Free-text handoffs are rejected.
The lead lints each block with `lint_run.py handoff --agent <agent-name>` (see
Scripts) -- the `--agent` flag additionally enforces that role's extra keys
(e.g. `mathodology-coder` requires `collision_gate_result`); every
`artifacts[].path` must resolve under `work/<run-id>/`.

```yaml
handoff:
  phase: 4
  agent: mathodology-coder
  loop: 0                      # 0 = first attempt; increments per gate retry
  status: complete             # complete | partial | blocked
  artifacts:
    - {path: work/<run-id>/outputs/figures/sens.pdf, role: sensitivity}
  decisions: []
  assumptions: []              # each: {id: A7, text: ..., evidence: ...|assumed, sensitivity_plan: ...}
  evidence: []
  commands: []                 # exact rerun commands
  weaknesses: []
  questions: []                # empty unless contest-critical
  critic_focus: []
```

The evidence researcher adds this role-specific contract:

```yaml
search_backend: combined          # combined | search-mcp | builtin | none
queries_run:
  - {query: "...", backend: search-mcp, category: paper, accepted: [], rejected: []}
  - {query: "...", backend: builtin, category: paper, accepted: [], rejected: []}
missing_evidence: []
citations_to_verify: []           # each: {id, claim, source, url, verified: bool}
```

`combined` requires at least one query from each backend. `search-mcp` and
`builtin` are single-source degradation modes: queries must match that backend
and `missing_evidence` must explain the missing channel and coverage. `none`
requires no queries, non-empty `missing_evidence`, and `status: blocked`.

The critic writes a `gate:` block per phase. `verdict: fail` on any unresolved
`blocker`/`high`. Lint with `lint_run.py gate`. Every issue carries a stable
`id` (`G<phase>-<n>`), reused unchanged when the finding recurs in a later loop
so the lead can mechanically detect a stalled fix.

```yaml
gate:
  phase: 4
  loop: 0
  verdict: pass                # pass | fail
  issues:
    - {id: G4-1, severity: high, summary: ..., artifact: ..., required_fix: ..., owner: mathodology-coder}
  evidence_checked: []
  missing_evidence: []
```

Each Phase-7 judge seat returns one `scorecard:` block. Weights sum to 1.0;
scores are 0-100. Lint with `lint_run.py scorecard`. `target_tier` is optional
and judge seats leave it out -- seats are blind to the target (the lead supplies
`--target` only at aggregation). `implied_tier` follows the weighted-total band
(>=85 outstanding, 80-84.9 finalist, 75-79.9 meritorious, <75 below); a seat may
place it below its own band only with a `tier_justification` field.

```yaml
scorecard:
  contest: MCM
  seat: A                      # A | B | C
  round: 1
  criteria:                    # one row per criterion; weights sum to 1.0, scores 0-100
    - {name: summary, weight: 0.25, score: 82}
    - {name: modeling, weight: 0.25, score: 80}
    - {name: results, weight: 0.20, score: 84}
    - {name: writing, weight: 0.15, score: 85}
    - {name: completeness, weight: 0.15, score: 83}
  weighted_total: 82.4
  implied_tier: finalist
  fix_one_thing: "..."
  ranked_gaps: []
  do_not_regress: []
```

When a budget is exhausted the lead emits a `decision_memo:` and stops for a
human decision (never silently continues). Lint with `lint_run.py memo`.

```yaml
decision_memo:
  phase: 7
  budget_spent: {loops: 2, cap: 2}
  unresolved: []               # remaining issues with severity
  options:                     # 2-3 options, each {option, consequence, recommended: bool}
    - {option: ..., consequence: ..., recommended: true}
```

## 2. Severity Ladder

- `blocker`: violates contest rules, breaks prompt coverage, invalidates the model, prevents reproduction, or makes submission unsafe.
- `high`: likely to lower award level unless fixed, including sparse result presentation or visible figure/table rendering defects in a paper-first contest.
- `medium`: should be fixed or explicitly accepted with rationale.
- `low`: polish or minor clarity issue that does not affect correctness, scoring, reproducibility, or submission validity.

No `blocker` or `high` may remain before advancing a phase. `medium` needs an
owner, a fix plan, or an explicit, rationale-backed risk acceptance.

## 3. Judge Aggregation And Thresholds

Run the panel with `lint_run.py aggregate <scorecard files> --target <tier>`.
The panel PASSES only when all of:

- (a) every seat's `implied_tier` is at or above the target tier;
- (b) the minimum seat `weighted_total` clears the target's total threshold;
- (c) no single criterion, in any seat, falls below the target's floor.

Two seats differing by more than 20 on one criterion is an **evidence conflict**:
it is surfaced and adjudicated by the lead, never averaged away, and blocks a
clean pass until resolved. **Adjudication procedure**: the lead examines the two
seats' cited artifact evidence, re-dispatches ONLY the outlier seat once with the
specific evidence question, and counts it as one re-score round; the outcome is
recorded in the decision_memo.

| Target tier | Total >= | Criterion floor >= |
|---|---|---|
| Outstanding / 国一 | 85 | 70 |
| Finalist / 国一边缘 | 80 | 65 |
| Meritorious / 国二 | 75 | 60 |

`--target` accepts the canonical tokens (`outstanding|finalist|meritorious`) and
documented aliases including `国一`, `国二`, `国一边缘`, `一等奖`, `二等奖`; judge
seats use the same tokens in `implied_tier`.

Calibrate against real rarity: Outstanding is roughly the top 1-2%, 国一 roughly
the top 5-8%. Do not inflate scores to force a pass.

This table -- and everything else in this skill -- is **lead/critic context
only**. Per-criterion band anchors are defined in
`.claude/agents/mathodology-award-judge.md`, deliberately not here: judge seats
must never see the pass thresholds above, or scores cluster at the bar.

## 4. Iteration Budgets

- Each per-phase critic gate: at most 2 fix loops (3 evaluations total).
- Phase 7: at most 2 re-score rounds. These do not count against the whole-run
  cap: the initial panel is round 1, the two permitted re-scores are rounds 2
  and 3 (max r = 3).
- Whole run: capped at 8 fix loops across all phases.
- Stop early when a loop fails to improve. Improvement metric: a gate fix loop
  improves iff the count of open blocker+high issues strictly decreases (match
  findings by their stable `id`); a Phase 7 re-score improves iff the minimum
  seat weighted_total strictly increases.
- On exhaustion of any budget: emit a `decision_memo:` and stop for a human.

## 5. Run Layout

Every run writes under a single gitignored `work/<run-id>/` tree; every handoff
artifact path resolves inside it:

```text
work/<run-id>/
  phase-logs/
  gates/                       # gates/phase-<n>-loop-<k>.yaml
  scorecards/                  # scorecards/phase7-seat-<A|B|C>-round-<r>.yaml
  evidence/
  code/                        # the coder's code and run_all.py
  outputs/
    figures/
    tables/
    data/
  paper/
  package/                     # incl. manifest.md, compiled by the lead at Phase 6 close
```

## 6. Blind Judge Panel

Phase 7 dispatches three parallel `mathodology-award-judge` seats in a single
message with no shared context. Each seat receives ONLY its seat brief, the
rendered PDF, and `work/<run-id>/package/manifest.md` (the artifact manifest the
lead compiles at Phase 6 close: rendered PDF path plus figures, tables, data,
and code paths) -- no phase log, no other seat's scorecard, no cross-seat
contact, and **no target tier or thresholds** -- so the three scorecards are
independent and un-anchored.

**Canonical seat rubrics** (the lead builds seat briefs from these; all seats
share `summary`, `modeling`, `results` so cross-seat conflict detection has
overlap -- `summary` is the MCM summary sheet / CUMCM 摘要 quality):

| Seat | Role | Criteria (weight) |
|---|---|---|
| A | contest flagship-tier general judge | summary .25, modeling .25, results .20, writing .15, completeness .15 |
| B | innovation & decision-usefulness | summary .15, modeling .20, results .15, innovation .30, evidence .20 |
| C | skeptical applied-math referee | correctness .35, reproducibility .25, summary .10, modeling .15, results .15 |

Each seat scores its criteria 0-100 against the band anchors in the judge agent
brief, produces a weighted total, maps it to the implied tier by band, and names
the single most award-limiting weakness ("if you fix only one thing"). The lead
lints and aggregates the three scorecards per Section 3.

## 7. Scripts

All four scripts ship with this skill and self-test with `--self-test`.
**Execute the shipped scripts -- do not reimplement their logic inline.** From a
cloned repo use the repo-relative path; from a global skill install the same
files live under `scripts/` in this skill's directory.

- `figqa.py` (matplotlib) -- bbox-collision gate. **Import-only by design**: the
  CLI runs only `--self-test` (proving the gate works); it cannot inspect saved
  figure files. Wire `assert_no_overlap(fig)`
  (`from figqa import assert_no_overlap`) into the figure factory and `run_all`
  so any text/annotation/legend overlap with data artists, or any clipped
  artist, **fails the run**. A zero-collision pass is therefore evidenced by
  re-running `run_all.py` and observing exit 0 -- the critic re-runs it
  independently rather than trusting the coder's `collision_gate_result` key.
  The coder copies `figqa.py` into `work/<run-id>/code/` so the submission
  package is self-contained and reruns the gate without the skill installed.
- `pdf_qa.sh` (poppler-utils: pdfinfo/pdftoppm/pdftotext) -- rendered-PDF QA:
  page-count, duplicate caption prefixes (`Figure N:`/`Table N:`/`Fig. N`/
  `图 N`/`表 N`), anonymity (`--anonymous`: metadata identity including CJK
  names in Author/Creator/Producer, plus a page-1 body-text scan -- emails,
  author lines, and 姓名/指导教师-style labels FAIL, while ambiguous shapes (an
  English institution pattern, a bare 学校/学院) WARN for review since the
  problem itself may be about schools; a bare control number is expected and
  not flagged), and a blank-page heuristic, run
  against the **compiled PDF**.
- `make_contact_sheet.py` (poppler-utils + matplotlib) -- builds the chart-QA
  contact sheet FROM the compiled PDF via pdftoppm, never from source images.
  The coder's Phase-4 draft sheet from source renders is coverage QA only; the
  authoritative sheet is regenerated from the compiled PDF at Phase 6+.
- `lint_run.py` (PyYAML) -- validates the Section 1 blocks (`handoff --agent
  <name>` also enforces role-specific keys) and runs the Section 3 judge
  aggregation.

Repo-relative invocations:

```bash
python3 .claude/skills/mathodology-award-gates/scripts/figqa.py --self-test
python3 .claude/skills/mathodology-award-gates/scripts/lint_run.py handoff work/<run-id>/phase-logs/phase4.md --agent mathodology-coder
python3 .claude/skills/mathodology-award-gates/scripts/lint_run.py aggregate work/<run-id>/scorecards/phase7-seat-*-round-1.yaml --target outstanding
bash    .claude/skills/mathodology-award-gates/scripts/pdf_qa.sh work/<run-id>/paper/solution.pdf --max-pages 25 --anonymous
python3 .claude/skills/mathodology-award-gates/scripts/make_contact_sheet.py work/<run-id>/paper/solution.pdf -o work/<run-id>/outputs/figures/contact_sheet.png
```

Aggregate one round at a time (the round-suffixed glob): after a re-score, round
2's files are `phase7-seat-*-round-2.yaml` -- a bare `phase7-seat-*.yaml` glob
would mix rounds and be rejected as duplicate seats. `--max-pages 25` is the
current MCM rule; set it from the `variant:` block's `limits.pages` for other
contests, and note the MCM AI-use report is excluded from the 25-page count
(`--max-pages` applies to the solution body).

Skill-relative wording (global install): run `scripts/figqa.py`,
`scripts/pdf_qa.sh`, `scripts/make_contact_sheet.py`, and `scripts/lint_run.py`
from this skill's directory. Prerequisites: matplotlib (figqa, contact sheet),
poppler-utils (pdf_qa, contact sheet), PyYAML (lint_run); each script prints an
actionable message when a prerequisite is missing.
