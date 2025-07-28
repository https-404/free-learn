import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class HarvardOnlineConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.search_url = f"https://www.harvardonline.harvard.edu/search?query={topic}"

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
                        for rank, result in enumerate(soup.select('a.course-card')[:self.limit], 1):
                            link = result['href']
                            if not link.startswith('http'):
                                link = 'https://www.harvardonline.harvard.edu' + link
                            await queue.put((link, rank))
                    else:
                        logger.warning(f"Harvard Online search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in Harvard Online search: {e}")