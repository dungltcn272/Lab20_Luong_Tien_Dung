import requests
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """YouTube search client using Google YouTube Data API v3."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/search"

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for YouTube videos relevant to a query."""
        
        if not self.api_key:
            # Trả về danh sách trống nếu thiếu API Key
            return []

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception:
            # Trong production nên có logging ở đây
            return []
        
        results = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            
            doc = SourceDocument(
                title=snippet.get("title", "No Title"),
                url=f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
                snippet=snippet.get("description", ""),
                metadata={
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "channel_title": snippet.get("channelTitle"),
                    "publish_time": snippet.get("publishedAt")
                }
            )
            results.append(doc)
            
        return results
