"""Supervisor / router skeleton."""

import json
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route.

        Implement routing policy based on the current state of VibeTube Advisor.
        """

        system_prompt = """You are the Supervisor of a Multi-Agent system called VibeTube Advisor.
Your job is to coordinate three agents to help a user based on their emotion:
1. 'analyst': Analyzes user's emotion and provides empathetic advice + search keywords.
2. 'researcher': Uses keywords to search for relevant YouTube videos (links and thumbnails).
3. 'writer': Takes the analysis and video results to write a final, beautifully formatted response.

Current State:
- Emotion Analysis: {emotion_status}
- Search Queries: {search_queries_status}
- YouTube Sources: {sources_count} videos found.
- Final Answer: {final_answer_status}
- Iteration: {iteration}

Routing Logic:
1. If 'emotion_analysis' is missing -> 'analyst'.
2. If 'emotion_analysis' is done but 'sources' is empty -> 'researcher'.
3. If 'emotion_analysis' and 'sources' are both done but 'final_answer' is missing -> 'writer'.
4. If 'final_answer' is prepared -> 'FINISH'.

Respond ONLY with a JSON object: {{"next": "analyst" | "researcher" | "writer" | "FINISH"}}
"""
        
        status = {
            "emotion_status": "Done" if state.emotion_analysis else "Missing",
            "search_queries_status": f"{len(state.search_queries)} queries" if state.search_queries else "Missing",
            "sources_count": len(state.sources),
            "final_answer_status": "Done" if state.final_answer else "Missing",
            "iteration": state.iteration
        }

        response = self.llm.complete(
            system_prompt=system_prompt.format(**status),
            user_prompt=f"User Query: {state.request.query}\nDecide the next step."
        )
        state.total_cost += response.cost_usd or 0

        try:
            # Clean response if LLM returns markdown code block
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            decision = json.loads(content)
            next_agent = decision.get("next", "FINISH")
        except Exception:
            # Fallback logic
            if not state.emotion_analysis: next_agent = "analyst"
            elif not state.sources: next_agent = "researcher"
            elif not state.final_answer: next_agent = "writer"
            else: next_agent = "FINISH"

        if state.iteration >= 6:
            next_agent = "FINISH"

        state.record_route(next_agent)
        return state
