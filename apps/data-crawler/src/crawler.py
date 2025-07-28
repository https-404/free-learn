import asyncio
import logging
from typing import List
from src.connectors.google import GoogleConnector
from src.connectors.youtube import YouTubeConnector
from src.connectors.arxiv import ArxivConnector
from src.connectors.udemy import UdemyConnector
from src.connectors.coursera import CourseraConnector
from src.connectors.edx import EdxConnector
from src.connectors.khan_academy import KhanAcademyConnector
from src.connectors.harvard_online import HarvardOnlineConnector
from src.connectors.mit_ocw import MitOcwConnector
from src.scraper import ResourceScraper
from src.deduplicator import Deduplicator
from src.storage import ResourceStorage
from src.config import CONFIG

logger = logging.getLogger(__name__)

class ResourceCrawler:
    def __init__(self, topic: str, limit: int):
        self.topic = topic
        self.limit = limit
        self.deduplicator = Deduplicator(topic, CONFIG['output_dir'])
        self.storage = ResourceStorage(topic, CONFIG['output_dir'])
        self.scraper = ResourceScraper(topic, limit, self.deduplicator)
        self.connectors = [
            GoogleConnector(topic, limit),
            YouTubeConnector(topic, limit),
            ArxivConnector(topic, limit),
            UdemyConnector(topic, limit),
            CourseraConnector(topic, limit),
            EdxConnector(topic, limit),
            KhanAcademyConnector(topic, limit),
            HarvardOnlineConnector(topic, limit),
            MitOcwConnector(topic, limit)
        ]
        self.queue = asyncio.Queue()

    async def run(self):
        tasks = [connector.search(self.queue) for connector in self.connectors]
        await asyncio.gather(*tasks)
        
        collected_items = []
        while not self.queue.empty() and len(collected_items) < self.limit:
            item = await self.queue.get()
            url, rank = item if isinstance(item, tuple) else (item, None)
            resource = await self.scraper.scrape_resource(url, rank)
            if resource and not self.deduplicator.is_duplicate(resource):
                self.deduplicator.add_hash(resource)
                collected_items.append(resource)
        
        if collected_items:
            self.storage.save_resources(collected_items)
        logger.info(f"Crawling complete. Collected {len(collected_items)} items.")