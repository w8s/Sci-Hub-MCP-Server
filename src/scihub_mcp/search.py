"""
Sci-Hub search and download utilities.

Uses CrossRef for metadata lookup and Sci-Hub mirrors for PDF retrieval.
"""

import re
import os
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCIHUB_MIRRORS = [
    "https://sci-hub.hkvisa.net",
    "https://sci-hub.mksa.top",
    "https://sci-hub.ren",
    "https://sci-hub.se",
    "https://sci-hub.st",
    "https://sci-hub.ee",
]


def _create_session() -> requests.Session:
    session = requests.Session()
    session.verify = False
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    return session


def _extract_pdf_url(html: str) -> str | None:
    """Extract PDF URL from Sci-Hub HTML response."""
    soup = BeautifulSoup(html, "html.parser")

    iframe = soup.find("iframe")
    if iframe and iframe.get("src") and ".pdf" in iframe["src"]:
        return iframe["src"].split("#")[0]

    embed = soup.find("embed")
    if embed and embed.get("src") and ".pdf" in embed["src"]:
        return embed["src"].split("#")[0]

    for tag in soup.find_all(attrs={"onclick": True}):
        m = re.search(
            r"location\.href=['\"]([^'\"]+\.pdf[^'\"]*)['\"]",
            tag["onclick"].replace("\\/", "/"),
        )
        if m:
            return m.group(1).split("#")[0]

    for match in re.findall(r'((?:https?:)?//[^\s"\'<>]+\.pdf)', html):
        url = match if match.startswith("http") else "https:" + match
        return url.split("#")[0]

    return None


def _fetch_from_scihub(identifier: str) -> tuple[str | None, str | None]:
    """Try each Sci-Hub mirror and return (pdf_url, mirror) on first success."""
    session = _create_session()
    for mirror in SCIHUB_MIRRORS:
        try:
            url = f"{mirror}/{identifier}"
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 1000:
                pdf_url = _extract_pdf_url(r.text)
                if pdf_url:
                    return pdf_url, mirror
        except Exception:
            continue
    return None, None


def _fetch_crossref_metadata(doi: str) -> dict:
    """Fetch paper metadata from CrossRef API by DOI."""
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}",
            timeout=15,
        )
        if r.status_code != 200:
            return {}

        item = r.json().get("message", {})
        authors = item.get("author", [])
        author_str = ", ".join(
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in authors[:3]
        )
        if len(authors) > 3:
            author_str += " et al."

        date_parts = item.get("published", {}).get("date-parts", [[""]])
        year = str(date_parts[0][0]) if date_parts and date_parts[0] else ""

        abstract = item.get("abstract", "")
        # CrossRef abstracts often include JATS XML tags — strip them
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        return {
            "title": item.get("title", [""])[0],
            "author": author_str,
            "year": year,
            "abstract": abstract,
            "venue": item.get("container-title", [""])[0],
        }
    except Exception:
        return {}


def search_paper_by_doi(doi: str) -> dict:
    """
    Search for a paper by DOI and return metadata + Sci-Hub PDF link.

    Returns a dict with keys: doi, title, author, year, abstract, venue,
    pdf_url, mirror, status. Status is 'success' or 'not_found'.
    """
    pdf_url, mirror = _fetch_from_scihub(doi)
    if not pdf_url:
        return {"doi": doi, "status": "not_found"}

    metadata = _fetch_crossref_metadata(doi)
    return {
        "doi": doi,
        "pdf_url": pdf_url,
        "mirror": mirror,
        "status": "success",
        **metadata,
    }


def search_paper_by_title(title: str) -> dict:
    """
    Search for a paper by title using CrossRef, then retrieve from Sci-Hub.

    Returns same structure as search_paper_by_doi, or status 'not_found'.
    """
    try:
        r = requests.get(
            "https://api.crossref.org/works",
            params={"query.title": title, "rows": 1},
            timeout=15,
        )
        if r.status_code == 200:
            items = r.json().get("message", {}).get("items", [])
            if items:
                doi = items[0].get("DOI")
                if doi:
                    return search_paper_by_doi(doi)
    except Exception:
        pass
    return {"title": title, "status": "not_found"}


def search_papers_by_keyword(keyword: str, num_results: int = 10) -> list[dict]:
    """
    Search for papers by keyword using CrossRef, then retrieve PDFs from Sci-Hub.

    Returns a list of paper dicts (same structure as search_paper_by_doi).
    Only papers successfully found on Sci-Hub are included.
    """
    papers = []
    try:
        r = requests.get(
            "https://api.crossref.org/works",
            params={"query": keyword, "rows": num_results},
            timeout=15,
        )
        if r.status_code != 200:
            return papers

        for item in r.json().get("message", {}).get("items", []):
            doi = item.get("DOI")
            if not doi:
                continue

            result = search_paper_by_doi(doi)
            if result.get("status") != "success":
                continue

            # Fill any missing metadata from the CrossRef search result we already have
            if not result.get("title"):
                result["title"] = item.get("title", [""])[0]
            if not result.get("year"):
                parts = item.get("published", {}).get("date-parts", [[""]])
                result["year"] = str(parts[0][0]) if parts and parts[0] else ""
            if not result.get("author"):
                authors = item.get("author", [])
                result["author"] = ", ".join(
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in authors[:3]
                )
                if len(authors) > 3:
                    result["author"] += " et al."

            papers.append(result)

    except Exception as e:
        return [{"error": str(e), "status": "error"}]

    return papers


def download_paper(pdf_url: str, output_path: str) -> bool:
    """
    Download a PDF from a Sci-Hub URL to a local file path.

    Returns True on success, False on failure.
    """
    session = _create_session()
    try:
        download_url = pdf_url if "?download=true" in pdf_url else pdf_url + "?download=true"
        r = session.get(download_url, timeout=60, stream=True)
        if r.status_code == 200:
            os.makedirs(
                os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
                exist_ok=True,
            )
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception:
        pass
    return False
