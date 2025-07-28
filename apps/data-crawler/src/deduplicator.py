import hashlib
import json
import os
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self, topic: str, output_dir: str):
        self.storage_path = os.path.join(output_dir, f"{topic}.json")
        self.existing_hashes = self.load_existing_hashes()

    def load_existing_hashes(self) -> Set[str]:
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {item['hash'] for item in data}
            return set()
        except Exception as e:
            logger.error(f"Error loading existing hashes: {e}")
            return set()

    def generate_hash(self, item: Dict) -> str:
        unique_string = f"{item['content_link']}{item['title']}"
        return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

    def is_duplicate(self, item: Dict) -> bool:
        item_hash = self.generate_hash(item)
        return item_hash in self.existing_hashes

    def add_hash(self, item: Dict):
        item_hash = self.generate_hash(item)
        self.existing_hashes.add(item_hash)