# Model Capability Configuration Guide

In DSH, "can this model read images?" and "which models may sub-agents use?" are decided by **configuration declarations, not automatic model detection**. Miss one declaration line and a perfectly capable model becomes unusable. This doc covers how to inspect, how to declare, and how to handle common errors.

---

## 1. How to inspect current model capabilities

### Use the `llm` service

Mount a temporary Cordis plugin (or have the agent `cordis_define` one), inject `llm`, and query:

```js
// list every model of every provider
for (const p of ctx.llm.listProviders()) {
  const models = await ctx.llm.listModels(p.id || p.name)
  for (const m of models) {
    const info = await ctx.llm.resolveModelInfo(p.id || p.name, m.id || m.name)
    console.log(p.id, m.id, info.inputModalities)   // ['text'] or ['text','image']
  }
}
```

A model can read images **only if** `info.inputModalities` includes `image`.

---

## 2. Declaring image capability (the most common pitfall)

### The key fact

DSH's capability field **defaults to `["text"]`**:

```js
inputModalities: model.inputModalities ?? ["text"]
```

So even if a model genuinely supports images, **without an `image` declaration `read_image` is refused**:

```
Error: cannot read "xxx.png" as an image:
model "xxx" does not declare image input;
switch to an image-capable model to read images
```

### How to declare

Add `inputModalities` to the model entry under its provider in `~/.dsh/settings.yaml`:

```yaml
llm-deepseek:
  models:
    - id: deepseek-flash
      name: DeepSeek-V4.1-Flash
      inputModalities:
        - text
        - image        # ← add this line and it can read images
```

> Configuration is **hot-reloaded**; a DSH restart is usually unnecessary.

### Optional image parameters

Once `image` is declared, you may tune image budgets (defaults apply if omitted):

```yaml
      inputModalities:
        - text
        - image
      imagePixelBudget: low      # pixel budget: a number, or "low"
      imageMaxBytes: 1048576     # per-image encoded byte cap
```

### Schema constraints (invalid values are rejected)

- `inputModalities` may contain only `"text"` / `"image"`; it **must not be empty or contain duplicates**;
- A **text-only model must not declare** `imagePixelBudget` / `imageMaxBytes` (it errors).

---

## 3. Sub-agent model allowlist

DSH can restrict which models sub-agents may use, via `settings.yaml`:

```yaml
subagent-model-selection:
  enabled: true
  allowedModels:
    - provider: deepseek-official
      model: deepseek-flash
    - provider: kimi-coding
      model: k3-256k
    - provider: kimi-coding
      model: kimi-for-coding
```

**Key points**:
- When `workflow` / `subagent` dispatches a child, **naming a model outside the allowlist fails** (the child returns `null`);
- Before planning which model does image review or content review, confirm it is in the allowlist — or add the target model to it.

---

## 4. Common error reference

| Error / symptom | Cause | Fix |
|---|---|---|
| `model "X" does not declare image input` | Missing `image` declaration (defaults to `["text"]`) | Add `inputModalities: [text, image]` to that model's config |
| `The DeepSeek chat-completions adapter does not support image content` | Request took the text-only path | Same as above: declare image |
| Sub-agent returns `null` / no output | A model **outside the allowlist** was specified | Use a model from `allowedModels`, or add the target model |
| Preset mount fails: `$.prefix missing required value (at prefix)` | After a DSH upgrade, `dsh-persona`'s field changed from `text` to `prefix` | Rename `text:` to `prefix:` in `agent.cordis.yml` |
| `row(s) published process-global service(s) [...]` | A preset row publishes a service without an `isolate` realm | Wrap that row in a `cordis:group` with `isolate` |

---

## 5. A real case (2026-09-10)

**Symptom**: reading an image with DeepSeek V4.1 Flash (`deepseek-official/deepseek-flash`) failed with `does not declare image input`.

**Diagnosis**:
1. `llm.resolveModelInfo` reported `inputModalities = ["text"]`;
2. Reading the `dsh-llm-deepseek` source showed the adapter **does support images** (`prepareRequestImages`, `resolveRequestImagePolicy`, v4 vision token accounting, PNG/JPEG/WebP/GIF support), and its built-in catalog declares `deepseek-v4-flash` as `["text", "image"]`;
3. Root cause: the custom `deepseek-flash` entry in `settings.yaml` **was missing the image declaration**.

**Fix**: add `inputModalities: [text, image]`.

**Verification**: after the fix, V4.1 Flash read the image successfully and produced a full item-by-item review (title / axes / legend / overlap / geometric consistency / PASS verdict).

---

## 6. File-reading capability comparison (measured 2026-09-10)

| Type | Can the main model read it directly? | Notes |
|---|---|---|
| **Images** (PNG / JPG / WebP / GIF) | ✅ **Yes** (if `image` is declared in config) | Use `read_image` directly; the main model sees the image and can review it |
| **PDF** | ❌ **No** | The `read` tool only handles UTF-8 text and returns `binary file` for PDFs; extract with a script (pypdf / pdfplumber), or upload via the Web UI and read through the file tool |

**Impact on workflow**:
- **Figure QA can be done by the main model** when it supports images — no need to dispatch a vision sub-agent (one less hop);
- **Still use a vision sub-agent when**: ① the main model cannot read images; ② you want an independent/isolated visual verdict, or a cheaper vision model;
- **PDF problems/templates still need scripted text extraction** (no native PDF tool on the agent side today).

### PDF text extraction (verified working)

The local `python` comes from msys64 and has **no pip**; the reliable route is `uv`, which installs the dependency into a throwaway environment.

**Step 1: write `extract_pdf.py`**

```python
from pypdf import PdfReader
import sys

src, dst = sys.argv[1], sys.argv[2]
reader = PdfReader(src)
parts = []
for i, page in enumerate(reader.pages, 1):
    parts.append(f"===== page {i} =====")
    parts.append(page.extract_text() or "(no text)")
with open(dst, "w", encoding="utf-8") as fh:
    fh.write("\n".join(parts))
print(f"extracted {len(reader.pages)} pages -> {dst}")
```

**Step 2: run it through `uv`** (temporarily installs `pypdf`, leaves the system untouched)

```powershell
uv run --with pypdf python extract_pdf.py "problem.pdf" "problem.txt"
```

**Step 3**: read the generated `problem.txt` with the `read` tool.

**Alternatives**:
- If your system Python has pip: `pip install pypdf` and run the same script;
- For tables/layout, use `pdfplumber` instead (`uv run --with pdfplumber ...`);
- If the PDF was uploaded through the Web UI, try the file tool directly (availability depends on the deployment).

## 7. Takeaways

1. **"Can it read images" depends on the declaration, not the model's reputation** — verify with `resolveModelInfo` instead of guessing;
2. If a genuinely image-capable model is refused, **first check whether `image` is declared in its config**;
3. **Check the allowlist before dispatching a sub-agent**, to avoid a wasted run;
4. **Watch for schema changes after a DSH upgrade** (e.g. `text` → `prefix`); running a preset mount check (`agentPresets.standingKeyFor(id)`) right after upgrading surfaces them early.
