# DSH Math Modeling Team Plugin Pack

Team-based math modeling workflow plugins for **DeepSeek Harness**. It distills the methodologies of mature math-modeling skill repos into **2 installable agent presets**, paired with a **multi-folder Git collaboration** model (Gitee/GitHub), so multiple people can work independently in their own workspaces without interference.

Hosted under the GitHub Topic: **`dsh-plugin`**.

> 简体中文说明见 [README.md](README.md) | English docs below.

## What this is

In DeepSeek Harness, an **agent preset** is a role configuration: a persona (job responsibility), a set of tools, and **Skills** (role capability documents) installed with the preset. Each session that picks a preset gains that role's full capability set.

This pack provides **2 role presets**:

| Preset dir | Role | Who | Core capabilities |
|---|---|---|---|
| `presets/model-code` | Modeling + Programming Agent | 2 modeling/coding members (shared) | Problem analysis, model building, Python/MATLAB solving, results & figures, reproducibility manifest; includes modeler/coder/algorithm/viz docs |
| `presets/paper` | Paper Agent | 1 paper-writing member | Paper writing (Word/LaTeX), evidence retrieval & verification, independent review gate; includes paper-writer/award-review/evidence-search docs |

### Each preset contains
- `agent.cordis.yml` — Harness capability baseline (derived from the shipped `cordis` preset: shell / fs / jobs / subagent collaboration / web search / skill loading, etc.)
- `preset.yml` — preset metadata (name, description)
- `skills/<name>/SKILL.md` — the role's primary skill (responsibilities, workflow, quality gates, collaboration rules)
- `skills/<name>/references/` — methodology docs installed with the preset (loaded on demand)

### Key features
- **Team collaboration**: preset embeds a "3-folder Git repo" protocol (`member-a/`, `member-b/`, `member-c/`) — each member commits only their own folder, no interference
- **Quality gates**: Modeling final-check M1 / minimal runnable P1 / **robustness attack final-check M2** / coding final-check P2 / evidence outline W1 / paper final-check W2
- **M2 robustness attack final-check**: systematically "attack" every core model — propose model → attack model → re-verify with an alternative method → add uncertainty → out-of-sample test → state the applicability boundary — to keep conclusions that cannot survive scrutiny out of the paper (with real 2023 CUMCM-C attack cases)
- **Vision sub-agent**: when the main model does not accept image input, dispatch a sub-agent on a **vision-capable model in the current environment** via `workflow` (auto-probe models whose `inputModalities` includes `image`; `opencode-go/mimo-v2.5` was validated on this host, but model names are not hardcoded)
- **Independent-model review (adversarial)**: adversarial critique by a model from a **different vendor** — factuality / consistency / completeness / **model attack** / citation check; fabricated numbers are blocked on the spot (recommended: `kimi-coding/k3-256k` on this host)

## Independent review model (adversarial)

**Why**: a model that both produces and accepts has no critical distance — fabricated numbers, inconsistent definitions, and contradictions go unnoticed. Reviewing from a **different vendor's model** is like a second pair of eyes.

**How**: dispatch a review sub-agent via `workflow`'s `agent(prompt, { provider, model })`, pinned to a model different from the producer (recommended `kimi-coding/k3-256k` on this host; do not hardcode — probe with the `llm` service for an available different-vendor model on another deployment).

**Review dimensions**:
- **Factuality**: can the headline numbers be traced to `results/` and the figures? Any fabrication?
- **Consistency**: are definitions/symbols/conclusions coherent across summary, body, tables, and figures?
- **Completeness**: do all sub-problems get covered?
- **Model attack**: question each core model's assumptions (instrument validity / key parameter values / baseline dependence / stockout truncation / share stability) and verify the stated applicability boundary
- **Citation check**: do references exist and are they cited correctly?

**Blocked instance (2023 CUMCM-C run)**: a fabricated number "0.78" in a draft was flagged (not present in the data) → removed, replaced with the honest interval (0.7, 0.8).

**Relation to M2**: M2 (modeling role) attacks the models at production time; independent review (paper role) re-checks the paper with a different model at delivery time — two lines of defense, front and back.

## Reusable global skill

The repo ships a directory installable as a **global skill** (drop it under a DSH shared user skill root; any preset discovers it):

- `skills/vision-subagent/` — vision sub-agent (visual QA). Install:
  ```bash
  # Copy to the DSH shared user skill root; any preset session auto-discovers it
  cp -R skills/vision-subagent ~/.agents/skills/vision-subagent
  # Windows:
  # Copy-Item -Recurse .\skills\vision-subagent "$env:USERPROFILE\.agents\skills\vision-subagent"
  ```
  DSH's `dsh-skill-filesystem` scans `~/.agents/skills/`, `~/.dsh/skills/`, project `.dsh/skills`, etc.; once placed, it is discovered automatically — no config change needed.

## Installation

### Prerequisites
- DeepSeek Harness (dsh) installed
- Quit dsh, or restart the session after install for changes to take effect

### Method 1: copy the folders (recommended)
Copy `presets/` into your user preset root:
```powershell
# Windows
Copy-Item -Recurse .\presets\model-code "$env:USERPROFILE\.dsh\.agent-presets\model-code"
Copy-Item -Recurse .\presets\paper "$env:USERPROFILE\.dsh\.agent-presets\paper"
```
```bash
# macOS / Linux: copy into $HOME/.dsh/.agent-presets/
mkdir -p "$HOME/.dsh/.agent-presets"
cp -R presets/model-code presets/paper "$HOME/.dsh/.agent-presets/"
```

### Method 2: manual copy
Place the `presets/model-code` and `presets/paper` folders verbatim into `~/.dsh/.agent-presets/`, keeping the directory names unchanged.

### Verify installation
Restart dsh and open a new session: the preset picker should list **`建模编程 Agent`** (Modeling-Coding Agent) and **`论文 Agent`** (Paper Agent). Validate via the `agentPresets` service:
```js
await agentPresets.standingKeyFor('model-code')  // no throw = success
await agentPresets.standingKeyFor('paper')
```

## Quick start (team collaboration mode)

1. Create an empty private repo on Gitee/GitHub (shared by the team)
2. On first clone, initialize the `member-a/`, `member-b/`, `member-c/` three-folder baseline per `docs/team-collaboration.md`
3. 2 members open `model-code` preset sessions in separate workspaces, each cloning the repo and committing their own modeling+coding deliverables to their `member-*` folder, then push
4. The paper member opens a `paper` preset session, `git pull`s A & B's deliverables, writes the paper in `member-c/`, and pushes
5. Everyone commits only their own `member-*` folder — no interference

Per-role kickoff prompt templates: see `docs/team-collaboration.md`.

## Documentation

- [Vision sub-agent](docs/vision-subagent.md) — vision review when the main model cannot read images
- [Team collaboration](docs/team-collaboration.md) — 3-folder collaboration protocol, handoff contract, per-role prompts
- [Attribution](docs/attribution.md) — methodology provenance from the two reference repos
- [Sample run record](docs/sample-run.md) — a full end-to-end run on the real 2023 CUMCM Problem C

## Sample showcase

Result of a full end-to-end run on the real **2023 CUMCM Problem C (Vegetable Pricing & Restocking)** — see [sample run](docs/sample-run.md) for the full pipeline and data:

- [Sample paper `examples/sample-paper.pdf`](examples/sample-paper.pdf) — 33-page final paper (XeLaTeX, 18 figures)
- `examples/figures/` — 15 result figures covering **raw / process / result** stages and all of Q1–Q3:

**Q1 Sales distribution & relationships**

![Q1 sales concentration](examples/figures/Q1_单品销量集中度.png)

![Q1 category correlation heatmap](examples/figures/Q1_品类相关热力图.png)

| | |
|---|---|
| ![Q1 seasonal factor](examples/figures/Q1_季节因子.png) | ![Q1 day-of-week factor](examples/figures/Q1_周内因子.png) |
| **Seasonal factor** (summer/CNY peaks) | **Day-of-week factor** (weekend peak) |

| | |
|---|---|
| ![Q1 clustering dendrogram](examples/figures/process_Q1_品类聚类树状图.png) | ![Q1 raw daily sales](examples/figures/raw_Q1_日销量时序.png) |
| **Category clustering** | **Raw daily sales series** |

**Q2 Category price-volume & restocking/pricing**

![Q2 backtest comparison](examples/figures/Q2_回测收益对比.png)

| | |
|---|---|
| ![Q2 price elasticity](examples/figures/Q2_量价弹性.png) | ![Q2 category pricing markup](examples/figures/Q2_品类定价加成.png) |
| **Price elasticity** | **Category mark-up pricing** |

**Q3 Single-item restocking & pricing**

| | |
|---|---|
| ![Q3 restock volume](examples/figures/Q3_单品补货量.png) | ![Q3 item profit](examples/figures/Q3_单品收益.png) |
| **Selected-item restock volume** | **Item profit** |

| | |
|---|---|
| ![Q3 item pricing](examples/figures/Q3_单品定价.png) | ![Q3 sensitivity](examples/figures/process_Q3_灵敏度分析.png) |
| **Item pricing** | **Satisfaction-revenue sensitivity** |

## Methodology attribution

The role methodology docs in this pack are distilled from (docs only; no scripts/tool sources are shipped):

- [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) — 3-stage workflow (modeling/coding/paper), quality gates, algorithm library, scientific-viz spec, reproducibility manifest
- [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) — award-grade review gates (blind judging / bounded iteration), evidence search, full workflow methodology

## License

MIT (most permissive; attribution required)
