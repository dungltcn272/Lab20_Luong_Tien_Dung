"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final response with formatted advice and video recommendations."""

    name = "writer"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        system_prompt = """You are the Lead Writer for VibeTube Advisor.
Your task is to take the empathetic analysis and create a beautiful, supportive, and well-structured response for the user.

Input:
- User Emotion Analysis: {emotion_analysis}

Requirement:
1. Provide a warm, caring, and encouraging advice based on the emotion analysis.
2. Use Markdown formatting to make it readable.
3. DO NOT list or mention the suggested videos in your response. The UI will automatically display the videos in a separate horizontal carousel. Your job is ONLY to provide the psychological advice.
4. Do NOT output raw JSON. Output a natural, human-like response.
5. IMPORTANT: You MUST write your final response in the EXACT SAME LANGUAGE as the Emotion Analysis provided above.

Final Goal: Provide a comprehensive 'care package' of advice matching the user's language.
"""
        
        response = self.llm.complete(
            system_prompt=system_prompt.format(
                emotion_analysis=state.emotion_analysis
            ),
            user_prompt="Write the final response for the user."
        )
        state.total_cost += response.cost_usd or 0

        state.final_answer = response.content
        return state
