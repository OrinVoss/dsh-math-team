# Mathodology Agent 工作流

Mathodology 支持两种编排模式：

- Claude Code：workflow 优先，使用项目 subagents。
- Codex：多 agents 分阶段并行执行，再由主 agent 综合。

两种模式都以国奖或 MCM/ICM O 奖级别为目标：题目覆盖完整、数学模型可辩护、计算可复现、论文表达成熟、提交包完整。

`.claude/workflows/mathodology-award-submission.md` 是 Claude Code 执行的权威来源；本文是给人阅读的共享 phase 模型和 Codex 接口，不得与之偏离。下文引用的运行时 gate schema、判审团协议、迭代预算和图表/PDF QA 脚本由 `mathodology-award-gates` skill 拥有。

## 外部质量信号

用这些信号校准工作流。它们不是固定模板，而是要转成 gate 的规则和评审预期。

- COMAP MCM/ICM 说明：Summary Sheet 是第一页且权重很高；解答以单个 PDF 提交；当前规则使用 25 页 solution 限制；参考文献、附录、代码和题目特别要求都计入 solution 页数；使用 AI 时必须披露并按要求附 AI 使用报告；匿名和来源引用是硬要求。来源：`https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php`。
- COMAP 评奖描述：Meritorious 及以上要求模型、分析、结论和表达清晰、有支撑、组织良好；Finalist 要超越仅仅满足题目要求；Outstanding 是建模、求解、分析和表达整体最强的论文。来源：`https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php`。
- COMAP 写作指导：高水平论文通常在 summary、问题分析、变量与假设、模型设计、测试、误差分析、敏感性或稳定性、优缺点、明确结论和来源记录上明显更强。来源：`https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php`。
- 国赛格式和评阅规则：论文和支撑材料分开处理；可运行源程序和支撑材料必须与论文相符；全国奖评阅使用独立评委和相似度查验；申报全国一等奖的论文会面对更严格的独立评阅。来源：`https://www.mcm.edu.cn/upload_cn/node/775/cQMeL0YY905244c8bd4b9af832f1699446d8385e.pdf`，`https://www.mcm.edu.cn/html_cn/node/b1f48689659f0660e80a2d6279d7b37d.html`。
- 国赛评阅要点示例：强论文应针对具体问题自主建模、体现创新、得到真实有效结果；弱论文常见问题是堆砌通用方法、简单复制算法、形式好看但内容空；有条件时应验证程序和结果。来源：`https://aimg8.dlssyht.cn/u/2179378/ueditor/file/1090/2179378/1663049277111493.pdf`。
- 公开优秀论文范例常见结构：摘要、问题分析、假设、数据预处理、分任务模型、结果分析、敏感性或鲁棒性、优缺点、结论、附录。把它当覆盖清单，不要机械套模板。参考范例：`https://reformship.github.io/pages/3competition/4mcm/MCM%20Outstanding/2024/F/2413565.pdf`，`https://explcre.github.io/files/mcm.pdf`。
- M3 Challenge 规则：团队在连续 14 小时窗口内完成，提交单个 PDF，图表、代码和其他图形都嵌入 PDF，正文建议控制在 20 页左右，第一页是 summary，并且 final-event validation 和 technical computing award 是额外评分面。来源：`https://m3challenge.siam.org/the-challenge/rules-and-guidelines/`，`https://m3challenge.siam.org/wp-content/uploads/01-M3_Official_Rules_and_Guidelines.pdf`。
- IMMC 规则：团队在选定的连续 5 天内工作，提交 PDF 解答，summary 在第一页，不接收非纸面软件材料，并要求模型测试、敏感性、误差分析、优缺点，以及用文字或图说明算法。来源：`https://www.immchallenge.org/Pages/Rules.html`。
- HiMCM/MidMCM 规则：团队在较长比赛窗口内二选一解题，提交英文 PDF，保持匿名，记录外部来源，使用 AI 工具时在正文和单独 AI 使用报告中披露。来源：`https://himcm.org.cn/instructions/`。
- 数据科学 leaderboard 竞赛不是论文优先。竞赛页、规则、数据说明、指标定义、sample submission、公榜/私榜切分和官方提交机制是硬约束。Kaggle 类竞赛中，官方 CLI 和 notebook 流程支持下载竞赛数据、生成提交文件和检查提交状态。来源：`https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md`。

## 共享 Phase 模型

| Phase | 目标 | 主要产出 | 验收门槛 |
|---|---|---|---|
| 0. 题目与评分 | 理解任务和评审面 | 题意重述、提交物、评分点、歧义登记 | 每个题目要求都有计划产出 |
| 1. 证据与数据 | 给问题建立依据 | 来源清单、数据计划、benchmark、引用笔记 | 每个模型输入都有数据、代理逻辑或假设 |
| 2. 候选模型 | 先比较路线再定型 | 三条模型路线、取舍表、最终路线、创新清单 | 路线匹配数据、时间、评分和题目；至少一项真实创新贡献，或显式标注获奖天花板风险 |
| 3. 数学规格 | 让模型可执行 | 符号、假设、目标、约束、算法、指标、头条数字来源 | coder 不需要临时发明数学；头条数字有基线和压力测试计划 |
| 4. 实验计算 | 生成可复现结果 | 代码、原始输出、表格、图、敏感性、鲁棒性、结果密度映射、偏离规格记录 | 论文中的数字可复现，核心结果有图表支撑；对比共用随机数、by-construction 结果如实标注 |
| 5. 解释结果 | 把结果接回题目 | 结论、图表说明、建议、局限、图表覆盖映射 | 每个结果回答题目问题 |
| 6. 论文初稿 | 形成完整论文 | 摘要、方法、结果、图表、参考文献、附录、单一权威推荐、创新清单（INN-n）和 scope ledger（MECH-n）收口 | 没有孤立结果、稀疏结果区、无支撑论断、推荐不一致或论文与代码不符；每个 INN-n 和 MECH-n 条目要么在正文承重要么被显式 descope |
| 7. 独立审稿 | 删除可修缺陷、确认获奖档位 | critic 审计外加三个并行盲评 `mathodology-award-judge` 评分表 | 无高严重度未解决问题；lead 聚合三席，只有每席位隐含档位达标、最低总分过线、无单项低于下限、且无未解决的共享评分项 >20 分歧时判审团才通过 |
| 8. 最终提交 | 组装提交包 | 论文、源码、代码、数据说明、README、AI 使用说明、清单 | 用户可直接提交 |

## 细化 Phase-Agent-Critic 矩阵

每个 phase 都有三层：专家产出、lead 综合、独立 critic gate。不能只凭专家产出进入下一 phase。

| Phase | 主 agent | 专家产出契约 | Critic gate |
|---|---|---|---|
| 0. 题目与评分 | lead, problem analyst, critic | 建立原子化需求映射、提交物清单、官方格式约束、评分假设、依赖图、歧义登记、竞赛关键问题。 | 每个题目语句都有负责人和输出路径；官方约束与假设分离；只把实质阻塞问题问用户。 |
| 1. 证据与数据 | evidence researcher, problem analyst, critic | 产出来源台账、链接或文件路径、可信度说明、抽取摘要、数据字典、代理数据逻辑、引用计划和证据缺口。 | 每个重要常数、数据集、benchmark 或领域判断都可追踪，或被标为假设并有敏感性检查计划。 |
| 2. 候选模型路线 | 至少两个 modeler, evidence researcher, critic | 至少三条路线，包含输入、方程或算法族、输出、优缺点、实现成本、数据匹配度和失败模式，外加一份点名至少一项真实贡献的创新清单。 | 选中路线必须能解释评分、数据、时间、可解释性和创新性；被拒路线有具体理由；禁止通用方法堆砌；不得把纯教科书做法当成获奖级；合成数据题禁止用"还原生成族"当贡献或选型理由。 |
| 3. 数学规格 | modeler, coder, critic | 写清符号、假设、量纲或单位、目标函数、约束、算法、伪代码、验证指标、baseline、ablation、敏感性和鲁棒性计划。 | coder 不需要临时发明数学；方程量纲一致；假设可测试或有证据；验证设计能暴露弱结论。 |
| 4. 实验计算 | coder, modeler, critic | 产出可复现脚本或 notebook、随机种子、环境说明、原始输出、整理表格、图、baseline、ablation、敏感性、鲁棒性、运行日志，以及覆盖模型结构、核心比较、敏感性、鲁棒性、权衡和建议的结果密度映射。 | 论文数字可重新生成或手工追踪；图有源数据；失败也被记录；不接受挑一次最好结果；图表稀疏或装饰性图表不能通过。 |
| 5. 解释结果 | modeler, evidence researcher, paper editor, critic | 把结果转成逐问回答、图表标题、建议、局限、不确定性说明、claim-source 链接，以及说明每个主要结论由哪张图或表支撑的覆盖映射。 | 每个结果都回答题目任务；每个论断都有数据、推导、图表、引用或明确假设支撑；局限不推翻主结论；重要结论不能只停留在文字断言。 |
| 6. 论文初稿 | paper editor, modeler, coder, critic | 完成摘要、引言、假设、方法、结果、敏感性、优缺点、结论、参考文献、必要的 AI 使用说明、页数约束内的最终图表布局，以及对照引用收口的创新清单（INN-n）和 scope ledger（MECH-n）收口。 | 摘要说明方法和最重要结论；论文不是实验流水账；符号、图注、引用、图表密度和需求覆盖一致；每个创新清单（INN-n）和 scope ledger（MECH-n）条目要么在正文承重要么在局限里被显式 descope。 |
| 7. 独立审稿 | critic, 三个盲评 `mathodology-award-judge` 席位, lead, 相关专家 rerun | critic 分别审计题目覆盖、数学有效性、原创性、论文与代码一致性、头条鲁棒性、推荐一致性、证据、复现、写作、格式和最终评分风险，并带 skill 归因；lead 在无共享上下文下并行分派三个盲评 `mathodology-award-judge` 席位（三席共享 summary/modeling/results 评分项；A 另加 writing/completeness、B 另加 innovation/evidence、C 另加权重最重的 correctness/reproducibility），不给目标奖级，各出一份评分表。 | 无 blocker/high 问题；每个 medium 问题已修复或有明确接受理由；lead lint 每份评分表并按阈值聚合（Outstanding/国一 总分 ≥ 85、下限 70；Finalist/国一边缘 80/65；Meritorious/国二 75/60），只有每席位隐含档位达标、最低总分过线、无单项低于下限、且无未解决的共享评分项 >20 分歧时判审团才通过；re-score 封顶 2 轮，然后出 decision_memo；critic 和判审都不能是原产出 agent。 |
| 8. 最终提交 | submission packager, paper editor, critic | 组装最终 PDF、必要的可编辑源文件、代码、数据或来源说明、图表、复现 README、AI 使用报告和 requirement-to-file 清单。 | 提交包符合规则、必要时匿名、无密钥和草稿文件、满足大小和页数限制，且未参与工作的人也能提交。 |

## Agent Handoff 契约

每个专家回复末尾都要带结构化 `handoff:` yaml block，便于 lead 和 critic 不重读完整历史也能审查。自由文本 handoff 会被拒绝。lead 用 `python3 .claude/skills/mathodology-award-gates/scripts/lint_run.py handoff` lint 每个 block，任何不符合 schema 或以自由文本提交的 handoff 都会被拒；每个 `artifacts[].path` 必须落在 `work/<run-id>/` 下。这个 schema 的权威定义在 `mathodology-award-gates` skill。

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

## Critic Gate 协议

每个 critic gate 必须独立、对抗，并且能链接证据。

- critic 阅读 phase handoff、源产物和 lead synthesis。
- critic 标注严重度：`blocker`、`high`、`medium`、`low`。
- `blocker` 或 `high` 问题阻止进入下一 phase。
- `medium` 问题需要负责人、修复计划，或在 phase log 中明确接受风险。
- 只有不会影响评分、正确性、复现或提交合法性的 `low` 问题才可排队。
- 任一产物缺少来源、计算路径或负责假设时，本 phase 不能通过。
- lead 必须记录 critic 发现和修复后才能推进。

critic 在每次 review 末尾给出结构化 `gate:` yaml block（用 `python3 .claude/skills/mathodology-award-gates/scripts/lint_run.py gate` lint）：

```yaml
gate:
  phase: 4
  loop: 0
  verdict: pass                # pass | fail
  issues:
    - {severity: high, summary: ..., artifact: ..., required_fix: ..., owner: mathodology-coder}
  evidence_checked: []
  missing_evidence: []
```

修复循环有硬性预算，避免无限打磨：

- 每个 per-phase critic gate 最多 2 轮修复（共 3 次评估）。
- Phase 7 最多 2 轮 re-score。re-score 轮不计入整轮 8 轮修复封顶：初始判审团是 round 1，两次允许的 re-score 是 round 2 和 round 3（r 最大为 3）。
- 整轮运行封顶 8 轮修复。
- 某轮没有改进就提前停止。改进的度量：gate 修复轮的改进 = 未关闭 blocker+high 问题数严格减少；Phase 7 re-score 的改进 = 最低席位 weighted_total 严格上升。
- 任一预算耗尽时，lead 不会静默继续：它输出 `decision_memo:` yaml block 并停下等人工决策。

```yaml
decision_memo:
  phase: 7
  budget_spent: {loops: 2, cap: 2}
  unresolved: []               # remaining issues with severity
  options:                     # 2-3 options, each {option, consequence, recommended: bool}
    - {option: ..., consequence: ..., recommended: true}
```

## 图表充足性 Gate

对 MCM/ICM O 奖、CUMCM 国一和类似论文优先竞赛，图表密度是 gate 项，不是最后美化。只有少数孤立图的论文，即使公式看起来合理，也应在 Phase 6 或 Phase 7 失败。

最终初稿通过前，图表系统至少应覆盖这些角色：

- 模型架构、算法流程或系统结构
- 数据、参数、假设或符号摘要
- baseline、模型路线或场景比较
- 敏感性分析
- 鲁棒性、不确定性、压力测试或误差分析
- 面向决策的权衡，例如成本、时间、环境影响、风险、实施路径或政策可行性
- 最终建议或逐问回答 dashboard

这些是最低覆盖角色，不是死板数量。一个强图可以同时承担多个角色，但填充式、重复式、装饰式或无支撑图表不计数。每张图和每个表都必须有源数据或计算路径，图注要写出结论，正文要解释它如何改变答案。

## 图表生成规范

本规范参考竞赛规则、公开 O 奖产物和绘图库真实行为：

- COMAP 要求解答以一个 PDF 提交，PDF 中包含文字、figures、charts 和支撑材料；所有图像、图、照片、表和绘图，要么由队伍创建，要么在提交文件中就地引用来源。来源：`https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php`。
- COMAP 强调 summary、组织结构、关键语句和主要结果会影响评委阅读路径。图表系统必须服务这个阅读路径，不能只是装饰。来源：`https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php`。
- 公开 O 奖仓库通常把论文源码、图表资源、代码和表格放在一起；例如 2024 ICM E 题 Outstanding/INFORMS 仓库包含完整论文、源码和 `paper_source_24/figure` 目录，LaTeX 源码中的图表也嵌入对应论证段落。来源：`https://github.com/ydchen0806/24ICM_E_O_Award_Paper_code`。
- Matplotlib 的 constrained layout 可以减少刻度、图例、colorbar 等重叠，但官方文档也说明其他 artist 仍可能被裁切或重叠，所以 annotation、自定义文字和复杂图必须单独检查。来源：`https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html`，`https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.annotate.html`。
- Matplotlib 的 bar label 文档说明标签可能需要调整坐标轴范围；真实 GitHub issue 也展示了 bar label 在常见变换下发生重叠的情况。来源：`https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar_label.html`，`https://github.com/matplotlib/matplotlib/issues/22414`。
- Seaborn 文档提供 style/context/font scale 控制。即使用纯 Matplotlib，也要采用这种显式样式管理思路。来源：`https://seaborn.pydata.org/tutorial/aesthetics.html`。

### 产物契约

每张图和每个表必须包含：

- 稳定文件路径、确定性生成命令、源数据路径
- 明确证据角色：模型结构、数据、假设、baseline、敏感性、鲁棒性、不确定性、权衡、决策、memo 或附录
- 论文位置，以及它支撑的精确结论
- 能写出 takeaway 的 caption，而不只是图表类型
- 每个定量轴或表格列都有单位
- 有意义的有效数字，不能伪装精度
- 如果数值来自代理、假设、模拟或外部来源，必须注明

coder 在 Phase 5 前必须产出图表 inventory。packager 必须把 inventory 写入最终 checklist 或 README。

### 设计规则

默认遵守以下规则，除非竞赛或期刊格式另有要求：

- 折线图、流程图、网络图、地图和密集标签图优先输出矢量格式 `.pdf` 或 `.svg`。仅对栅格图像（如照片、位图底图）或管线要求时使用 `.png`；草稿至少 180 dpi，最终至少 300 dpi。
- 多面板图使用 `layout="constrained"` 或显式 `GridSpec` 间距。含长标签、colorbar、legend、annotation 或 suptitle 的图，不能只依赖 `tight_layout()`。
- 图宽应匹配论文位置。常规全宽图约 6.5-7.2 英寸；多面板 dashboard 可到 7.2-9.0 英寸，但嵌入 PDF 后文字和 caption 必须可读。
- 最终 PDF 中的刻度、图例、节点标签、热力图单元格和注释通常不小于 8 pt。
- 图内 title 只放短描述；claim 放在 caption 和正文。避免 `Figure 2: Figure 2.` 这种重复。
- 长类别标签应换行、缩写并在表注解释，或改用横向条形图。除非没有更好方案，避免超过 30 度的斜刻度。
- 使用色盲友好 palette。顺序值用 sequential palette，正负偏差用 diverging palette，类别用 categorical palette，避免 rainbow。
- 重要区别不能只靠颜色表达；需要加 marker、线型、hatching、直接标签或表格数值。
- 只给关键点直接标注。如果每个点都要识别，改用表格、小多图或编号 legend。
- 只有当数量级差异本身是结论时才用 log/symlog，并在 caption 中说明。

### 图型规则

网络图、流程图和架构图：

- 节点文字和边标签必须是不同 artist，并放在不同坐标。
- 边标签放在边的中点附近，使用白色或浅色背景，不能压在节点文字上。
- 箭头不得穿过节点标签，除非语义必要且仍清晰。
- 节点必须足够容纳标签；否则节点编号，旁边给 legend 表。

条形图和柱状图：

- 长场景名使用横向条形图。
- 只有在不碰撞柱、坐标轴或边界时才添加数值标签。
- 标签在柱外时，标注后把坐标轴范围扩大 5-10%。
- 值相差超过一个数量级时，考虑 log/symlog、插图，或“表格 + 图”，不能让小柱消失。

折线图：

- 坐标轴必须有单位和场景含义。
- 尽量在右端直接标线名；否则把 legend 放在图外或空白区域。
- 当折线支撑不确定性下的建议时，必须展示置信区间、场景范围或敏感性带。

热力图和矩阵：

- 必须有带单位的 colorbar。
- 单元格文字颜色根据背景亮度选择，不能固定黑字或白字。
- 矩阵规模必须能在正文读清；大矩阵放附录表或支撑材料。

散点、Pareto 和权衡图：

- 明确说明每个轴是越小越好还是越大越好。
- 只标注 baseline、被选方案、dominated 点或 frontier 上需要论证的点。
- marker 大小和颜色必须有 legend 或说明，不能让气泡大小暗示未解释的值。

表格：

- 精确值用表格，趋势和结构用图。
- 使用 booktabs 风格或同等清晰边线；除矩阵外避免满格线。
- 表头尽量短，把解释放入表注。
- 统一舍入，不展示超过模型和数据支撑的位数。
- 宽表或换行混乱的表应拆分，或移入支撑材料；旋转表只能作为最后方案。

### 生成代码规则

图表生成代码必须：

- 定义可复用 style 常量：字体、颜色、线宽、marker、DPI
- 模拟类图表设置随机种子
- 每张图保存前或同时写出源 CSV/JSON 数据
- 保存后关闭 figure，避免隐藏状态污染
- 有结构化数据时不要手写字符串解析
- 除非明确记录，不要把多个文字对象放在同一坐标
- 导出能适配 PDF 的白底或透明背景
- 从干净 package root 可一键重生所有图表

Matplotlib 额外规则：

- 优先 `fig, ax = plt.subplots(..., layout="constrained")` 或 `fig = plt.figure(layout="constrained")`
- annotation 必须显式设置 `xy`、`xytext`、`textcoords` 和 `bbox`；不能把节点坐标同时当节点标签和边标签
- `bar_label` 或手动 bar label 后，必须调整 `xlim`/`ylim` 让标签可见
- 热力图单元格文字颜色要根据数值归一化后选择
- 长类别名用 `textwrap.fill` 或横向条形图
- 保存后检查真实导出图，不要只看 notebook 预览

### PDF 嵌入规则

paper editor 必须检查最终渲染 PDF，而不仅是 Markdown/LaTeX 源码：

- 图应出现在引入它的段落一页以内，除非明确是附录图
- 图不能被裁切、空白、像素化或不合理拆页
- 图或表内部无文字重叠
- 坐标轴、刻度、图例、colorbar、表头和 caption 不被裁切
- caption 不重复、不与图内 title 冲突
- 每张图和表都在附近正文中被解释
- 图表放置后仍满足页数限制

### 自动和视觉验证

Phase 6 或 Phase 8 通过前，运行 `mathodology-award-gates` skill 中已交付的图表/PDF QA gate。执行已交付的脚本 —— 不要内联重写它们的逻辑。`figqa.py` 主要是可导入 gate：把 `assert_no_overlap(fig)` 接入图表工厂，任何文字/annotation/legend 与数据 artist 重叠，或任何被裁切的 artist，都会让本次运行失败。`make_contact_sheet.py` 从编译后的 PDF 生成 contact sheet，`pdf_qa.sh` 检查渲染 PDF 的页数、重复 caption 前缀、匿名元数据和空白页。

```bash
python3 .claude/skills/mathodology-award-gates/scripts/figqa.py --self-test
python3 .claude/skills/mathodology-award-gates/scripts/make_contact_sheet.py work/<run-id>/paper/solution.pdf -o work/<run-id>/outputs/figures/contact_sheet.png
bash    .claude/skills/mathodology-award-gates/scripts/pdf_qa.sh work/<run-id>/paper/solution.pdf --max-pages 25 --anonymous
```

`--max-pages 25` 是当前 MCM 规则；其他竞赛按 `variant:` block 的 `limits.pages` 设置。MCM 的 AI 使用报告不计入 25 页（`--max-pages` 只约束 solution 正文）。

这些脚本的通过输出就是必需证据；本次运行收集的产物必须包含：

- 生成图数量和表数量
- 从编译后 PDF 生成的 contact sheet，而不是源图
- 渲染后 PDF 页数和一份干净的 `pdf_qa.sh` 报告
- 每张生成图的零碰撞证据：重跑 `run_all.py`（内嵌 `assert_no_overlap`）并观察 exit 0 —— `figqa.py --self-test` 证明 gate 本身有效
- 最终包 checksum 或干净重建证明

critic 仍必须目检 contact sheet，并至少检查含密集图表的页面。程序化 gate 不能替代目检，因为 layout engine 可能给出数学上合法但阅读上失败的结果。

### 失败条件

出现以下任一项即阻断 phase：

- 节点标签、边标签、数据标签或 annotation 重叠
- 最终 PDF 中文字过小无法阅读
- 图为空白、被裁切、像素化或有过多无效空白
- 图题、caption 和正文重复但没有解释
- 坐标轴缺单位或尺度误导
- 编码数值缺 legend 或 colorbar
- 图漂移到远离相关段落的位置，形成孤立图堆
- 表格换行混乱或溢出页面
- 图只是凑数量，不支撑任何结论
- 代码不能从提交包数据重生图表

## 竞赛类型工作流适配器

9-phase 模型是默认流程。Phase 0 结束前，lead 必须判断竞赛类型并套用一个适配器。如果竞赛官方规则和适配器冲突，以官方规则为准。

| 类型 | 适用场景 | 工作流重点 | 额外 critic gate |
|---|---|---|---|
| MCM/ICM O 奖 | COMAP 本科组 MCM/ICM，英文论文，4 天左右开放题 | 25 页 solution 纪律、summary-first 叙事、AI 使用透明、来源引用、逐问覆盖 | summary 不是套话；AI 使用报告和引用合规；无身份泄露；页数取舍保护结果和结论 |
| CUMCM 国一 | 全国大学生数学建模竞赛或类似“论文 + 支撑材料”提交 | 中文摘要和论文格式、论文与支撑材料一致、代码可运行、附录文件列表、匿名、查重风险 | 论文 PDF 与支撑包一致；代码能复现关键结果；无队伍/学校/赛区身份；支撑包不含无关文件 |
| HiMCM/MidMCM | 高中 COMAP 风格长窗口竞赛 | 更强脚手架、可读英文表达、选题支持、模型复杂度保守、AI 使用披露 | 模型能被高中团队诚实解释；最终 PDF 英文、匿名、可读；外部来源和 AI 使用披露完整 |
| IMMC / IM2C | 中学生国际 5 天建模挑战 | 本地语言到英文的翻译风险、不提交软件包、论文简洁、用文字/图解释算法、顾问和表格截止时间 | 翻译没有改进或改变原作；没有代码文件也能理解算法和测试；控制号和页眉正确 |
| M3 Challenge | 14 小时冲刺，单 PDF 提交，可能争取 MATLAB technical computing award | 严格时间盒、快速可行 baseline、简洁首页 summary、嵌入代码/图表、validation presentation 准备 | 单 PDF 满足大小/页数建议；technical computing 体现洞察而不是堆代码；最终结果能回答现场验证问题 |
| 数据科学 leaderboard | Kaggle、DrivenData、天池或企业指标型竞赛 | 指标对齐、防 leakage、训练/验证切分、公榜/私榜风险、可复现 pipeline、提交文件 schema | 验证指标贴近官方指标；无 test/public leaderboard leakage；提交 schema 匹配 sample；明确管理私榜过拟合风险 |
| 运筹/政策/商业案例赛 | 商业、物流、能源、金融、公共政策或咨询式建模 | stakeholder framing、决策变量、约束、场景分析、可执行建议、成本和可行性 | 建议能落地；约束贴近现实；场景和敏感性覆盖决策风险；假设能被 stakeholder 接受 |
| 研究生数模 / 华为杯 | 中国研究生数学建模竞赛及类似多天、含真实工业数据的研究生赛 | 在硬核上深而非广、诚实处理脏数据、给出非显然的建模/算法贡献、可运行代码与数据出处 | 硬核被深入正确求解；真实数据如实处理并披露清洗；存在真实贡献；论文、代码、附录一致且可复现 |
| APMCM 亚太赛 | 亚太地区竞赛，中英文赛道，较短的 COMAP 式窗口 | 结果先行摘要、有非通用动作的可辩护模型、诚实敏感性、按官方规则确定语言/模板 | 摘要可独立成立；模型有非通用动作；有敏感性；语言、模板、匿名和文件规则符合官方政策 |
| MathorCup / 主题国内杯赛 | MathorCup、电工杯、数维杯、深圳杯、小美赛等赞助或主题杯赛 | 逐杯读规则、先 baseline 再聚焦一项贡献、演示级图表、主题杯用赞助方决策语言 | 每个必答题都有答案；推荐在摘要/正文/备忘一致；代码与数据和论断对齐；格式与支撑规则符合该杯赛；演示质量达标 |
| 短时冲刺/校内邀请赛 | 6-24 小时本地赛、训练赛或轻格式规则 | 速度、baseline-first、选择性证据、简单鲁棒模型、清晰叙事、快速提交包审计 | 早期已有完整可提交答案；不过度复杂化；最终答案优先正确性和清晰度 |
| 未列出的竞赛 | 不匹配上面任何一行的竞赛 | 按提交物、评审面、窗口、层级和领域框架分类，再综合最接近的适配器；绝不默认 MCM | 所有通用获奖 gate 仍生效；在 variant handoff 记录综合出的适配器及其来源适配器 |

### 适配器分派规则

- Phase 0 必须记录 `contest_type`、官方规则来源、deadline、语言、文件限制、身份规则、代码政策、AI 使用政策和最终提交清单。
- 只有无法安全推断竞赛类型、官方规则、deadline 或提交格式时，lead 才问用户。
- 每个 phase 的 critic gate 都必须包含对应适配器的额外 gate，冲击顶档时还要包含通用获奖 gate（创新清单、点名机制 scope ledger、头条鲁棒性、推荐一致性、论文与代码一致、Phase 7 获奖档位判审团评分表）。
- 如果是论文优先型竞赛，paper editor 和 critic 要更早加入，从 Phase 2 或 Phase 3 开始。
- 如果是代码/leaderboard 优先型竞赛，coder 和 critic 要更早加入，从 Phase 1 开始；paper editor 可延后到解释阶段。
- 如果是 sprint 型竞赛，每个 phase 先交付最小可行产物，有余力再增强。
- 如果是中学生或翻译敏感竞赛，paper editor 必须检查可读性、词汇复杂度，以及团队是否能诚实答辩。
- 如果有 interview、presentation 或 validation round，Phase 8 增加 defense brief，列出可能评委问题、回答要点和产物引用。

## Claude Code Workflow 模式

适用于把本仓库 clone 后在 Claude Code 中打开。

主入口：

```text
.claude/workflows/mathodology-award-submission.md
```

Subagents（9 个）：

- `mathodology-lead`：phase 控制、综合、风险登记
- `mathodology-problem-analyst`：题目拆解和评分映射
- `mathodology-evidence-researcher`：文献、数据、benchmark、引用
- `mathodology-modeler`：数学建模、方法选择、验证设计
- `mathodology-coder`：可复现计算、图、表
- `mathodology-critic`：对抗审稿和 phase gate
- `mathodology-paper-editor`：论文叙事与润色
- `mathodology-award-judge`：Phase 7 的一个独立盲评席位（lead 并行分派三个）
- `mathodology-submission-packager`：最终提交包和复现 README

全部 9 个 subagent 都在 frontmatter 里固定为 `model: opus`。`CLAUDE_CODE_SUBAGENT_MODEL` 环境变量或按次调用的 model 参数会覆盖 frontmatter 固定（env/按次调用 > frontmatter）。lead 始终作为 Claude Code 主线程运行，绝不作为被分派的 subagent，因为被分派的 subagent 无法再生成本 workflow 所需的专家 subagent。

执行方式：

1. `mathodology-lead` 加载 `mathodology-whole-project`、`mathodology-agent-pipeline` 和 `mathodology-award-gates`。
2. Lead 启动 Phase 0 并分派专家。
3. 专家独立产出本阶段材料，每个都以 `handoff:` block 收尾。
4. Lead 合并为统一决策记录。
5. `mathodology-critic` 审计本阶段并返回 `gate:` block。
6. Lead 在迭代预算内修复或重新分派，直到 gate 通过。
7. Phase 7 时 lead 分派三个盲评 `mathodology-award-judge` 席位并聚合评分表。
8. 重复到 Phase 8。

如果用户只通过 `skills` CLI 全局安装 skills，Claude Code 可能不会获得 `.claude/agents` 和 `.claude/workflows` 文件。这时加载 `mathodology-whole-project`，并按本文的 phase 模型执行。

## Codex 多 Agents 模式

适用于把 skills 全局安装到 Codex 后使用。Codex 运行会加载 `mathodology-whole-project` 和 `mathodology-award-gates` —— 后者拥有 handoff/gate/scorecard/decision_memo schema、判审团阈值、迭代预算和图表/PDF QA 脚本。

启动提示：

```text
Use $mathodology-whole-project. Run the Mathodology 9-phase award submission workflow in Codex multi-agents mode. Work phase by phase: dispatch independent agents for analysis, modeling, evidence, coding, critique, and writing where applicable; synthesize their output; require result-density maps, figure/table sufficiency gates, and rendered-PDF figure QA; run the phase gate; then continue automatically. Pause to ask the user only for contest-critical details that would change requirements, data access, model choice, compute budget, or final submission constraints. For ordinary ambiguity, make a conservative assumption, record it in the phase log, and keep going.
```

Codex agent 角色：

- 主综合 agent
- 题目分析 agent
- 证据与数据 agent
- 模型设计 agent
- 实验计算 agent
- Critic agent
- 论文写作 agent
- 三个独立的 Phase 7 判审 agent（盲评团）
- 提交打包 agent

在 Codex 里，Phase 7 盲评判审团被模拟成三个互不共享上下文的独立 agent 调用。每个只拿到自己的 seat brief —— 三席共享 summary/modeling/results 评分项；A 席（旗舰通用评委）另加 writing 与 completeness，B 席（创新与决策有用性）另加 innovation 与 evidence，C 席（怀疑型裁判）另加权重最重的 correctness 与 reproducibility —— 外加渲染后 PDF 和 `package/manifest.md`，绝不给目标奖级或阈值。各自返回恰好一份 `scorecard:` block。lead 校验每份 block，然后按 `mathodology-award-gates` 阈值聚合三席（Outstanding/国一 总分 ≥ 85、下限 70；Finalist/国一边缘 80/65；Meritorious/国二 75/60），共享评分项分歧超过 20 时绝不取平均抹平。

### Codex 确认与连续执行

Codex 不一定能在一次回复里完成全部 9 个 phase。把流程设计为可恢复的连续执行，而不是一次性输出：

- 保留 phase log，记录当前 phase、已通过 gate、假设、未解决风险、产物路径和下一步动作。
- 如果一次回复到达边界，先完成当前综合或 gate，明确写出继续状态；用户说继续后，从这个状态恢复。
- 除非用户新信息推翻前面结论，不要重跑已完成 phase。
- gate 通过且没有竞赛关键问题阻塞时，自动进入下一 phase。
- 在回复边界必须停止时，用这个格式收尾：

```text
Continuation state:
- Current phase:
- Completed gates:
- Blocking user question, if any:
- Assumptions to carry forward:
- Artifact paths:
- Next action:
- Suggested prompt: Continue from the current continuation state and run the next Mathodology phase gate.
```

只有当答案会实质改变以下内容时，才向用户提问：

- 官方竞赛要求、提交格式、页数限制、AI 使用规则或截止时间
- 私有文件、数据集、付费来源、凭据或外部服务访问
- 多条可行模型路线之间的选择，且路线会带来不同评分或可行性风险
- 计算量、运行时间、语言、工具或复现约束
- 无法安全推断的最终结论、建议或提交包决策

非关键歧义采用最稳妥、可辩护的默认假设，写入 phase log 后继续执行。必须问用户时，问题要紧凑说明当前 phase、为什么重要、推荐默认值，以及常见答案的后果。用户回答后，从当前 phase log 恢复，不要重新执行已完成工作。

Codex 执行规则：

- 只有任务输入独立或可独立 review 时才并行。
- 每个 agent 都要有窄 brief、预期文件和 phase gate。
- Phase 2 至少让两个 agent 独立提出模型路线。
- 每个 gate 都由独立 critic agent 审查。
- Phase 7 分派三个独立盲评判审 agent，并按 award-gates 阈值聚合评分表；任一预算耗尽（每 gate 最多 2 轮修复、Phase 7 最多 2 轮 re-score、整轮封顶 8 轮）时输出 decision_memo 并停下交用户。
- 保留 phase log：决策、假设、被拒路线、证据、命令、输出路径。
- 最终回复前，按 Phase 8 检查提交包完整性。

## 最终提交包内容

完整奖项级提交包应包含：

- 最终论文 PDF
- 竞赛要求的可编辑论文源文件
- 代码或 notebooks
- 数据文件或数据来源说明
- 生成的图和表
- 复现 README
- 假设和符号说明
- 敏感性与鲁棒性证据
- 必要时的 AI 使用说明
- 题目要求到提交文件的最终映射清单

## 质量线

未满足以下条件前，不要声称达到奖项级：

- 有多条模型备选路线，并以与模型无关的依据给出清晰选择理由
- 至少一项超越教科书式套用的真实建模贡献——只做得扎实但平庸的工作上限是 Meritorious / 国二，到不了 Outstanding / 国一
- 题目点名的每个机制要么被建模，要么有经标注的合理 descope
- 假设有证据支撑
- 计算可复现，且对比之间共用随机数
- 有敏感性或鲁棒性分析，包括对每个头条数字针对其控制参数做压力测试
- 有足够的有效图表，让模型结构、比较、敏感性、鲁棒性、权衡和最终建议可被评委快速检查，且不浪费版面
- 逐问覆盖题目
- 推荐在摘要、正文、备忘和结论中一致
- 论文中的方法描述与交付代码一致
- 论文叙事成熟
- 经过独立 critic 审稿，并有达到目标档位的获奖判审团评分表
- 结构化的 yaml handoff/gate/scorecard/decision_memo 产物，由随 skill 交付的 `lint_run.py` 校验
- 有界的 gate 迭代预算（每个 critic gate 最多 2 轮修复、Phase 7 最多 2 轮 re-score、整轮封顶 8 轮），预算耗尽时向用户输出 decision_memo 升级
- 已交付的图表/PDF QA 硬门（`figqa.py`、`pdf_qa.sh`），其通过输出是必需证据
- 最终提交包完整，且合规项已对渲染后的 PDF 核对
