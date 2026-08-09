from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import sqlite3
from typing import Any, Optional


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEWING = "INTERVIEWING"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    GHOSTED = "GHOSTED"
    WITHDRAWN = "WITHDRAWN"

    @classmethod
    def from_string(cls, value: str) -> "ApplicationStatus":
        for member in cls:
            if member.value == value.strip().upper():
                return member
        raise ValueError(f"Unknown status: {value}. Valid options: {[m.value for m in cls]}")


@dataclass
class JobApplication:
    company: str
    role: str
    id: Optional[int] = None
    platform: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    url: Optional[str] = None
    date_applied: str = field(default_factory=lambda: date.today().isoformat())
    salary: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "JobApplication":
        raw_status = row["status"]
        status = ApplicationStatus.from_string(raw_status) if isinstance(raw_status, str) else raw_status
        return cls(
            id=row["id"],
            company=row["company"],
            role=row["role"],
            platform=row["platform"] if "platform" in row.keys() else None,
            status=status,
            url=row["url"],
            date_applied=row["date_applied"],
            salary=row["salary"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

