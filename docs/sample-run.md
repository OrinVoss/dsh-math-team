# Sample End-to-End Run Record

> Validation proof: a **full end-to-end run** on the real **2023 CUMCM Problem C — "Automatic Pricing & Restocking of Vegetable Items"**, exercising the whole pipeline: modeling+coding role → paper role → Git handoff → independent review.
>
> - Collaboration repo: `math-team/` (Gitee)
> - Split: member-a (modeling+coding) delivered Q1–Q4; member-c (paper) wrote/reviewed with vision QA
> - All data is real from the problem's attachments; every number in the paper traces back to `results/` and the figures

## 1. Problem & data

- **Problem**: 2023 CUMCM Problem C (vegetable pricing & restocking), 4 sub-problems
- **Data size**:
  - Attachment 1: 251 items / 6 categories
  - Attachment 2: **878,503 rows** of sales flow (2020-07-01 ~ 2023-06-30, includes returns and discount flag)
  - Attachment 3: 55,982 rows of wholesale price
  - Attachment 4: loss rates (6 sub-categories + 251 items)

## 2. Collaboration chain (A → C)

```
member-a (modeling+coding)
  ├─ 题目分析报告.md      ← read problem, split sub-problems, modeling constraints
  ├─ 术语表格.md
  ├─ 问题1~4 scripts       ← actually run
  ├─ results/             ← distribution/relationship/price-volume/restock plan/sensitivity CSV + reproducibility manifest.json
  └─ figures/             ← raw/process/result, covering Q1–Q4
        │  git add member-a && push
        ▼
member-c (paper) git pull
  ├─ W1 evidence outline
  ├─ 论文.tex + 论文.pdf   ← XeLaTeX (TinyTeX)
  ├─ 代码/                ← appendix B core code (read-only copy from member-a)
  ├─ 评审记录.md           ← W1/W2/independent review/multiple fix iterations
  └─ ai use disclosure
```

Throughout, each committed only their own `member-*` folder — no interference; the paper's evidence all comes from member-a's real deliverables.

## 3. Member A (modeling+coding) results

### Problem 1 — distribution & relationships
- **Long-tail concentration**: Top5 items = 25%, Top25 = 64%, Top50 = 84% of volume
- Daily-item sales right-skewed (mean ≈10.1 kg / median 5.2 kg); log-normal AIC beats gamma (304,372.5 < 660,894.3)
- **Day-of-week factor**: Fri 18.2%, Sat 17.6% ≫ weekdays 12.4%–12.8%
- Seasonal: peaks in Jul–Sep (summer) and Jan (CNY)
- Category correlation: mostly weak–moderate positive; **eggplant is relatively independent** (Pearson 0.07–0.31)
- Discounts identify price-sensitive samples (5.4% discounted, ~7–8 off)

### Problem 2 — category price-volume + next-week restock/pricing
- Constant-elasticity demand function (price elasticity + day-of-week/month/holiday factors), 2SLS correction
- Elasticity: foliage -0.364, chili -0.647
- Next week (Jul 1–7) per-category daily restock volume + mark-up pricing strategy
- **Roll backtest profit improvement +56.2%** (8289.98 vs 5589.42)

### Problem 3 — single-item restocking (27–33 items)
- Selected **33** of 49 sellable items, each ≥2.5 kg
- Selection criterion = **profit potential per unit of display space** (space-constraint driven)
- Demand-satisfaction lower-bound sensitivity scan + satisfaction-revenue trade-off
- Jul 1 single-day profit optimization

### Problem 4 — data collection recommendations
Proposed 7 types of data (next-day actual purchase price, true demand, promo/display data, dynamic loss, weather/traffic, return reasons, customer profiles) with rationale, based on gaps actually encountered during modeling.

## 4. Member C (paper) results

- **Paper.pdf / Paper.tex**: XeLaTeX compiles, body + appendix 33 pages (appendix B core code ~6 pages)
- **18 formal figures**: 6 each for Q1/Q2/Q3 (raw/process/result); Q4 presented as a table
- **Numbering continuity audit**: Fig 1–18, Table 1–12, Eq 1–10, Listing 1–5 all continuous; cite ↔ bibliography 6↔6, no dangling references
- **W1 evidence outline / W2 paper final-check**: passed

### Independent review & multiple fix rounds (bounded iteration + vision sub-agent)
1. **First review PASS** (all low)
2. **Enhancement round + re-review FAIL**: caught and **deleted a fabricated number "0.78"** (replaced with honest interval (0.7,0.8)); fixed self-contradictory elasticity tiers and misattributed improvements; re-review PASS
3. **Code-appendix round**: caught two reproducibility defects (return-signature mismatch, undefined `rho`); re-review PASS
4. **Numbering continuity**: found and fixed an appendix table missing `\label` that caused a table-number jump 10→12
5. **Figure round**: vision sub-agent flagged Figure 2 as visually misleading (a clipped histogram masked the "log-normal beats gamma" conclusion); redrawn as dual panels and re-validated PASS

> Note: the reviewing main model itself cannot read images (`deepseek-v4-flash` has no image input), so **visual QA of all 18 figures was performed by the `opencode-go/mimo-v2.5` vision sub-agent**, and this was explicitly disclosed in the paper.

## 5. What this plugin pack contributed

| Capability | Where it showed up |
|---|---|
| 3-stage workflow & gates (M1/P1/P2, W1/W2) | member-a modeling/coding delivery, member-c writing/final-check |
| 3-folder collaboration (member-a/b/c, no interference) | A delivered → C pulled and wrote; conflict-free |
| Vision sub-agent (mimo-v2.5 visual review) | visual QA of 18 figures; caught & fixed the Figure 2 visual misdirection |
| Bounded iteration + independent review gate | blocked fabricated 0.78; fixed numbering jump and visual misdirection |
| Reproducibility manifest | `results/复现清单.json`, results traceable |
| Git collaboration + proxy (sslBackend=openssl) | clone/pull/push all the way |

## 6. Artifact index

- Analysis/build: `member-a/问题1~4_求解.py`, `member-a/results/*.csv`, `member-a/figures/*`
- Paper: `member-c/论文.pdf`, `member-c/论文.tex`, `member-c/代码/`
- QA: `member-c/评审记录.md`, `member-c/W1 证据大纲.md`, `member-c/ai使用声明.md`

> Note: member-b's earlier Q3 delivery was superseded by member-a's full Q1–Q4; this paper's evidence relies on member-a's deliverables, as honestly documented in the review record — no fabricated changes to others' contributions.
