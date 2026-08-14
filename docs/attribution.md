# Methodology Attribution

The methodology docs in the two presets are distilled from two open-source math-modeling skill repos (**docs only; scripts/tool sources are NOT shipped**). After installation they load on demand with the preset.

## Source 1: XiaoMaColtAI/math-modeling-skill

A three-stage (modeling → coding → paper) workflow with quality gates.

### Into `presets/model-code`
- **Modeler**: `references/roles-建模手/` (SKILL, pre-contract, workflow, common patterns, modeling-design theory, QA checklist)
- **Coder**: `references/roles-编程手/` (SKILL, workflow, MATLAB spec, QA checklist)
- **Algorithm library (7 categories)**: `references/assets/01~07` (optimization, forecasting, evaluation, graph/network, statistics/data-processing, integrated, machine learning) + algorithm index
- **Visualization spec**: `references/可视化规范/` (chart selection, design theory, common pitfalls, journal specs, publication checklist)

### Into `presets/paper`
- **Paper writer**: `references/roles-论文手/` (SKILL, writing spec, paper format, LaTeX format, chapter template, self-review framework, English-writing workflow)

## Source 2: sweetcornna/mathodology

Award-grade (O / national-first-prize) quality-control methodology and workflow.

### Into `presets/paper`
- **Review gate**: `references/获奖评审/评审门禁-award-gates.md` (independent blind judging, bounded iteration budget, decision memo)
- **Evidence search**: `references/获奖评审/证据检索-evidence-search.md` (dual-source evidence discovery, source reconciliation, citation verification)
- **Workflow methodology**: `references/获奖评审/工作流方法论-WORKFLOWS_zh.md` (the full 9-phase award workflow)

## NOT shipped

- The reference repos' **Python/MATLAB scripts and tool sources**
- mathodology's full 9-skill system, search MCP server, and subagents/workflows templates
- Copyright and ownership remain with the original authors

If the team later needs these tool capabilities, integrate them under each project's respective license, or re-implement based on their implementation.
