# Vision Sub-agent

When the main model does not accept image input (`read_image` refuses), use a **`workflow` sub-agent pinned to a vision-capable model** to "see" the figure — for checking chart visual quality (blank/overlapping regions, missing axis labels, whether a figure supports a conclusion).

## Principle

DeepSeek Harness's `workflow` tool lets you specify `provider` and `model` independently on `agent()`. **The key prerequisite is choosing a model in the current deployment that actually accepts image input** (its `inputModalities` includes `image`), so the sub-agent can read and review the image.

Registered vision model names differ across deployments — do **not** hardcode one. Probe first.

## How to find an available vision model

Use the `llm` service's `listProviders()` / `resolveModelInfo(provider, model)` to iterate providers and pick a model whose `inputModalities` includes `image`:

```js
// Idea: iterate provider -> listModels/resolveModelInfo -> filter inputModalities includes 'image'
// Pick a model that accepts images and get its { provider, model }
const vision = /* a {provider, model} whose inputModalities contains 'image' */
await agent(prompt, { provider: vision.provider, model: vision.model })
```

## Usage template

Dispatch the vision sub-agent via `workflow` (replace `provider`/`model` with what you probed):

```js
await agent(
  'Use the read_image tool to read <absolute image path>, review the chart, and output a structured verdict: ' +
  'title, axis ticks/labels, legend, data lines, any blank or overlapping regions, and whether it is acceptable.',
  { provider: '<probed provider>', model: '<probed vision model>' }  // the vision model
)
```

## Validated example (this host)

On the deployment hosting this preset, `opencode-go / mimo-v2.5` (MiMo V2.5, `inputModalities` `text`+`image`, 1M context) was used and validated as the vision model:
- The sub-agent successfully read a PNG image
- It returned a structured review: title, chart type, axes, data lines, legend, and defects (e.g. "axis missing tick labels")
- The result can be used as evidence for chart QA / paper figure verification / review gates

> ⚠️ This is **one validated candidate**, not a name every deployment uses. On a different environment, re-probe as described above; if `mimo-v2.5` is unavailable, use any other model whose `inputModalities` includes `image`.

## Notes

- Do not hardcode `provider` / `model` — probe with `llm.resolveModelInfo` before use to confirm the model supports `image` input
- If the main model (e.g. `deepseek-v4-flash`) declares no image input, a direct `read_image` throws — that is expected; use this approach instead
