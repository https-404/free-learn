import aiohttp
import logging
from urllib.parse import urlparse
from datetime import datetime
from newspaper import Article
import yt_dlp
import pdfplumber
from src.tagger import ResourceTagger
from src.deduplicator import Deduplicator
from src.config import CONFIG
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ResourceScraper:
    def __init__(self, topic: str, limit: int, deduplicator: Deduplicator):
        self.topic = topic
        self.limit = limit
        self.tagger = ResourceTagger()
        self.deduplicator = deduplicator
        self.trusted_domains = {
            'wikipedia.org': 0.9,
            'stackoverflow.com': 0.85,
            'arxiv.org': 0.8,
            'udemy.com': 0.75,
            'coursera.org': 0.75,
            'edx.org': 0.75,
            'khanacademy.org': 0.75,
            'harvardonline.harvard.edu': 0.85,
            'ocw.mit.edu': 0.85
        }

    async def fetch_page(self, url: str) -> Optional[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={'User-Agent': CONFIG['user_agent']},
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Failed to fetch {url}: Status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def fetch_pdf(self, url: str) -> Optional[bytes]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={'User-Agent': CONFIG['user_agent']},
                    timeout=10
                ) as response:
                    if response.status == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                        return await response.read()
                    else:
                        logger.warning(f"Failed to fetch PDF {url}: Status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching PDF {url}: {e}")
            return None

    def normalize_score(self, value: float, max_value: float, weight: float = 1.0) -> float:
        try:
            return min(100.0, (value / max_value) * 100 * weight)
        except ZeroDivisionError:
            return 0.0

    async def scrape_resource(self, url: str, search_rank: int = None) -> Optional[Dict]:
        try:
            domain = urlparse(url).netloc
            content_type = self.detect_content_type(url)
            html = await self.fetch_page(url)
            is_free = await self.detect_free_access(url, html, content_type)
            rating_score = await self.compute_rating_score(url, html, content_type, search_rank)

            item = {
                'content_link': url,
                'website_name': domain,
                'title': '',
                'description': '',
                'content': '',
                'content_type': content_type,
                'tags': [],
                'field_related_to': self.topic,
                'timestamp': datetime.utcnow().isoformat(),
                'hash': '',
                'free_access': is_free,
                'rating_score': rating_score
            }

            if content_type == 'article':
                article = Article(url)
                try:
                    article.download()
                    article.parse()
                    article.nlp()
                    item['title'] = article.title or 'No title'
                    item['description'] = article.meta_description or article.summary or ''
                    item['content'] = article.text[:2000] or ''
                    item['tags'] = self.tagger.generate_tags(item['content'] + ' ' + item['title'])
                except Exception as e:
                    logger.warning(f"Failed to parse article {url}: {e}")
                    if html:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html, 'html.parser')
                        item['title'] = soup.title.string if soup.title else 'No title'
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        item['description'] = meta_desc['content'] if meta_desc else ''
                        item['content'] = ' '.join(p.get_text() for p in soup.select('p')[:5])[:2000]

            elif content_type == 'video':
                ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        item['title'] = info.get('title', 'No title')
                        item['description'] = info.get('description', '')[:500]
                        item['content'] = info.get('description', '')[:2000]
                        item['tags'] = self.tagger.generate_tags(item['content'] + ' ' + item['title'])
                    except Exception as e:
                        logger.warning(f"Failed to parse video {url}: {e}")
                        item['title'] = 'No title'

            elif content_type == 'pdf':
                pdf_data = await self.fetch_pdf(url)
                if pdf_data:
                    try:
                        with pdfplumber.open(pdf_data) as pdf:
                            text = ''
                            for page in pdf.pages[:2]:
                                text += page.extract_text() or ''
                            item['content'] = text[:2000]
                            item['title'] = pdf.metadata.get('Title', 'No title')
                            item['description'] = pdf.metadata.get('Subject', '')[:500]
                            item['tags'] = self.tagger.generate_tags(item['content'] + ' ' + item['title'])
                    except Exception as e:
                        logger.warning(f"Failed to parse PDF {url}: {e}")
                if html:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    item['title'] = soup.title.string if soup.title else 'No title'
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    item['description'] = meta_desc['content'] if meta_desc else ''

            elif content_type == 'course':
                if html:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    item['title'] = soup.title.string if soup.title else 'No title'
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    item['description'] = meta_desc['content'] if meta_desc else ''
                    content_elems = soup.select('div.course-description, div.about, p, div.overview')
                    item['content'] = ' '.join(elem.get_text() for elem in content_elems)[:2000]
                    item['tags'] = self.tagger.generate_tags(item['content'] + ' ' + item['title'])

            item['hash'] = self.deduplicator.generate_hash(item)
            return item
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def detect_content_type(self, url: str) -> str:
        if url.endswith('.pdf'):
            return 'pdf'
        elif 'youtube.com' in url or 'vimeo.com' in url:
            return 'video'
        elif any(d in url for d in ['udemy.com', 'coursera.org', 'edx.org', 'khanacademy.org', 'harvardonline.harvard.edu', 'ocw.mit.edu']):
            return 'course'
        else:
            return 'article'

    def detect_free_access(self, url: str, html: Optional[str], content_type: str) -> bool:
        if not html:
            return False
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            if 'udemy.com' in url:
                return bool(soup.find(text=lambda t: 'Free' in t))
            elif 'coursera.org' in url:
                return bool(soup.find(text=lambda t: 'Enroll for Free' in t))
            elif 'edx.org' in url:
                return bool(soup.find(text=lambda t: 'Free' in t or 'Audit this course' in t))
            elif 'khanacademy.org' in url or 'harvardonline.harvard.edu' in url or 'ocw.mit.edu' in url:
                return True
            elif content_type == 'video' and 'youtube.com' in url:
                return True
            elif content_type == 'pdf' and 'arxiv.org' in url:
                return True
            return False
        except Exception as e:
            logger.warning(f"Error detecting free access for {url}: {e}")
            return False

    def compute_rating_score(self, url: str, html: Optional[str], content_type: str, search_rank: Optional[int]) -> float:
        try:
            domain = urlparse(url).netloc
            if content_type == 'course' and 'udemy.com' in url and html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                rating_elem = soup.select_one('span[data-purpose="rating-number"]')
                reviews_elem = soup.select_one('span[data-purpose="enrollment"]')
                rating = float(rating_elem.text) if rating_elem else 0.0
                reviews = int(reviews_elem.text.split()[0]) if reviews_elem else 0
                return self.normalize_score(rating * reviews, max_value=5.0 * 1000, weight=0.8)

            elif content_type == 'course' and any(d in url for d in ['coursera.org', 'edx.org', 'harvardonline.harvard.edu']) and html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                rating_elem = soup.select_one('span[data-test="ratings-count-text"], span.rating')
                rating = float(rating_elem.text.split()[0]) if rating_elem and rating_elem.text.split()[0].replace('.', '').isdigit() else 0.0
                return self.normalize_score(rating, max_value=5.0, weight=0.8)

            elif content_type == 'course' and any(d in url for d in ['khanacademy.org', 'ocw.mit.edu']):
                return self.normalize_score(1.0 / (search_rank or 10), max_value=0.1, weight=0.7)

            elif content_type == 'video' and 'youtube.com' in url:
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    views = info.get('view_count', 0)
                    likes = info.get('like_count', 0)
                    return self.normalize_score(views + likes * 10, max_value=1000000, weight=0.7)

            elif content_type == 'pdf' and 'arxiv.org' in url:
                return self.normalize_score(1.0 / (search_rank or 10), max_value=0.1, weight=0.6)

            elif content_type == 'article' and search_rank:
                domain_score = self.trusted_domains.get(domain, 0.5)
                rank_score = 1.0 / (search_rank or 10)
                return self.normalize_score(rank_score, max_value=0.1, weight=domain_score)

            return 0.0
        except Exception as e:
            logger.warning(f"Error computing rating score for {url}: {e}")
            return 0.0