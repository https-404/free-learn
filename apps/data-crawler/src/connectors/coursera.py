import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class CourseraConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.search_url = f"https://www.coursera.org/search?query={topic}&index=prod_all_products_term_optimization_free_courses"

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
                        # Try multiple selectors for Coursera
                        results = soup.select('a[data-click-key="search.search.click.search_card"]') or soup.select('a[href*="/learn/"]') or soup.select('div.card a[href*="/learn/"]')
                        count = 0
                        for rank, result in enumerate(results[:self.limit], 1):
                            link = result.get('href', '')
                            if link and '/learn/' in link:
                                if not link.startswith('http'):
                                    link = 'https://www.coursera.org' + link
                                await queue.put((link, rank))
                                count += 1
                        if count == 0:
                            logger.warning(f"Coursera search found no results for query: {self.topic}")
                        else:
                            logger.info(f"Coursera search found {count} results")
                    else:
                        logger.warning(f"Coursera search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in Coursera search: {e}")
