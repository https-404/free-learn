import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class GoogleConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        # Enhance query with educational keywords
        educational_query = f"{topic} tutorial course learn lesson guide"
        self.search_url = f"https://www.google.com/search?q={educational_query}"

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
                        # Try multiple selectors for Google search results
                        results = soup.select('div.g a[href]') or soup.select('a[href^="http"]') or soup.select('div.yuRUbf a')
                        count = 0
                        for rank, result in enumerate(results[:self.limit], 1):
                            link = result.get('href', '')
                            # Filter out Google's own pages
                            if link.startswith('http') and 'google.com' not in link:
                                await queue.put((link, rank))
                                count += 1
                        if count == 0:
                            logger.warning(f"Google search found no results for query: {self.topic}")
                        else:
                            logger.info(f"Google search found {count} results")
                    else:
                        logger.warning(f"Google search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
