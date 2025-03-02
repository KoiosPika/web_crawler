from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
import aiohttp
from urllib.parse import urljoin, urlparse
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    start_url: str
    max_depth: int

async def fetch_html(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            return await response.text()
    except:
        return None

async def bfs_crawl(start_url, max_depth):
    root_id = str(uuid.uuid4())
    queue = [(start_url, 0, root_id, None)]
    visited = set()
    results = []
    domain = urlparse(start_url).netloc
    domainSplit = domain.split('.')

    if len(domainSplit) == 2:
        domain = domainSplit[0]
    else:
        domain = domainSplit[1]

    async with aiohttp.ClientSession() as session:
        while queue:
            url, depth, node_id, parent_id = queue.pop(0)
            if url in visited or depth > max_depth:
                continue
            visited.add(url)

            html = await fetch_html(session, url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            links = []
            for a in soup.find_all('a', href=True):
                url = urljoin(url, a['href'])
                links.append(url)
            print(len(links))
            valid_links = []
            for link in links:
                parsed_link = urlparse(link)
                if parsed_link.scheme in ["http", "https"] and domain in parsed_link.netloc:
                    valid_links.append(link)

            valid_links = valid_links[:7]

            results.append({
                "id": node_id,
                "url": url,
                "title": title,
                "depth": depth,
                "parent_id": parent_id
            })

            for link in valid_links:
                if link not in visited:
                    child_id = str(uuid.uuid4())
                    queue.append((link, depth + 1, child_id, node_id))

    return results

@app.post("/crawl")
async def crawl_web(data: CrawlRequest):
    result = await bfs_crawl(data.start_url, data.max_depth)
    return {"crawled_pages": result}
