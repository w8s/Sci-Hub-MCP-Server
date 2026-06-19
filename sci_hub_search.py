import re
import os
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCIHUB_MIRRORS = [
    'https://sci-hub.hkvisa.net',
    'https://sci-hub.mksa.top',
    'https://sci-hub.ren',
    'https://sci-hub.se',
    'https://sci-hub.st',
    'https://sci-hub.ee',
]

def _create_session():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    return session

def _extract_pdf_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    # 1. iframe src
    iframe = soup.find('iframe')
    if iframe and iframe.get('src') and '.pdf' in iframe['src']:
        return iframe['src'].split('#')[0]
    # 2. embed src
    embed = soup.find('embed')
    if embed and embed.get('src') and '.pdf' in embed['src']:
        return embed['src'].split('#')[0]
    # 3. onclick with download link
    for tag in soup.find_all(attrs={'onclick': True}):
        m = re.search(r"location\.href=['\"]([^'\"]+\.pdf[^'\"]*)['\"]", tag['onclick'].replace('\\/', '/'))
        if m:
            return m.group(1).split('#')[0]
    # 4. regex fallback
    for match in re.findall(r'((?:https?:)?//[^\s"\'<>]+\.pdf)', html):
        url = match if match.startswith('http') else 'https:' + match
        return url.split('#')[0]
    return None

def _fetch_from_scihub(identifier):
    session = _create_session()
    for mirror in SCIHUB_MIRRORS:
        try:
            url = f'{mirror}/{identifier}'
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 1000:
                pdf_url = _extract_pdf_url(r.text)
                if pdf_url:
                    return pdf_url, mirror
        except Exception:
            continue
    return None, None

def search_paper_by_doi(doi):
    pdf_url, mirror = _fetch_from_scihub(doi)
    if pdf_url:
        return {
            'doi': doi,
            'pdf_url': pdf_url,
            'status': 'success',
            'mirror': mirror,
            'title': '',
            'author': '',
            'year': ''
        }
    return {'doi': doi, 'status': 'not_found'}

def search_paper_by_title(title):
    try:
        url = f"https://api.crossref.org/works?query.title={title}&rows=1"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if data['message']['items']:
                doi = data['message']['items'][0]['DOI']
                return search_paper_by_doi(doi)
    except Exception as e:
        print(f"CrossRef search error: {e}")
    return {'title': title, 'status': 'not_found'}

def search_papers_by_keyword(keyword, num_results=10):
    papers = []
    try:
        url = f"https://api.crossref.org/works?query={keyword}&rows={num_results}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for item in data['message']['items']:
                doi = item.get('DOI')
                if doi:
                    result = search_paper_by_doi(doi)
                    if result['status'] == 'success':
                        papers.append(result)
    except Exception as e:
        print(f"Search error: {e}")
    return papers

def download_paper(pdf_url, output_path):
    session = _create_session()
    try:
        if '?download=true' not in pdf_url:
            download_url = pdf_url + '?download=true'
        else:
            download_url = pdf_url
        r = session.get(download_url, timeout=60, stream=True)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Download error: {e}")
    return False
