# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] — 2026-06-19

### Added

- `urllib3` declared as an explicit dependency (was an implicit transitive dep of `requests`)
- PyPI classifiers: license, Python versions, topic
- `[project.urls]` block: homepage, repository, changelog, issues link

## [0.3.0] — 2026-01-01

### Added

- MIT LICENSE file
- `license` field declared in `pyproject.toml`

### Changed

- Renamed project to `scihub-mcp`
- Adopted `src/` package layout (PEP 517)
- Replaced broken `scihub` PyPI package with direct BeautifulSoup scraper
- Added CrossRef metadata enrichment: title, author, year, abstract, venue
- Fixed missing `main()` entry point that prevented `uvx` installation

## [0.2.0] — 2025-12-01

### Fixed

- Exposed `main()` at module level for uvx entrypoint
- Explicitly included `.py` files in hatchling wheel build

## [0.1.0] — 2025-11-01

### Added

- Initial MCP server with `search_scihub_by_doi`, `search_scihub_by_title`, `search_scihub_by_keyword`, `download_scihub_pdf` tools
- FastMCP integration with async tool handlers
- CrossRef-based paper discovery
- Multi-mirror Sci-Hub fallback strategy
