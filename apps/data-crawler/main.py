import argparse
import asyncio
import logging
from src.crawler import ResourceCrawler
from src.config import configure_logging

def main():
    configure_logging()
    parser = argparse.ArgumentParser(description="Scalable web crawler for topic-based resource collection.")
    parser.add_argument('topic', type=str, help="Topic to search for")
    parser.add_argument('--limit', type=int, default=10, help="Maximum number of results to fetch")
    args = parser.parse_args()

    crawler = ResourceCrawler(args.topic, args.limit)
    asyncio.run(crawler.run())

if __name__ == '__main__':
    main()