import logging
import os

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crawler.log'),
            logging.StreamHandler()
        ]
    )

CONFIG = {
    'output_dir': 'output',
    'download_delay': (1, 3),  # (min, max) seconds for throttling
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'retry_times': 3,
    'retry_http_codes': [429, 503, 504],
    'concurrent_requests': 16
}