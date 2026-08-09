# JobHunt Tracker (`jht`)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A fast, terminal-native job application tracker built with modern Python. Manage, track, search, and visualize your job hunt directly from your shell.

---

## Tech Stack

- **CLI Engine**: [Typer](https://typer.tiangolo.com/) (Type-driven CLI builder with Click foundation)
- **Terminal UI**: [Rich](https://rich.readthedocs.io/)
- **Visualizations**: [Plotext](https://github.com/piccolomo/plotext)
- **Database**: SQLite3

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/jobhunt-tracker.git
cd jobhunt-tracker
```

### 2. Install in editable mode

```bash
pip install -e .
```

Once installed, the `jht` command will be available across your terminal.

---

## Usage Guide

### 1. Add an Application

Run interactively:

```bash
jht add
```

Or provide arguments via flags:

```bash
jht add -c "Google" -r "React Engineer" -p "LinkedIn" -s "APPLIED" -u "https://careers.google.com/jobs/123" -n "Referred by Alex"
```

### 2. List Applications

List all logged applications:

```bash
jht list
```

Filter by status or platform:

```bash
jht list -s INTERVIEWING
jht list -p Justjoin.it
```

Search across company, role, platform, or notes:

```bash
jht list -q "frontend"
```

### 3. View Application Details by ID

```bash
jht show 1
```

### 4. Update Application

```bash
jht update 1 -s INTERVIEWING -p "Indeed" -n "Recruiter screening on Friday at 2 PM"
```

### 5. View Statistics

Display total count and a terminal bar chart of your current funnel:

```bash
jht stats
```

### 6. Delete an Application

```bash
jht delete 1
```

---

## Project Architecture

```text
jobhunt-tracker/
├── pyproject.toml              # Build backend and CLI entrypoints
├── README.md                   # Project documentation
├── .gitignore                  # Python/SQLite ignores
└── src/
    └── jobhunt_tracker/
        ├── __init__.py         # Package metadata & version
        ├── config.py           # App paths & DB path resolution (~/.jobhunt-tracker/)
        ├── models.py           # ApplicationStatus Enum & JobApplication dataclass
        ├── db.py               # SQLite schema & repository CRUD operations
        ├── ui.py               # Rich UI tables/cards & Plotext  chart
        └── cli.py              # Typer CLI commands and arguments
```

---

## Application Status Workflow

- `Applied` - Initial application submitted
- `Screening` - Recruiter screen scheduled/completed
- `Interviewing` - Interviews in progress
- `Offer` - Offer received
- `Rejected` - Application declined
- `Ghosted` - No response received
- `Withdrawn` - Candidate withdrew application

---

## License

MIT
