"""Google Sheets service layer (gspread-based)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

import gspread
from google.oauth2.service_account import Credentials

from bot.config import GOOGLE_CREDENTIALS, SheetsConfig


@dataclass(slots=True)
class ExpenseEntry:
    date: str
    description: str
    category: str
    amount: float
    note: str = ""


@dataclass(slots=True)
class IncomeEntry:
    date: str
    description: str
    category: str
    amount: float
    note: str = ""


class SheetsService:
    """Wrapper around user spreadsheet operations."""

    def __init__(self, spreadsheet_id: str) -> None:
        self.spreadsheet_id = spreadsheet_id
        self._client = self._build_client()

    @staticmethod
    def _build_client() -> gspread.Client:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=scopes)
        return gspread.authorize(creds)

    def _month_sheet_name(self, dt: datetime | None = None) -> str:
        now = dt or datetime.now()
        return SheetsConfig.MONTHS[now.month - 1]

    def _worksheet(self, title: str) -> gspread.Worksheet:
        book = self._client.open_by_key(self.spreadsheet_id)
        return book.worksheet(title)

    def _first_empty_row(
        self,
        ws: gspread.Worksheet,
        col: int,
        row_start: int,
        row_end: int,
    ) -> int | None:
        values = ws.get(f"{gspread.utils.rowcol_to_a1(row_start, col)}:{gspread.utils.rowcol_to_a1(row_end, col)}")
        for idx, row in enumerate(values, start=row_start):
            if not row or not str(row[0]).strip():
                return idx
        return None

    def get_expense_categories(self, month_name: str | None = None) -> list[str]:
        month = month_name or self._month_sheet_name()
        ws = self._worksheet(month)
        start = SheetsConfig.EXP_CAT_RANGE_START
        col = SheetsConfig.EXP_CAT_RANGE_COL
        rng = f"{gspread.utils.rowcol_to_a1(start, col)}:{gspread.utils.rowcol_to_a1(start + 50, col)}"
        values = ws.get(rng)
        return [row[0].strip() for row in values if row and row[0].strip()]

    def get_income_categories(self, month_name: str | None = None) -> list[str]:
        month = month_name or self._month_sheet_name()
        ws = self._worksheet(month)
        start = SheetsConfig.INC_CAT_RANGE_START
        col = SheetsConfig.INC_CAT_RANGE_COL
        rng = f"{gspread.utils.rowcol_to_a1(start, col)}:{gspread.utils.rowcol_to_a1(start + 50, col)}"
        values = ws.get(rng)
        return [row[0].strip() for row in values if row and row[0].strip()]

    def append_expense(self, entry: ExpenseEntry, month_name: str | None = None) -> int:
        month = month_name or self._month_sheet_name()
        ws = self._worksheet(month)
        row = self._first_empty_row(
            ws,
            col=SheetsConfig.EXP_DATE_COL,
            row_start=SheetsConfig.EXP_DAILY_START,
            row_end=SheetsConfig.EXP_DAILY_END,
        )
        if row is None:
            raise RuntimeError("Не найдено свободной строки для расходов")

        updates = [
            (row, SheetsConfig.EXP_DATE_COL, entry.date),
            (row, SheetsConfig.EXP_DESC_COL, entry.description),
            (row, SheetsConfig.EXP_CAT_COL, entry.category),
            (row, SheetsConfig.EXP_AMT_COL, entry.amount),
            (row, SheetsConfig.EXP_NOTE_COL, entry.note),
        ]
        for r, c, value in updates:
            ws.update_cell(r, c, value)
        return row

    def append_income(self, entry: IncomeEntry, month_name: str | None = None) -> int:
        month = month_name or self._month_sheet_name()
        ws = self._worksheet(month)
        row = self._first_empty_row(
            ws,
            col=SheetsConfig.INC_DATE_COL,
            row_start=SheetsConfig.INC_DAILY_START,
            row_end=SheetsConfig.INC_DAILY_END,
        )
        if row is None:
            raise RuntimeError("Не найдено свободной строки для доходов")

        updates = [
            (row, SheetsConfig.INC_DATE_COL, entry.date),
            (row, SheetsConfig.INC_DESC_COL, entry.description),
            (row, SheetsConfig.INC_CAT_COL, entry.category),
            (row, SheetsConfig.INC_AMT_COL, entry.amount),
            (row, SheetsConfig.INC_NOTE_COL, entry.note),
        ]
        for r, c, value in updates:
            ws.update_cell(r, c, value)
        return row


def normalize_categories(values: Sequence[str]) -> list[str]:
    """Normalize category list for keyboard output."""
    seen: set[str] = set()
    result: list[str] = []
    for raw in values:
        value = raw.strip()
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
