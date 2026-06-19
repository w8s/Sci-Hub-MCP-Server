# AGENTS.md — scihub-mcp Developer Guide

Developer-facing documentation. For user-facing setup and usage, see [README.md](README.md).

## Architecture

```
src/scihub_mcp/
├── __init__.py   # Package version
├── server.py     # MCP tool definitions (FastMCP) — interface layer only
└── search.py     # CrossRef + Sci-Hub retrieval logic — no MCP dependencies
```

**Separation of concerns:** `server.py` owns the MCP interface; `search.py` owns all network logic. Tool handlers in `server.py` are thin wrappers: they call `asyncio.to_thread()` (since `search.py` is synchronous) and handle exceptions into structured error returns.

## Local Development

```bash
git clone https://github.com/w8s/scihub-mcp
cd scihub-mcp
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

Run server locally (stdio mode, for Claude Desktop):
```bash
python src/scihub_mcp/server.py
```

Or point Claude Desktop at your local venv:
```json
{
  "mcpServers": {
    "sci-hub": {
      "command": "/path/to/scihub-mcp/.venv/bin/python3",
      "args": ["/path/to/scihub-mcp/src/scihub_mcp/server.py"]
    }
  }
}
```

## Key Design Decisions

- **`asyncio.to_thread()`** — `search.py` uses synchronous `requests`; all MCP tools are async. `to_thread` bridges them without blocking the event loop.
- **Multi-mirror fallback** — mirrors are tried in order; first success wins. Mirror list is in `search.py`. If all fail, `status: not_found` is returned rather than raising.
- **CrossRef first** — DOI resolution and metadata always go through CrossRef. Sci-Hub is used only for PDF retrieval, not for discovery.
- **No `scihub` PyPI package** — the published `scihub` package on PyPI is broken/unmaintained. This server scrapes Sci-Hub mirrors directly with `requests` + `beautifulsoup4`.

## Adding a New Mirror

In `search.py`, find the `MIRRORS` list and append the new URL. No other changes needed.

## CI / Workflows

- **`ci.yml`** — runs on every push/PR to `main`; verifies the package installs cleanly and imports without error across Python 3.10–3.12.
- **`publish.yml`** — triggered by version tags (`0.x.y`). Builds and publishes to PyPI via Trusted Publishing, then creates a GitHub Release from `CHANGELOG.md`.

## Release Process

1. Update version in `pyproject.toml` and `src/scihub_mcp/__init__.py`
2. Add entry to `CHANGELOG.md`
3. Commit: `git commit -m "chore: bump version to X.Y.Z"`
4. Tag: `git tag X.Y.Z`
5. Push: `git push origin main --tags`
6. CI publishes to PyPI and creates the GitHub Release automatically

> **Note:** PyPI Trusted Publishing must be configured at pypi.org for the `scihub-mcp` project before the first publish. See [PyPI docs](https://docs.pypi.org/trusted-publishers/).

## Branch Strategy

- `main` — stable only; direct pushes for small fixes, feature branches for anything larger
- `feature/*` — new features, merged with `--no-ff`

## Known Limitations

- No test suite yet — the scraping logic is network-dependent and brittle to test without mocking. Adding `pytest` + `responses` mocking is a reasonable future investment.
- Mirror availability changes over time. If keyword searches return empty results, check mirror status manually.
