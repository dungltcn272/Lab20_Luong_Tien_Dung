"""Analyst agent skeleton."""

import json
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Analyzes user's emotion and extracts search intents."""

    name = "analyst"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.emotion_analysis` and `state.search_queries`."""

        system_prompt = """You are an Empathetic Analyst for VibeTube Advisor.
Your goal is to understand the user's emotional state from their message and suggest how to help them through YouTube content.

Tasks:
1. Analyze the user's current mood/emotion.
2. Write a brief, deeply empathetic message of support/advice in the EXACT SAME LANGUAGE as the user's message.
3. Generate 3 specific search queries for YouTube that would help improve or match their mood. The queries MUST be in the same language as the user's message to find suitable local content.

Respond ONLY with a JSON object:
{
  "emotion_analysis": "Your empathetic advice here (in the user's language)...",
  "search_queries": ["query 1", "query 2", "query 3"]
}
"""
        
        response = self.llm.complete(
            system_prompt=system_prompt,
            user_prompt=state.request.query
        )
        state.total_cost += response.cost_usd or 0

        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            data = json.loads(content)
            state.emotion_analysis = data.get("emotion_analysis")
            state.search_queries = data.get("search_queries", [])
            state.analysis_notes = state.emotion_analysis  # Backup for original field
        except Exception:
            state.emotion_analysis = "Mình hiểu bạn đang phải trải qua rất nhiều suy nghĩ ngổn ngang. Hãy để mình gợi ý cho bạn một vài video để giải toả nhé."
            state.search_queries = [state.request.query]

        return state
