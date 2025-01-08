from typing import List, Dict, Tuple
from serpapi import GoogleSearch
import os
from bs4 import BeautifulSoup
from rake_nltk import Rake
from markdownify import markdownify as md
import requests
import concurrent.futures
from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor


class SEOTools:
    def __init__(self):
        self.serp_api_key = os.getenv("SERPAPI_API_KEY")
        # Initialize text compressor
        self.compressor = TextMessageCompressor(text_compressor=LLMLingua())

    def get_autocomplete_suggestions(self, query: str) -> List[str]:
        """Get autocomplete suggestions for a query"""
        params = {
            "q": query,
            "api_key": self.serp_api_key,
            "engine": "google_autocomplete",
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract suggestions
        suggestions = []
        if "suggestions" in results:
            suggestions = [item["value"] for item in results["suggestions"]]

        return suggestions

    def analyze_competition(self, topic: str) -> Dict:
        """Gather and analyze both Google and autocomplete data"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Run Google and autocomplete research in parallel
            google_future = executor.submit(self.get_google_research, topic)
            autocomplete_future = executor.submit(
                self.get_autocomplete_suggestions, topic
            )

            google_data = google_future.result()
            autocomplete_data = autocomplete_future.result()

        return {"google_research": google_data, "related_queries": autocomplete_data}

    def fetch_page_content(self, url: str) -> Tuple[str, BeautifulSoup]:
        """Fetch page content and return both raw HTML and BeautifulSoup object"""
        try:
            response = requests.get(url)
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            return html_content, soup
        except Exception as e:
            return f"Error fetching content: {str(e)}", None

    def compress_content(self, content: str) -> str:
        """Compress content while maintaining important information"""
        try:
            compressed = self.compressor.apply_transform([{"content": content}])
            return compressed
        except Exception as e:
            print(f"Warning: Content compression failed: {e}")
            return content

    def extract_content_and_headings(self, url: str) -> Tuple[str, List[str]]:
        """Extract both content and headings from a webpage"""
        html_content, soup = self.fetch_page_content(url)

        if soup is None:
            return html_content, []

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Extract headings
        headings = []
        for tag in ["h1", "h2", "h3", "h4"]:
            for heading in soup.find_all(tag):
                text = heading.get_text().strip()
                if text:
                    headings.append({"level": int(tag[1]), "text": text})

        # Convert to markdown
        markdown_content = md(
            str(soup),
            heading_style="ATX",
            bullets="-",
            strip=["img"],
            wrap=True,
            wrap_width=80,
        )

        # Clean up the markdown
        lines = markdown_content.split("\n")
        lines = [line for line in lines if line.strip()]
        lines = [line for line in lines if not line.strip().startswith("<!--")]
        clean_content = "\n\n".join(lines)

        return clean_content, headings

    def get_google_research(self, topic: str) -> Dict:
        """Comprehensive analysis of top Google results"""
        results = self.get_top_results(topic, num_results=10)
        analyzed_results = []

        for result in results:
            content, headings = self.extract_content_and_headings(result["link"])
            keywords = self.extract_keywords(content)

            # Compress the content
            compressed_content = self.compress_content(content)

            # Create a summary that includes both compressed content and structure
            analyzed_result = {
                "url": result["link"],
                "title": result["title"],
                "snippet": result.get("snippet", ""),
                "content": compressed_content,
                "key_phrases": keywords,
                "word_count": len(content.split()),
                "headings": headings,
            }

            analyzed_results.append(analyzed_result)

        return {
            "results": analyzed_results,
            "total_results": len(results),
            "avg_word_count": sum(r["word_count"] for r in analyzed_results)
            / len(analyzed_results),
        }

    def get_top_results(self, query: str, num_results: int = 3) -> List[Dict]:
        """Get top Google search results using SerpAPI"""
        params = {"q": query, "api_key": self.serp_api_key, "num": num_results}
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("organic_results", [])

    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract key phrases using RAKE algorithm"""
        rake = Rake()
        rake.extract_keywords_from_text(text)
        return rake.get_ranked_phrases()[:num_keywords]
