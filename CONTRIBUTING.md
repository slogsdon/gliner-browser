# Contributing

Bug reports, focused fixes, and improvements to the agent instructions are
welcome.

## Before opening a change

1. Check the existing issues and pull requests for related work.
2. Keep changes focused and include a local test when behavior changes.
3. Do not use live third-party websites in automated tests; use localhost pages.

## Set up and test

```sh
uv sync
uv run playwright install chromium
uv run python -m unittest discover -s tests -v
```

Natural-language resolver changes can also be checked against the configured
GLiNER2.5 model. That check may download model files on first use.

## Pull requests

Describe the behavior changed, the reason, and the checks you ran. Mention any
platform or model limitations that affect the change.
