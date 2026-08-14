# Team Collaboration

A 3-person collaboration model: **3 independent workspaces + 3 independent folders + collaboration through one Git repo**, without interference.

## Core rules (everyone abides)

1. **Commit only your own `member-*` folder** — use `git add member-a` (or member-b / member-c), **never `git add .`**
2. `git pull` before you start every work session, to avoid a stale base
3. If you hit `schannel ... SEC_E_NO_CREDENTIALS (0x8009030e)`, first run:
   ```bash
   git config http.sslBackend openssl
   ```
   Add a proxy if needed: `git config http.proxy http://127.0.0.1:10808`
4. `git pull` only reads others' folders — never overwrite them

## Repository layout

```
<repo>/
├── member-a/    # modeling+coding member A
├── member-b/    # modeling+coding member B
└── member-c/    # paper member C
```

## Initialization (first member, once, when the repo is empty)

```bash
git clone <git-repo-url>
cd <repo>
mkdir -p member-a member-b member-c
printf 'Modeling/coding member A\n' > member-a/README.md
printf 'Modeling/coding member B\n' > member-b/README.md
printf 'Paper member C\n'           > member-c/README.md
git add member-a member-b member-c
git commit -m "init: team 3-folder baseline"
git branch -M main && git push -u origin main
```

## Deliverable contract

- **Modeling+coding role**: `题目分析报告.md` (problem analysis report), `术语表格.md` (term table), solution scripts (.py/.m), `results/` (result tables + reproducibility manifest.json), `figures/` (raw/process/result figures covering all sub-problems)
- **Paper role**: `W1 证据大纲.md` (W1 evidence outline), final paper (`完整论文.docx|.md|.pdf`), `评审记录.md` (review record), and an `ai使用声明.md` (AI-use disclosure) when required

## Quality gates

- Modeling+coding: `M1 modeling final-check → P1 minimal runnable → P2 coding final-check → reproducibility verification`
- Paper: `W1 evidence outline → evidence-search verification → W2 paper final-check`
- Keep an independent review gate (severity blocker/high/medium/low + bounded-iteration budget)

## Per-role kickoff prompts

### Member A / B — modeling+coding (pick the `model-code` preset)
```
Use the math-model-code skill and perform team Git collaboration:
1. Repo URL = <git-repo-url> (if schannel errors, first: git config http.sslBackend openssl)
2. git clone into my independent workspace
3. In member-a/ (or member-b/), solve the problem: 【paste problem】
4. Produce 题目分析报告.md, 术语表格.md, solution scripts, results/, figures/; git add only my member folder
5. After passing M1→P1→P2, push to main
```

### Member C — paper (pick the `paper` preset)
```
Use the math-paper skill and perform team Git collaboration:
1. Repo URL = <git-repo-url> (if schannel errors, first: git config http.sslBackend openssl)
2. git clone into my independent workspace, git pull
3. Read member-a/ and member-b/ deliverables
4. Write W1 evidence outline → final paper → review record; git add only my member-c folder
5. After passing W1→W2, push to main
```

## Example task split (a contest with 4 sub-problems)

- **Member A**: Problem 1 + Problem 2 (distribution/relationship analysis, category pricing-sales modeling & weekly restocking optimization)
- **Member B**: Problem 3 + Problem 4 (single-item restocking combinatorial optimization, data-collection recommendations)
- **Member C**: integrate A & B conclusions into the final paper

Data can live on a shared path (accessible to all sessions on the same machine) or under the repo's `data/` (self-hosted; avoid large-binary constraints).
