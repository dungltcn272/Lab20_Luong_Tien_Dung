"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    from multi_agent_research_lab.services.llm_client import LLMClient
    
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    with console.status("[bold green]Running single-agent baseline..."):
        llm = LLMClient()
        response = llm.complete(
            system_prompt="You are a helpful assistant. Provide a concise response to the user query.",
            user_prompt=query
        )
        state.final_answer = response.content
        
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))
    console.print(f"[dim]Tokens: In={response.input_tokens}, Out={response.output_tokens} | Cost: ${response.cost_usd:.6f}[/dim]")


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run both single and multi-agent systems and compare results."""

    _init()
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    
    # 1. Run Baseline (Single Agent)
    def baseline_runner(q: str) -> ResearchState:
        from multi_agent_research_lab.services.llm_client import LLMClient
        state = ResearchState(request=ResearchQuery(query=q))
        llm = LLMClient()
        resp = llm.complete("You are a helpful assistant.", q)
        state.final_answer = resp.content
        return state

    console.print("[bold blue]Starting Benchmark...[/bold blue]")
    with console.status("[bold blue]Running Baseline..."):
        _, baseline_metrics = run_benchmark("Single-Agent (Baseline)", query, baseline_runner)
    
    # 2. Run Multi-Agent
    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    with console.status("[bold green]Running Multi-Agent..."):
        _, multi_metrics = run_benchmark("Multi-Agent (System)", query, multi_agent_runner)
    
    # 3. Display Report
    from rich.table import Table
    table = Table(title="Benchmark Comparison Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Single-Agent", style="magenta")
    table.add_column("Multi-Agent", style="green")
    
    table.add_row("Latency (s)", f"{baseline_metrics.latency_seconds:.2f}", f"{multi_metrics.latency_seconds:.2f}")
    table.add_row("Estimated Cost ($)", f"{baseline_metrics.estimated_cost_usd:.5f}", f"{multi_metrics.estimated_cost_usd:.5f}")
    table.add_row("Quality Score (0-10)", f"{baseline_metrics.quality_score:.1f}", f"{multi_metrics.quality_score:.1f}")
    table.add_row("Steps/Notes", "1", f"{multi_metrics.notes}")
    
    console.print(table)
    
    # Save to file
    import os
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Report: VibeTube Advisor\n\n")
        f.write(f"**Query**: {query}\n\n")
        f.write("| Metric | Single-Agent | Multi-Agent |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| Latency | {baseline_metrics.latency_seconds:.2f}s | {multi_metrics.latency_seconds:.2f}s |\n")
        f.write(f"| Cost | ${baseline_metrics.estimated_cost_usd:.5f} | ${multi_metrics.estimated_cost_usd:.5f} |\n")
        f.write(f"| Quality | {baseline_metrics.quality_score:.1f}/10 | {multi_metrics.quality_score:.1f}/10 |\n")
    
    console.print(f"\n[green]Report saved to {report_path}[/green]")


if __name__ == "__main__":
    app()
