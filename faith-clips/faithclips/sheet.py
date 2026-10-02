"""Google Sheet: the delivery spot AND the finder's memory.

Tabs (created automatically on the first run):
  Clips     one row per clip, newest at the top
  Channels  your approved channel list (Approved: Yes / No / New)
  Seen      every video already judged, so nothing is reviewed twice
  Log       one row per run, so you can see it's working
"""
import json
import logging

import gspread
from gspread.exceptions import WorksheetNotFound

log = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CLIP_HEADERS = [
    "Date", "Speaker", "Type", "Source Channel", "Video Link (timestamped)", "Start", "End",
    "Exact Quote", "Segment Transcript", "Score", "Hook 1", "Hook 2", "Hook 3", "Caption",
    "Piece Pairing", "How To Use", "Permission Message", "Status", "Notes", "Video Title", "Video ID",
]
CHANNEL_HEADERS = [
    "Name", "Handle", "Type", "Approved", "Channel ID", "YouTube Title", "Subscribers",
    "Link", "Source", "Added",
]
SEEN_HEADERS = ["Video ID", "Date", "Result"]
LOG_HEADERS = [
    "Date", "Time (Pacific)", "Run Type", "Candidates", "Sent To Claude", "Clips Added",
    "YouTube Units", "Claude Cost (est.)", "Notes",
]
TABS = {"Clips": CLIP_HEADERS, "Channels": CHANNEL_HEADERS, "Seen": SEEN_HEADERS, "Log": LOG_HEADERS}


def safe(value):
    """Every write uses RAW mode, so text is stored exactly as-is and is never run
    as a formula (a transcript line starting with "=" stays plain text)."""
    if value is None:
        return ""
    return value if isinstance(value, (int, float)) else str(value)


class Sheet:
    def __init__(self, service_account_json: str, sheet_id: str):
        info = json.loads(service_account_json)
        self.client_email = info.get("client_email", "")
        gc = gspread.service_account_from_dict(info, scopes=SCOPES)
        self.book = gc.open_by_key(sheet_id)
        self.url = self.book.url
        self.tabs: dict[str, gspread.Worksheet] = {}

    def setup(self) -> list[str]:
        """Create any missing tabs with bold, frozen headers. Returns tabs created."""
        created = []
        existing = {ws.title: ws for ws in self.book.worksheets()}
        for name, headers in TABS.items():
            ws = existing.get(name)
            if ws is None:
                ws = self.book.add_worksheet(title=name, rows=1000, cols=len(headers))
                created.append(name)
            first = ws.row_values(1)
            if first != headers:
                if not first:
                    ws.update([headers], "A1")
                elif first[: len(headers)] != headers:
                    log.warning("%s tab headers differ from expected; leaving them as they are", name)
            ws.freeze(rows=1)
            ws.format("1:1", {"textFormat": {"bold": True}})
            self.tabs[name] = ws
        # A brand-new Google Sheet starts with "Sheet1"; remove it once ours exist.
        if "Sheet1" in existing and len(existing) == 1:
            self.book.del_worksheet(existing["Sheet1"])
        return created

    def ws(self, name: str) -> gspread.Worksheet:
        if name not in self.tabs:
            try:
                self.tabs[name] = self.book.worksheet(name)
            except WorksheetNotFound:
                self.setup()
        return self.tabs[name]

    def records(self, name: str) -> list[dict]:
        rows = self.ws(name).get_all_values()
        if not rows:
            return []
        headers = rows[0]
        return [dict(zip(headers, r + [""] * (len(headers) - len(r)))) for r in rows[1:]]

    # -- channels -------------------------------------------------------------
    def channels(self) -> list[dict]:
        out = []
        for i, r in enumerate(self.records("Channels"), start=2):
            r["_row"] = i
            out.append(r)
        return out

    def add_channels(self, rows: list[list]):
        if rows:
            self.ws("Channels").append_rows([[safe(v) for v in r] for r in rows])

    def update_channel(self, row: int, values: dict):
        ws = self.ws("Channels")
        cells = []
        for key, value in values.items():
            col = CHANNEL_HEADERS.index(key) + 1
            cells.append(gspread.Cell(row, col, safe(value)))
        ws.update_cells(cells)

    # -- memory ---------------------------------------------------------------
    def known_video_ids(self) -> set[str]:
        ids = {r.get("Video ID", "") for r in self.records("Clips")}
        ids |= {r.get("Video ID", "") for r in self.records("Seen")}
        return {i for i in ids if i}

    def known_quotes(self) -> set[str]:
        from .util import normalize
        return {normalize(r.get("Exact Quote", "")) for r in self.records("Clips") if r.get("Exact Quote")}

    def add_seen(self, rows: list[list]):
        if rows:
            self.ws("Seen").append_rows([[safe(v) for v in r] for r in rows])

    # -- clips ----------------------------------------------------------------
    def add_clips(self, rows: list[list]):
        """Insert at the top (row 2) so the newest, best clips are first on a phone."""
        if rows:
            self.ws("Clips").insert_rows([[safe(v) for v in r] for r in rows], row=2)

    def clips_for_date(self, date: str) -> list[dict]:
        return [r for r in self.records("Clips") if r.get("Date") == date]

    # -- log ------------------------------------------------------------------
    def log_run(self, row: list):
        self.ws("Log").append_rows([[safe(v) for v in row]])

    def runs_on(self, date: str) -> list[dict]:
        return [r for r in self.records("Log") if r.get("Date") == date]
