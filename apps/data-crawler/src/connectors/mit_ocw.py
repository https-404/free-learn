import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class MitOcwConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.search_url = f"https://ocw.mit.edu/search/?q={topic}"

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
                        # MIT OCW may load content via JavaScript, try regex extraction
                        import re
                        # Look for course links in various formats
                        course_links = re.findall(r'/courses/[^"\'<>\s)]+', html)
                        # Also try BeautifulSoup for any links
                        soup_links = soup.find_all('a', href=re.compile(r'/courses/'))
                        for link in soup_links:
                            href = link.get('href', '')
                            if '/courses/' in href:
                                course_links.append(href)

                        # Remove duplicates and normalize
                        unique_links = []
                        seen = set()
                        for link in course_links:
                            # Normalize link
                            if not link.startswith('http'):
                                link = 'https://ocw.mit.edu' + link
                            if link not in seen and '/courses/' in link:
                                unique_links.append(link)
                                seen.add(link)

                        count = 0
                        for rank, link in enumerate(unique_links[:self.limit], 1):
                            await queue.put((link, rank))
                            count += 1
                        if count == 0:
                            logger.warning(f"MIT OCW search found no results for query: {self.topic} (content may be loaded via JavaScript)")
                        else:
                            logger.info(f"MIT OCW search found {count} results")
                    else:
                        logger.warning(f"MIT OCW search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in MIT OCW search: {e}")
