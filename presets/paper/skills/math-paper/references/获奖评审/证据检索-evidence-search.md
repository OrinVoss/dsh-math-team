---
name: mathodology-evidence-search
description: Use when an award run needs external evidence — literature, datasets, benchmarks, domain constants, prior-art checks, or citation verification — with combined built-in WebSearch and search MCP discovery, source reconciliation, document reading, citation confirmation, token budgets, and reproducibility rules.
---

# Mathodology Evidence Search

Award submissions are scored on traceability: every constant, benchmark, dataset,
and domain claim must resolve to a source, a derivation, or an explicitly stated
assumption. This skill defines how Mathodology agents acquire and verify that
external evidence, so search work is repeatable instead of improvised per run.

## Tool Stack

The `search` MCP server ([free-search-mcp](https://github.com/sweetcornna/free-search-mcp))
complements built-in `WebSearch` as a peer discovery channel. Its tools appear as `mcp__search__<tool>`:

| Tool | Use it for |
|---|---|
| `search(query, ...filters)` | Source discovery. Multi-engine, RRF-merged, deduplicated link list. |
| `research(question, depth, ...filters)` | One open question you cannot yet phrase as a URL hunt: search + fetch top N + Markdown brief in one call. |
| `fetch(url, render?)` | Read one page as Markdown, or describe a non-text resource. |
| `fetch_batch(urls)` | Read up to 20 shortlisted URLs concurrently. |
| `read_doc(source, start?, length?)` | Read PDF / DOCX / XLSX / PPTX / EPUB / CSV / HTML with pagination — the correct tool for a paper PDF or a data file, not `fetch`. |
| `compare(question, urls=[2..5])` | Reconcile a constant or definition that two to five sources state differently. |
| `extract_structured(url)` | Pull JSON-LD / OpenGraph / microdata — DOI, authors, journal, volume, pages, date. The mechanical path to citation specifics. |
| `cache_search(query, limit?)` | Full-text search over pages already fetched in this run. Cheap; use before re-fetching. |
| `engines()` | Check which engines are available before blaming a query for thin results. |
| `download(url)` | Keep an actual file — a contest data attachment, a dataset archive, a PDF the coder must read. Staging only: see *Reproducibility Boundary*. |

A normal project installation exposes the full MCP list, including `download`.
Filters on `search` / `research`: `freshness` (`day`/`week`/`month`/`year`),
`include_domains`, `exclude_domains`, `category`, `include_text`, `exclude_text`.

## Availability And Explicit Degradation

Contract assertions:

- `dual-source-default: WebSearch + mcp__search__search`
- `single-source-mode: explicit degradation`
- `search_backend: combined`

A clone of this repository registers the server at project scope through its `.mcp.json`,
so the tools are normally present after the user approves the server once. They can still
be missing — a skills-only install into another project, a client that does not read
project MCP config, or a machine without `uv`. Inspect available tools once at the start of an evidence task and record one mode:

- `combined` — the default. Use both `WebSearch` and `mcp__search__search` for discovery.
- `search-mcp` — degraded mode when built-in `WebSearch` is unavailable.
- `builtin` — degraded mode when MCP discovery is unavailable.
- `none` — neither discovery channel is available; set the handoff status to `blocked`.

A `combined` run logs at least one query from each backend. Either single-source mode
requires a reason and its coverage loss under `missing_evidence`. Never silently
degrade or convert unavailable search into evidence of absence.

Treat MCP capabilities individually. If search works but `download` is absent,
continue discovery and reading, record a configuration degradation under
`missing_evidence`, and do not reconfigure MCP from an agent.

Registering it elsewhere with downloads enabled (no API key):

```bash
# Claude Code
claude mcp add --transport stdio --env "SEARCH_MCP_DOWNLOAD_DIR=$HOME/.cache/search-mcp/downloads" search -- uvx free-search-mcp

# Codex
codex mcp add --env "SEARCH_MCP_DOWNLOAD_DIR=$HOME/.cache/search-mcp/downloads" search -- uvx free-search-mcp
```

## Routing Rules

`category` routes the query to sources a general web engine cannot index. Pass it
instead of hand-listing engines:

- `paper` — arXiv, OpenAlex, Crossref, PubMed. Use for every literature,
  benchmark-method, and prior-art query. Hostname-filtering general web results is
  not a literature search.
- `dataset` — Zenodo, with DOIs. Replaces the default pool.
- `news` — Google News plus GDELT, for events, policy dates, and non-English coverage.
- `github` — repository metadata for reference implementations.
- `forum` — Stack Exchange and Hacker News, for accepted-answer signal on a method.
- `image` — openly-licensed images; results are direct file URLs. Replaces the default pool.

Naming `engines=[...]` explicitly disables this routing — do that only to reach a
specific opt-in engine (for example `google`, `wikipedia`, or the Chinese-language
engines for a CUMCM/华数杯 domain term).

## Search Protocol

Per evidence item in the source ledger:

1. Check the ledger and `cache_search` before fetching material already read.
2. In `combined` mode, run complementary queries through both built-in `WebSearch`
   and `mcp__search__search`; use the narrowest MCP `category` and filters. Do not
   wait for one channel to fail before using the other.
3. Log every query in `queries_run` with `backend: builtin` or `backend: search-mcp`.
4. Merge results before reading. Deduplicate by canonical DOI when available;
   otherwise canonicalize the URL by removing fragments and tracking parameters.
   Preserve every contributing channel in each accepted source's `discovered_by` list.
5. Shortlist by title, host, date, and claim fit — not rank alone. Prefer primary
   sources (publisher, standards body, statistical agency) over aggregators and blogs.
6. Choose one reader by resource type: `read_doc` for PDFs and data/office files;
   MCP `fetch`/`fetch_batch` or built-in `WebFetch` for pages. Discovery by both
   channels does not require duplicate fetches.
7. Use `compare` when sources disagree on a value you will print or model. Record
   the disagreement, chosen value, and reason.
8. Record canonical DOI/URL, original URL, `discovered_by`, date, access date,
   credibility note, and extracted quantity for every accepted source.

Thin or empty results are a diagnosis, not an answer. Check `engines()` and the
server's `rescued_via` note: a gated or CAPTCHA-walled engine looks identical to
"no such source exists" if you do not look. Report a blocked search as a gap in
`missing_evidence`; never convert it into an implicit claim that no evidence exists.

## Citation Verification Protocol

A citation is verified only when the URL resolves to the *primary* work being
cited — not a "cited-by" entry, not a neighbouring article in the same issue, not
a preprint of a paper you cite by its journal pagination.

1. Read the landing page or document once with the type-appropriate reader:
   `read_doc`, MCP `fetch`, or built-in `WebFetch`; confirm the title and authors.
2. When available, use `extract_structured` on the landing page to read DOI,
   journal, volume, issue, pages, and publication date from publisher metadata
   rather than from a search snippet; otherwise verify them on the publisher page.
3. Anything you cannot confirm down to the specifics the paper will print goes on
   `citations_to_verify` with `verified: false`. Do not print a page or volume
   number that no tool call confirmed.
4. `cache_search` makes this auditable: `mathodology-critic` can re-read the exact
   page the researcher saw, without re-fetching, when closing the citation gate.

## Reproducibility Boundary

Interactive search is not a reproducible pipeline stage.

- Evidence acquisition (this skill) produces a ledger of URLs, quotes, and values.
- Any number that enters the model or the paper must be re-derivable from a file
  under `work/<run-id>/` or a scripted download that `mathodology-coder` commits,
  not from an unrepeatable tool call.
- `download` writes to a **staging** directory that purges itself after 24 hours. It is
  the right tool when a real file is needed — contest attachments, dataset archives,
  a PDF the coder parses — and the wrong one for reading content, where `read_doc`
  and `fetch` touch no filesystem at all.
- Anything downloaded must be copied into `work/<run-id>/data/` in the same turn, and
  the ledger records its URL plus the SHA-256 the tool prints. A file left only in the
  staging directory is gone by the next day and the packager cannot account for it.
- The URL and hash are what make the download reproducible: a committed script can
  re-acquire the file and verify it is the same bytes the results were computed from.
- Respect licensing. Note license or usage constraints on any dataset in the ledger;
  a dataset that cannot be redistributed must not end up inside the submission package.

## Token Discipline

- Keep `format="markdown"` (default). Pass `format="json"` only when a script
  parses the output.
- `research(depth=N)` fetches N full documents — use it for a genuinely open
  question, not to read one URL you already have.
- Read the part of a long PDF you need with `read_doc(start=..., length=...)`
  instead of pulling the whole document into context.
- Cap breadth per claim: three to five accepted sources beat twenty skimmed ones,
  and the ledger stays reviewable.

## Who Uses This

- `mathodology-evidence-researcher` — primary owner, Phase 1 and every later
  evidence request.
- `mathodology-critic` — verification only against the researcher's ledger with
  its existing readers, metadata, and cache tools; it does not start a new discovery pass.
- `mathodology-award-judge` — **never**. Judge seats score the rendered PDF and the
  artifact list blind; external lookups break the blind protocol in
  `.claude/skills/mathodology-award-gates/SKILL.md`.

## Handoff Keys

The canonical role-specific contract lives in
`.claude/skills/mathodology-award-gates/SKILL.md`. Evidence work carries:

```yaml
search_backend: combined          # combined | search-mcp | builtin | none
queries_run: []                   # each includes {query, backend, category, engines_note, accepted, rejected}; backend: search-mcp | builtin
citations_to_verify: []           # each: {id, claim, source, url, verified}
missing_evidence: []              # blocked/gated/paywalled gaps and every backend/configuration degradation reason
```

Accepted sources are deduplicated by canonical DOI/URL and carry `discovered_by`.
`combined` requires both query backends; either single-source mode requires a
`missing_evidence` degradation reason; `none` requires a blocked handoff.
