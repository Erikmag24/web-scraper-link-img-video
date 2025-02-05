from serpapi import GoogleSearch
from typing import List, Dict, Set, Optional
import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
from urllib.parse import urlparse, urljoin
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import sys
import io

# Forza la codifica UTF-8 per stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Il resto del codice di serpapi_code.py rimane invariato ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchEngine(Enum):
    GOOGLE = "google"
    BING = "bing"
    BAIDU = "baidu"
    YANDEX = "yandex"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    NAVER = "naver"
    YELP = "yelp"

@dataclass
class SearchConfig:
    query: str
    num_links: int
    engines: List[SearchEngine]
    async_mode: bool = True
    api_key: str = ""

class LinkExtractor:
    def __init__(self, config: SearchConfig):
        self.config = config
        self.results: Dict[str, List[str]] = {}

    async def extract_links(self) -> Dict[str, List[str]]:
        """Main method to extract links based on configuration"""
        if self.config.async_mode:
            return await self._extract_links_async()
        return await self._extract_links_sync()

    async def _extract_links_async(self) -> Dict[str, List[str]]:
        """Extract links from all configured search engines asynchronously"""
        tasks = []
        for engine in self.config.engines:
            tasks.append(self._process_engine(engine))

        results = await asyncio.gather(*tasks)

        # Merge results from all engines
        all_results = {}
        for engine_results in results:
            all_results.update(engine_results)

        return all_results

    async def _extract_links_sync(self) -> Dict[str, List[str]]:
        """Extract links from all configured search engines synchronously"""
        all_results = {}

        for engine in self.config.engines:
            engine_results = await self._process_engine(engine)
            all_results.update(engine_results)

        return all_results

    async def _process_engine(self, engine: SearchEngine) -> Dict[str, List[str]]:
        """Process a single search engine with retries"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                results = await self._search_engine(engine)
                return {engine.value: results}
            except Exception as e:
                logger.error(f"Error processing {engine.value}: {str(e)}")
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"Max retries reached for {engine.value}")
                    return {engine.value: []}
                await asyncio.sleep(1)  # Wait before retry

    async def _search_engine(self, engine: SearchEngine) -> List[str]:
        """Perform search using specific engine"""
        params = self._get_engine_params(engine)

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            if "organic_results" in results:
                links = [result.get("link") for result in results["organic_results"]
                        if result.get("link")]
                return links[:self.config.num_links]  # Limit after fetching
            else:
                logger.warning(f"No organic results found for {engine.value}")
                return []

        except Exception as e:
            logger.error(f"Error searching {engine.value}: {str(e)}")
            raise

    def _get_engine_params(self, engine: SearchEngine) -> Dict:
        """Get parameters for specific search engine"""
        base_params = {
            "api_key": self.config.api_key
        }

        engine_specific_params = {
            SearchEngine.GOOGLE: {
                "engine": "google",
                "q": self.config.query,
                "num": self.config.num_links  # Specify number of results
            },
            SearchEngine.BING: {
                "engine": "bing",
                "q": self.config.query,
                "cc": "US",
                "count": self.config.num_links # Specify number of results
            },
            SearchEngine.BAIDU: {
                "engine": "baidu",
                "q": self.config.query,
                "rn": self.config.num_links # Specify number of results
            },
            SearchEngine.YANDEX: {
                "engine": "yandex",
                "text": self.config.query,
                "p": 0, # Start page
                "n": self.config.num_links # Specify number of results per page (adjust 'p' for more)
            },
            SearchEngine.YAHOO: {
                "engine": "yahoo",
                "p": self.config.query,
                "b": 1, # Start result
                "count": self.config.num_links # Specify number of results
            },
            SearchEngine.DUCKDUCKGO: {
                "engine": "duckduckgo",
                "q": self.config.query,
                "kl": "us-en",
                "t": "h_", # Type of search (web)
                "df": "y", # Do not filter
                "vnr": "1" # Show all results (may not be exact num_links)
            },
            SearchEngine.NAVER: {
                "engine": "naver",
                "query": self.config.query,
                "display": self.config.num_links # Specify number of results
            },
            SearchEngine.YELP: {
                "engine": "yelp",
                "find_desc": self.config.query,
                "find_loc": "United States",
                "attrs": "RestaurantsTakeOut", # Example attribute (can be removed)
                "sortby": "relevance",
                "size": self.config.num_links # Specify number of results (may have limits)
            }
        }

        return {**base_params, **engine_specific_params[engine]}

