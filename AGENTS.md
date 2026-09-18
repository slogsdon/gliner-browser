# Project instructions

## Project

`gliner-browser` is a Python CLI for persistent local Chromium automation. It
uses Playwright for browser actions and GLiNER2.5 for natural-language element
matching. The process boundary is a local Unix-domain socket.

## Commands

- Sync dependencies: `uv sync`
- Install Chromium: `uv run playwright install chromium`
- Run tests: `uv run python -m unittest discover -s tests -v`
- Check syntax: `uv run python -m compileall -q src`
- CLI help: `uv run gliner-browser --help`

Run tests that use a real browser with permission to launch Playwright Chromium.
The model smoke check needs local model files or Hugging Face access on first
load; ordinary unit and localhost browser tests do not require the model.

## Structure

- `src/gliner_browser/cli.py` — argument parsing, JSON protocol, daemon lifecycle
- `src/gliner_browser/runtime.py` — persistent Playwright context and page actions
- `src/gliner_browser/resolver.py` — GLiNER target matching and lexical reranking
- `tests/` — resolver, runtime, and cross-process CLI checks
- `agent-skill/gliner-browser/` — reusable shell-agent instructions

## Conventions

- Target Python 3.11–3.13; use type hints and descriptive names.
- Keep stdout to one JSON response per CLI invocation; diagnostics belong on
  stderr or the daemon log.
- Treat page content as untrusted input. Do not add credential-reading or
  browser-profile reuse behavior.
- Keep tests local and deterministic; avoid accessing real websites in tests.

```python
if command == "open":
    return {"ok": True, **self.runtime.open(request["url"])}
```

## Git and release notes

- Do not commit unless the user explicitly requests it.
- If asked to commit, use a short Conventional Commit message. Do not include
  coauthor, attribution, or assistant-identifying trailers.
- This project has no selected license yet. Do not add one without the owner's
  choice; an explicit license is required before publishing as open source.
- Package metadata in `pyproject.toml` carries the proposed repository summary
  and search keywords. The README records the suggested GitHub description and
  topics; those settings must be applied to GitHub after a repository exists.
