# scihub-mcp

MCP server for searching and downloading academic papers via Sci-Hub, with metadata enrichment from CrossRef.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/github/license/w8s/scihub-mcp)

## Features

- 🔍 **Search by keyword, title, or DOI** — powered by CrossRef discovery
- 📋 **Rich metadata** — title, authors, year, abstract, and venue returned automatically
- 📄 **PDF retrieval** — fetches available PDFs across multiple Sci-Hub mirrors
- ⚡ **Async throughout** — non-blocking tool calls via FastMCP
- 🧩 **Clean package structure** — `src/` layout, PEP 8 compliant, no legacy cruft

## Quick Start

```bash
# Install via uvx (recommended)
uvx --from git+https://github.com/w8s/scihub-mcp scihub-mcp
```

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sci-hub": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/w8s/scihub-mcp",
        "scihub-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop. The following tools will be available:

- `search_scihub_by_keyword` — find papers by topic
- `search_scihub_by_title` — resolve a title to a PDF
- `search_scihub_by_doi` — look up a specific paper
- `download_scihub_pdf` — save a PDF to disk

## Installation

### Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) or `pip`
- Claude Desktop (or any MCP-compatible client)

### Via uvx (recommended — no local install needed)

```bash
uvx --from git+https://github.com/w8s/scihub-mcp scihub-mcp
```

### Via pip (local install)

```bash
pip install git+https://github.com/w8s/scihub-mcp
```

### Local development

```bash
git clone https://github.com/w8s/scihub-mcp
cd scihub-mcp
uv venv --python 3.12
uv pip install -e . --only-binary cryptography
```

Point your Claude Desktop config at the local server:

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

## Usage

### Search by keyword

```
search_scihub_by_keyword("dopamine ADHD executive function", num_results=5)
```

Returns: list of papers with `title`, `author`, `year`, `abstract`, `venue`, `doi`, `pdf_url`, `mirror`, `status`.

### Search by title

```
search_scihub_by_title("Attention and Effort")
```

Resolves the title via CrossRef, then retrieves from Sci-Hub. Returns same fields as keyword search.

### Search by DOI

```
search_scihub_by_doi("10.1038/nature09492")
```

Direct lookup. Fastest when you already have the DOI.

### Download a PDF

```
download_scihub_pdf(
  pdf_url="https://sci.bban.top/pdf/10.1038/nature09492.pdf",
  output_path="/Users/you/papers/nature09492.pdf"
)
```

`pdf_url` comes from any of the search tools above.

## Configuration

No environment variables required. The server uses public CrossRef and Sci-Hub mirror endpoints by default.

**Sci-Hub mirrors** (tried in order, first success wins):

```
https://sci-hub.hkvisa.net
https://sci-hub.mksa.top
https://sci-hub.ren
https://sci-hub.se
https://sci-hub.st
https://sci-hub.ee
```

Mirror availability varies. If searches return empty results, the DOI may not be available on current mirrors — try a different paper or check mirror status manually.

## Project Structure

```
scihub-mcp/
├── src/
│   └── scihub_mcp/
│       ├── __init__.py   # version
│       ├── server.py     # MCP tool definitions (FastMCP)
│       └── search.py     # CrossRef + Sci-Hub retrieval logic
├── pyproject.toml
└── README.md
```

## Limitations

- **Coverage**: Sci-Hub mirrors do not host every paper. Older, highly-cited papers have the best availability.
- **Abstracts**: CrossRef does not provide abstracts for all records. Newer structured metadata is more complete.
- **Mirror stability**: Sci-Hub mirrors change over time. If all mirrors fail, the tool returns `status: not_found`.
- **Legal**: Access to Sci-Hub may be restricted or illegal in some jurisdictions. Use responsibly and in accordance with local law.

## Contributing

Issues and PRs welcome. Please:

1. Follow the existing code style (`src/` layout, PEP 8, double quotes, type hints)
2. Keep `search.py` and `server.py` separated — logic vs. MCP interface
3. Test against at least one known-good DOI before submitting

## Acknowledgments

Inspired by and forked from:

- [JackKuo666/Sci-Hub-MCP-Server](https://github.com/JackKuo666/Sci-Hub-MCP-Server) — original MCP server concept
- [JackKuo666/Sci-Hub-MCP-Server](https://github.com/JackKuo666/Sci-Hub-MCP-Server) (alternate fork) — additional reference

This version rewrites the metadata layer, adds CrossRef enrichment (title, author, year, abstract, venue), adopts a `src/` package structure, removes unused dependencies, and fixes the missing `main()` entry point that prevented uvx installation.

## License

MIT
