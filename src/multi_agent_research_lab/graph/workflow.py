"""LangGraph workflow skeleton."""

from langgraph.graph import END, StateGraph
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.writer import WriterAgent


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.analyst = AnalystAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()

    def build(self):
        """Create and compile the LangGraph graph."""
        
        # Khởi tạo Graph với schema của ResearchState
        workflow = StateGraph(ResearchState)
        
        # Định nghĩa các Node (nút) trong Graph
        workflow.add_node("supervisor", self.supervisor.run)
        workflow.add_node("analyst", self.analyst.run)
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("writer", self.writer.run)
        
        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("supervisor")
        
        # Thiết lập các cạnh điều kiện (conditional edges) từ Supervisor
        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state.route_history[-1], # Lấy quyết định cuối cùng từ Supervisor
            {
                "analyst": "analyst",
                "researcher": "researcher",
                "writer": "writer",
                "FINISH": END
            }
        )
        
        # Sau khi mỗi worker làm xong, quay lại Supervisor để quyết định bước tiếp theo
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("writer", "supervisor")
        
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""

        app = self.build()
        
        # Chạy workflow
        final_output = app.invoke(state)
        
        # Đảm bảo trả về đối tượng ResearchState
        if isinstance(final_output, dict):
            return ResearchState(**final_output)
        return final_output

    def stream(self, state: ResearchState):
        """Stream the workflow execution for live UI updates."""
        app = self.build()
        return app.stream(state)
