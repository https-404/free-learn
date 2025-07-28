import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ResourceStorage:
    def __init__(self, topic: str, output_dir: str):
        self.storage_path = os.path.join(output_dir, f"{topic}.json")
        os.makedirs(output_dir, exist_ok=True)

    def save_resources(self, resources: List[Dict]):
        try:
            existing_data = []
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

            existing_data.extend(resources)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(resources)} new resources to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving resources: {e}")