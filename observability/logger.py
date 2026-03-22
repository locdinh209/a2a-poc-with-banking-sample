import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class A2AEventLogger:
    """Logs all A2A protocol events to terminal with rich formatting."""

    def log_discovery(self, agent_url: str, agent_card: dict):
        console.print(Panel(
            f"[bold green]🔍 DISCOVERED[/] {agent_card.get('name', 'Unknown')}\n"
            f"    URL: {agent_url}\n"
            f"    Skills: {', '.join(s.get('name', 'Unknown') for s in agent_card.get('skills', []))}",
            title="Agent Discovery",
            border_style="green"
        ))

    def log_send_message(self, agent_name: str, message: str, task_id: str):
        console.print(Panel(
            f"[bold cyan]📤 SEND[/] → {agent_name}\n"
            f"    Message: {message[:120]}...\n"
            f"    Task ID: {task_id}",
            title=f"A2A Request [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}]",
            border_style="cyan"
        ))

    def log_task_status(self, agent_name: str, task_id: str, state: str, message: str = ""):
        colors = {
            "SUBMITTED": "yellow", "WORKING": "blue",
            "COMPLETED": "green", "FAILED": "red",
            "INPUT_REQUIRED": "magenta", "CANCELED": "grey50",
        }
        color = colors.get(state, "white")
        icon = {"COMPLETED": "✅", "FAILED": "❌", "WORKING": "⏳",
                "INPUT_REQUIRED": "❓", "SUBMITTED": "📋"}.get(state, "🔄")
        console.print(Panel(
            f"[bold {color}]{icon} {state}[/] ← {agent_name}\n"
            f"    Task: {task_id}\n"
            f"    {f'Detail: {message}' if message else ''}",
            title=f"Task Update [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}]",
            border_style=color
        ))

    def log_artifact(self, agent_name: str, artifact_name: str, content_preview: str):
        console.print(Panel(
            f"[bold green]📦 ARTIFACT[/] from {agent_name}\n"
            f"    Name: {artifact_name}\n"
            f"    Content: {content_preview[:200]}...",
            title="Artifact Received",
            border_style="green"
        ))

    def log_workflow_summary(self, steps: list[dict]):
        table = Table(title="🏦 Workflow Summary", show_lines=True)
        table.add_column("Step", style="bold")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        for s in steps:
            table.add_row(str(s["step"]), s["agent"], s["status"], str(s["duration"]))
        console.print(table)
