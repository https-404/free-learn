from keybert import KeyBERT
import logging
from typing import List

logger = logging.getLogger(__name__)

class ResourceTagger:
    def __init__(self):
        self.kw_model = KeyBERT()

    def generate_tags(self, text: str, top_n: int = 5) -> List[str]:
        try:
            keywords = self.kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n
            )
            return [keyword[0] for keyword in keywords]
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return []