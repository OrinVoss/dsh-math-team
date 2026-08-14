# DSH 数学建模团队插件包

面向 **DeepSeek Harness** 的团队化数学建模工作流插件包。把参考成熟数学建模 Skill 仓库的方法论，整理成 **2 套可直接安装的 Agent 预设（preset）**，配合团队 **Gitee/GitHub 多文件夹协同**，实现多人在各自独立工作区互不干扰地协作完成数学建模竞赛题。

本仓库挂载于 GitHub Topic：**`dsh-plugin`**。

## 这是什么

在 DeepSeek Harness 中，一个 **Agent 预设（preset）**就是一套岗位配置：包含 persona（角色职责）、可用的工具集、以及随预设安装的 **Skills**（岗位能力文档）。每个会话选择某个预设，就获得了该岗位的全部能力。

本包提供 **2 套岗位预设**：

| 预设目录 | 岗位 | 面向 | 核心能力 |
|---|---|---|---|
| `presets/model-code` | 建模+编程 Agent | 2 名建模编程成员（共用） | 题目分析与建模、Python/MATLAB 求解、结果与图表产出、复现清单；含建模手/编程手/算法资料/可视化文档 |
| `presets/paper` | 论文 Agent | 1 名论文成员 | 论文撰写（Word/LaTeX）、证据检索核验、独立评审质检门禁；含论文手/获奖评审/证据检索文档 |

### 每套预设包含
- `agent.cordis.yml` — Harness 能力基线（源自部署的 `cordis` 预设，含 shell / fs / jobs / 子代理协作 / 网页搜索 / skill 加载等）
- `preset.yml` — 预设元数据（名称、描述）
- `skills/<name>/SKILL.md` — 岗位主技能（职责、流程、质量门禁、协同规则）
- `skills/<name>/references/` — 随预设安装的方法论文档（按需加载）

### 关键特性
- **团队协同**：预设内置"Gitee 仓库三独立文件夹"协同协议（`member-a/` `member-b/` `member-c/`），各成员只提交自己文件夹，互不干扰
- **质量门禁**：建模终检 M1 / 最小可运行 P1 / 编程终检 P2 / 证据大纲 W1 / 论文终检 W2
- **识图子代理**：当主模型不支持图像输入时，用 `workflow` 派生一个指定视觉模型（`opencode-go/mimo-v2.5`）的子代理审查图表

## 安装

### 前提
- 已安装 DeepSeek Harness（dsh）
- 关闭 dsh 进程，或安装后重启会话使其生效

### 方式一：一键安装脚本（推荐）
把 `presets/` 复制到本机用户预设根目录：
```powershell
# Windows
Copy-Item -Recurse .\presets\model-code "$env:USERPROFILE\.dsh\.agent-presets\model-code"
Copy-Item -Recurse .\presets\paper "$env:USERPROFILE\.dsh\.agent-presets\paper"
```
```bash
# macOS / Linux：复制到 $HOME/.dsh/.agent-presets/
mkdir -p "$HOME/.dsh/.agent-presets"
cp -R presets/model-code presets/paper "$HOME/.dsh/.agent-presets/"
```

### 方式二：手动复制
将 `presets/model-code` 与 `presets/paper` 两个文件夹原样放入 `~/.dsh/.agent-presets/`，保持目录名不变。

### 验证安装
重启 dsh 并新开会话，预设选择器中应出现 **`建模编程 Agent`** 与 **`论文 Agent`**。用 `agentPresets` 服务可校验挂载：
```js
await agentPresets.standingKeyFor('model-code')  // 不抛错即成功
await agentPresets.standingKeyFor('paper')
```

## 快速开始（团队协同模式）

1. 在 Gitee/GitHub 建一个空私有仓库（团队共享）
2. 首次 clone 后按 `docs/团队协同.md` 初始化 `member-a/ member-b/ member-c/` 三文件夹基线
3. 2 名成员开 `model-code` 预设会话在各自独立工作区 clone，分别产出建模+编程交付物到自己的 `member-*` 文件夹并 push
4. 论文成员开 `paper` 预设会话，`git pull` 拉取 A、B 交付物，在 `member-c/` 撰写论文并 push
5. 全程只提交自己那个 `member-*` 文件夹，互不干扰

各岗位的开工口令模板见 `docs/团队协同.md`。

## 文档

- [团队协同说明](docs/团队协同.md) — 三文件夹协同协议、交接契约、各岗位开工口令
- [识图子代理](docs/识图子代理.md) — 主模型不读图时的视觉审查方案
- [方法论来源](docs/方法论来源.md) — 两套预设吸收的参考仓库内容清单
- [示例题目全流程跑通记录](docs/示例题目全流程跑通记录.md) — 用 2023 国赛 C 题真实跑通「建模→论文→评审」完整链路的验证记录

## 方法论来源

本包的岗位方法论文档整理自（仅文档，脚本/工具源码未搬运）：

- [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) — 三阶段工作流（建模/编程/论文）、质量门禁、算法资料、科学可视化规范、复现清单
- [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) — 获奖评审门禁（盲评/有界迭代）、证据检索、完整工作流方法论

## License

MIT（最宽松许可证，仅要求保留版权声明）
