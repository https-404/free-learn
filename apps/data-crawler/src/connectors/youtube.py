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
        # Enhance query with educational keywords
        educational_query = f"{topic} tutorial course learn"
        self.search_url = f"https://www.youtube.com/results?search_query={educational_query}"

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
                        # YouTube embeds video IDs in the HTML, extract using regex
                        import re
                        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
                        unique_ids = list(dict.fromkeys(video_ids))  # Remove duplicates while preserving order
                        count = 0
                        for rank, video_id in enumerate(unique_ids[:self.limit], 1):
                            link = f'https://www.youtube.com/watch?v={video_id}'
                            await queue.put((link, rank))
                            count += 1
                        if count == 0:
                            logger.warning(f"YouTube search found no results for query: {self.topic}")
                        else:
                            logger.info(f"YouTube search found {count} results")
                    else:
                        logger.warning(f"YouTube search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in YouTube search: {e}")
