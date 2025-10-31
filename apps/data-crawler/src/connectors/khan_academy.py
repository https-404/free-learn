import aiohttp
import logging
from bs4 import BeautifulSoup
from src.config import CONFIG
from typing import List

logger = logging.getLogger(__name__)

class KhanAcademyConnector:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.search_url = f"https://www.khanacademy.org/search?query={topic}"

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
                        # Khan Academy loads content via JavaScript, try to extract from any available links
                        import re
                        # Look for Khan Academy links in the HTML
                        ka_links = re.findall(r'"(/computing/[^"]+)"|"(/programming/[^"]+)"|"(/a/[^"]+)"', html)
                        flat_links = [link for group in ka_links for link in group if link]
                        # Also try BeautifulSoup
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            href = link.get('href', '')
                            if href and ('computing' in href or 'programming' in href or '/a/' in href):
                                flat_links.append(href)

                        unique_links = list(dict.fromkeys(flat_links))  # Remove duplicates
                        count = 0
                        for rank, link in enumerate(unique_links[:self.limit], 1):
                            if not link.startswith('http'):
                                link = 'https://www.khanacademy.org' + link
                            await queue.put((link, rank))
                            count += 1
                        if count == 0:
                            logger.warning(f"Khan Academy search found no results for query: {self.topic} (content may be loaded via JavaScript)")
                        else:
                            logger.info(f"Khan Academy search found {count} results")
                    else:
                        logger.warning(f"Khan Academy search failed: Status {response.status}")
        except Exception as e:
            logger.error(f"Error in Khan Academy search: {e}")
