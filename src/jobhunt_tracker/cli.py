from datetime import date
from typing import Optional
import typer
from rich.console import Console

from jobhunt_tracker import __version__
from jobhunt_tracker.db import (
    add_application,
    delete_application,
    get_application,
    get_status_counts,
    list_applications,
    update_application,
)
from jobhunt_tracker.models import ApplicationStatus, JobApplication
from jobhunt_tracker.ui import (
    render_application_detail,
    render_stats_chart,
    render_table,
)

app = typer.Typer(
    name="jht",
    help="JobHunt Tracker (jht) - Track and manage job applications from your terminal.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]JobHunt Tracker (jht)[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    pass


@app.command(name="add", help="Add a new job application.")
def add_cmd(
    company: Optional[str] = typer.Option(None, "--company", "-c", help="Company name"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="Job title or role"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Platform/source (e.g. LinkedIn, Indeed, Justjoin.it)"),
    status: Optional[ApplicationStatus] = typer.Option(
        None,
        "--status",
        "-s",
        help="Current application status",
        case_sensitive=False,
    ),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Job posting URL"),
    date_applied: Optional[str] = typer.Option(
        None,
        "--date",
        "-d",
        help="Date applied (YYYY-MM-DD)",
    ),
    salary: Optional[str] = typer.Option(None, "--salary", help="Target salary or compensation"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Optional notes or recruiter details"),
):
    is_interactive = not any([company, role, platform, status, url, date_applied, salary, notes])

    if is_interactive:
        console.print("[bold cyan]Adding a new job application (interactive mode)[/bold cyan]\n")

        while not company:
            company = typer.prompt("Company").strip()

        while not role:
            role = typer.prompt("Role").strip()

        platform_input = typer.prompt("Platform (e.g. LinkedIn, Indeed, Justjoin.it)", default="", show_default=False).strip()
        platform = platform_input if platform_input else None

        status_choices = ", ".join([s.value for s in ApplicationStatus])
        status_input = typer.prompt(f"Status ({status_choices})", default=ApplicationStatus.APPLIED.value).strip()
        try:
            status = ApplicationStatus.from_string(status_input)
        except ValueError:
            console.print(f"[yellow]Unknown status '{status_input}'. Defaulting to Applied.[/yellow]")
            status = ApplicationStatus.APPLIED

        url_input = typer.prompt("Job URL", default="", show_default=False).strip()
        url = url_input if url_input else None

        date_applied = typer.prompt("Date applied (YYYY-MM-DD)", default=date.today().isoformat()).strip()

        salary_input = typer.prompt("Compensation", default="", show_default=False).strip()
        salary = salary_input if salary_input else None

        notes_input = typer.prompt("Notes", default="", show_default=False).strip()
        notes = notes_input if notes_input else None
    else:
        if not company:
            company = typer.prompt("Company name").strip()
        if not role:
            role = typer.prompt("Job title / Role").strip()
        if not status:
            status = ApplicationStatus.APPLIED
        if not date_applied:
            date_applied = date.today().isoformat()

    new_app = JobApplication(
        company=company.strip(),
        role=role.strip(),
        platform=platform.strip() if platform else None,
        status=status,
        url=url.strip() if url else None,
        date_applied=date_applied.strip(),
        salary=salary.strip() if salary else None,
        notes=notes.strip() if notes else None,
    )
    app_id = add_application(new_app)
    console.print(f"[bold green]✓[/bold green] Application for [bold]{role}[/bold] at [bold]{company}[/bold] saved! (ID: [cyan]#{app_id}[/cyan])")


@app.command(name="list", help="List job applications with optional filtering.")
def list_cmd(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (e.g. APPLIED, INTERVIEWING)"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Filter by platform (e.g. LinkedIn, Indeed)"),
    search: Optional[str] = typer.Option(None, "--search", "-q", help="Search query for company, role, platform, or notes"),
):
    apps = list_applications(status=status, platform=platform, search=search)
    title = f"Applications ({len(apps)})"
    filters = []
    if status:
        filters.append(f"Status: {status.upper()}")
    if platform:
        filters.append(f"Platform: {platform}")
    if search:
        filters.append(f"Search: '{search}'")
    if filters:
        title += f" [{' | '.join(filters)}]"
    render_table(apps, title=title)


@app.command(name="show", help="View full details of an application by ID.")
def show_cmd(
    app_id: int = typer.Argument(..., help="Application ID"),
):
    app_data = get_application(app_id)
    if not app_data:
        console.print(f"[bold red]Error:[/bold red] Application #{app_id} not found.")
        raise typer.Exit(code=1)
    render_application_detail(app_data)


@app.command(name="update", help="Update fields on an existing application.")
def update_cmd(
    app_id: int = typer.Argument(..., help="Application ID to update"),
    status: Optional[ApplicationStatus] = typer.Option(
        None,
        "--status",
        "-s",
        help="New status",
        case_sensitive=False,
    ),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Update platform"),
    salary: Optional[str] = typer.Option(None, "--salary", help="Update compensation"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Update notes"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Update job URL"),
    date_applied: Optional[str] = typer.Option(None, "--date", "-d", help="Update date applied"),
):
    existing = get_application(app_id)
    if not existing:
        console.print(f"[bold red]Error:[/bold red] Application #{app_id} not found.")
        raise typer.Exit(code=1)

    updated = update_application(
        app_id=app_id,
        status=status,
        platform=platform,
        salary=salary,
        notes=notes,
        url=url,
        date_applied=date_applied,
    )
    if updated:
        console.print(f"[bold green]✓[/bold green] Application [cyan]#{app_id}[/cyan] updated successfully.")
    else:
        console.print("[dim]No changes were provided to update.[/dim]")


@app.command(name="delete", help="Delete an application by ID.")
def delete_cmd(
    app_id: int = typer.Argument(..., help="Application ID to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    existing = get_application(app_id)
    if not existing:
        console.print(f"[bold red]Error:[/bold red] Application #{app_id} not found.")
        raise typer.Exit(code=1)

    if not yes:
        confirmed = typer.confirm(f"Are you sure you want to delete application #{app_id} ({existing.company} - {existing.role})?")
        if not confirmed:
            console.print("[dim]Action cancelled.[/dim]")
            raise typer.Abort()

    delete_application(app_id)
    console.print(f"[bold green]✓[/bold green] Application [cyan]#{app_id}[/cyan] deleted.")


@app.command(name="stats", help="Display visual breakdown of application statuses.")
def stats_cmd():
    counts = get_status_counts()
    render_stats_chart(counts)


if __name__ == "__main__":
    app()
