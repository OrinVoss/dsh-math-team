---
name: vision-subagent
description: 视觉审查子代理。当主模型不支持图像输入、需要审查图表/论文配图的视觉质量时使用——用 workflow 派生一个指定当前环境可用视觉模型的子代理，通过 read_image 看图并输出结构化视觉质检结论（空白、遮挡、坐标轴/图例缺失、是否支撑结论）。适用于任何需要"看图质检"的会话。
---

# 识图子代理（Vision Sub-agent）

当主模型**不支持图像输入**（`read_image` 会拒读）时，需要审查图表视觉效果（是否空白、遮挡、坐标轴缺标签、是否支撑结论）的环节，用 **`workflow` 派生一个指定视觉模型的子代理**来"看图"。

本 skill 是全局可用的视觉质检方案，任何预设/会话都可加载。

## 触发条件

- 主模型 `read_image` 报错拒读（如 `deepseek-v4-flash` 不声明图像输入）
- 需要核对图表/配图的视觉质量（空白、遮挡、缺标签、支撑关系）

## 原理

DeepSeek Harness 的 `workflow` 工具允许在 `agent()` 上独立指定 `provider` 与 `model`。只要选一个**当前部署里真正支持图像输入的模型**（其 `inputModalities` 含 `image`），派生的子代理就能用 `read_image` 读取并审查图片。

不同部署注册的视觉模型名可能不同，**不要硬编码模型名**，应先探测。

## 如何找可用的视觉模型

用 `llm` 服务遍历各 provider 的模型，过滤出 `inputModalities` 含 `image` 的：

```js
// 思路：遍历 provider -> resolveModelInfo -> 过滤 inputModalities 含 'image'，得到 { provider, model }
const vision = /* inputModalities 含 'image' 的 {provider, model} */
await agent(prompt, { provider: vision.provider, model: vision.model })
```

本套部署已验证的候选：`opencode-go/mimo-v2.5`（MiMo V2.5，text+image，100 万上下文）、`kimi-coding/k3/k3-256k`（text+image）。

## 用法模板

用 workflow 派发识图子代理（`provider`/`model` 替换为探测到的可用视觉模型）：

```js
await agent(
  '用 read_image 工具读取 <图片绝对路径>，审查图表并输出结构化结论：' +
  '标题、坐标轴刻度/标签、图例、数据线条、是否有空白或遮挡、是否达标。',
  { provider: '<探测到的provider>', model: '<探测到的视觉 model>' }  // 指定视觉模型
)
```

## 结构化审查输出（要求子代理按此格式返回）

审查子代理的输出应包含以下维度：

| 维度 | 审查点 |
|---|---|
| 标题 | 是否有清晰标题，与正文/主张一致 |
| 坐标轴 | 刻度、标签、单位是否缺失或错误 |
| 图例 | 是否缺失、是否足够区分数据系列 |
| 数据内容 | 线条/柱/点是否清晰、有无空白区域、有无遮挡/重叠 |
| 结论支撑 | 图是否客观支撑了它被用于支撑的结论（如 AIC 最优、回测改进） |
| 达标判定 | `PASS` / `FAIL`，FAIL 时给缺陷与改进建议 |

## 与"独立模型审查"的区别

- **识图子代理**（本 skill）：解决"主模型看不了图"，专注**视觉质检**（看图）。
- **独立模型审查**：用与主模型**不同厂商**的模型做内容/事实/一致性的对抗式挑错（不带图）。

两者可组合：先识图看视觉，再用独立模型审内容。

## 兜底

- 若探测不到任何 `inputModalities` 含 `image` 的模型，如实标记"此环境无视觉模型，视觉质检受限"，不要假装通过。
- 主模型若是纯文本模型，直接 `read_image` 报错属预期行为，应走本方案。
