import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class EdxConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.search_url = f"https://www.edx.org/search?q={topic}&cost=Free"

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
                        # edX uses Next.js, extract course links from hrefs
                        # Look for links with /learn/ pattern
                        import re
                        course_links = re.findall(r'/learn/[^"\'<>\s)]+', html)
                        # Also try BeautifulSoup for links
                        soup_links = soup.find_all('a', href=re.compile(r'/learn/'))
                        for link in soup_links:
                            href = link.get('href', '')
                            if '/learn/' in href:
                                course_links.append(href)

                        # Remove duplicates and filter
                        unique_links = []
                        seen = set()
                        for link in course_links:
                            # Skip image links
                            if '/course/image/' in link or link.endswith('.png') or link.endswith('.jpg'):
                                continue
                            # Normalize link
                            if not link.startswith('http'):
                                link = 'https://www.edx.org' + link
                            if link not in seen and '/learn/' in link:
                                unique_links.append(link)
                                seen.add(link)

                        count = 0
                        for rank, link in enumerate(unique_links[:self.limit], 1):
                            await queue.put((link, rank))
                            count += 1
                        if count == 0:
                            logger.warning(f"edX search found no results for query: {self.topic}")
                        else:
                            logger.info(f"edX search found {count} results")
                    else:
                        logger.warning(f"edX search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in edX search: {e}")
