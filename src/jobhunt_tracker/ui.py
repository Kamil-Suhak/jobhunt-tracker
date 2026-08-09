from typing import Sequence
import plotext as plt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from jobhunt_tracker.models import ApplicationStatus, JobApplication

console = Console()

STATUS_STYLES = {
    ApplicationStatus.APPLIED: "cyan",
    ApplicationStatus.SCREENING: "blue",
    ApplicationStatus.INTERVIEWING: "yellow bold",
    ApplicationStatus.OFFER: "green bold",
    ApplicationStatus.REJECTED: "red",
    ApplicationStatus.GHOSTED: "dim white",
    ApplicationStatus.WITHDRAWN: "magenta",
}


def get_status_badge(status: ApplicationStatus) -> str:
    color = STATUS_STYLES.get(status, "white")
    return f"[{color}]{status.value}[/{color}]"


def render_table(applications: Sequence[JobApplication], title: str = "Job Applications") -> None:
    if not applications:
        console.print("[dim]No applications found.[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta", expand=True)
    table.add_column("ID", style="dim", width=4, justify="right")
    table.add_column("Company", style="bold white", min_width=15)
    table.add_column("Role", style="bold cyan", min_width=18)
    table.add_column("Platform", style="blue", min_width=12)
    table.add_column("Status", justify="center", width=14)
    table.add_column("Date Applied", style="dim", width=12, justify="center")
    table.add_column("Salary", style="green", width=12)
    table.add_column("Notes", style="dim italic", max_width=25)

    for app in applications:
        table.add_row(
            str(app.id),
            app.company,
            app.role,
            app.platform or "-",
            get_status_badge(app.status),
            app.date_applied,
            app.salary or "-",
            app.notes or "-",
        )

    console.print(table)


def render_application_detail(app: JobApplication) -> None:
    content = (
        f"[bold]Company:[/bold] {app.company}\n"
        f"[bold]Role:[/bold] {app.role}\n"
        f"[bold]Platform:[/bold] {app.platform or '-'}\n"
        f"[bold]Status:[/bold] {get_status_badge(app.status)}\n"
        f"[bold]Date Applied:[/bold] {app.date_applied}\n"
        f"[bold]URL:[/bold] {app.url or '-'}\n"
        f"[bold]Salary:[/bold] {app.salary or '-'}\n"
        f"[bold]Notes:[/bold] {app.notes or '-'}\n"
        f"[dim]Created: {app.created_at} | Updated: {app.updated_at}[/dim]"
    )
    panel = Panel(
        content,
        title=f"Application #{app.id} - {app.company}",
        border_style="cyan",
        expand=False,
    )
    console.print(panel)


def render_stats_chart(status_counts: dict[str, int]) -> None:
    total = sum(status_counts.values())
    if total == 0:
        console.print("[dim]No applications to display stats for.[/dim]")
        return

    active_statuses = {k: v for k, v in status_counts.items() if v > 0}
    categories = list(active_statuses.keys())
    values = list(active_statuses.values())

    console.print(f"\n[bold green]Total Applications:[/bold green] [bold]{total}[/bold]\n")

    plt.clf()
    plt.bar(categories, values, orientation="horizontal", color="cyan")
    plt.title("Applications by Status")
    plt.plotsize(60, len(categories) * 2 + 3)
    plt.show()
