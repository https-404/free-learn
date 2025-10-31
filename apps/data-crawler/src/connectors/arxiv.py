import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class ArxivConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        # Search for tutorials and educational materials, not research papers
        # Arxiv may not be the best source for learning materials, but we'll try to find tutorials
        educational_query = f"{topic} tutorial OR course OR guide OR introduction"
        self.search_url = f"https://arxiv.org/search/?query={educational_query}&searchtype=all"

    async def search(self, queue):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.search_url,
                    headers={'User-Agent': CONFIG['user_agent']},
                    timeout=10
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        for rank, result in enumerate(soup.select('p.list-title a[href]')[:self.limit], 1):
                            link = result['href']
                            await queue.put((link, rank))
                    else:
                        logger.warning(f"arXiv search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in arXiv search: {e}")
