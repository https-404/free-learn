import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class YouTubeConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.search_url = f"https://www.youtube.com/results?search_query={topic}"

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
                        for rank, result in enumerate(soup.select('a#video-title')[:self.limit], 1):
                            link = 'https://www.youtube.com' + result['href']
                            await queue.put((link, rank))
                    else:
                        logger.warning(f"YouTube search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in YouTube search: {e}")