"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects YouTube videos based on search queries."""

    name = "researcher"

    def __init__(self):
        self.search_client = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` using search queries."""

        all_sources = []
        # Thực hiện tìm kiếm cho từng query được Analyst đề xuất
        for query in state.search_queries:
            results = self.search_client.search(query, max_results=2)
            all_sources.extend(results)
        
        # Nếu không có search_queries thì tìm theo query gốc
        if not all_sources:
             all_sources = self.search_client.search(state.request.query, max_results=5)

        state.sources = all_sources
        state.research_notes = f"Found {len(all_sources)} YouTube videos for the user."
        
        return state
