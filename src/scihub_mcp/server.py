"""
Sci-Hub MCP Server

Provides tools for searching and downloading academic papers via Sci-Hub,
with metadata enrichment from CrossRef.
"""

import asyncio
import logging
from typing import Any

from fastmcp import FastMCP
from scihub_mcp.search import (
    download_paper,
    search_paper_by_doi,
    search_paper_by_title,
    search_papers_by_keyword,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

mcp = FastMCP("scihub")


@mcp.tool()
async def search_scihub_by_doi(doi: str) -> dict[str, Any]:
    """
    Search for a paper on Sci-Hub by DOI.

    Returns title, author, year, abstract, venue, pdf_url, mirror, and status.
    Status is 'success' or 'not_found'.

    Args:
        doi: Digital Object Identifier (e.g. '10.1038/nature09492')
    """
    logging.info(f"Searching by DOI: {doi}")
    try:
        return await asyncio.to_thread(search_paper_by_doi, doi)
    except Exception as e:
        return {"error": str(e), "status": "error"}


@mcp.tool()
async def search_scihub_by_title(title: str) -> dict[str, Any]:
    """
    Search for a paper on Sci-Hub by title.

    Resolves the title to a DOI via CrossRef, then retrieves from Sci-Hub.
    Returns title, author, year, abstract, venue, pdf_url, mirror, and status.

    Args:
        title: Full or partial paper title
    """
    logging.info(f"Searching by title: {title}")
    try:
        return await asyncio.to_thread(search_paper_by_title, title)
    except Exception as e:
        return {"error": str(e), "status": "error"}


@mcp.tool()
async def search_scihub_by_keyword(
    keyword: str, num_results: int = 10
) -> list[dict[str, Any]]:
    """
    Search for papers on Sci-Hub by keyword.

    Uses CrossRef for discovery, then retrieves available PDFs from Sci-Hub.
    Only returns papers successfully found on Sci-Hub mirrors.

    Args:
        keyword: Search term or phrase
        num_results: Maximum results to return (default 10)
    """
    logging.info(f"Searching by keyword: {keyword!r}, num_results={num_results}")
    try:
        return await asyncio.to_thread(search_papers_by_keyword, keyword, num_results)
    except Exception as e:
        return [{"error": str(e), "status": "error"}]


@mcp.tool()
async def download_scihub_pdf(pdf_url: str, output_path: str) -> str:
    """
    Download a PDF from Sci-Hub to a local file.

    Args:
        pdf_url: Direct PDF URL from a previous search result
        output_path: Local file path to save the PDF (include .pdf extension)
    """
    logging.info(f"Downloading PDF from {pdf_url} to {output_path}")
    try:
        success = await asyncio.to_thread(download_paper, pdf_url, output_path)
        if success:
            return f"PDF successfully downloaded to {output_path}"
        return f"Failed to download PDF from {pdf_url}"
    except Exception as e:
        return f"Download error: {str(e)}"


def main() -> None:
    logging.info("Starting Sci-Hub MCP Server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
