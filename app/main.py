import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Agent Journal")

AGENT_ID = os.environ.get("AGENT_ID", "unknown")

# In-memory store (swap for DB later)
entries: list[dict] = []


class JournalEntry(BaseModel):
    title: str
    body: str


@app.get("/", response_class=HTMLResponse)
async def index():
    entry_html = ""
    for e in reversed(entries):
        entry_html += f"<li><strong>{e['title']}</strong> — {e['body']} <small>({e['created']})</small></li>"
    if not entry_html:
        entry_html = "<li>No entries yet. POST /entries to add one.</li>"

    return f"""<!DOCTYPE html>
<html>
<head><title>Journal — {AGENT_ID}</title></head>
<body>
  <h1>Journal App</h1>
  <p>Served by agent: <strong>{AGENT_ID}</strong></p>
  <p><a href="/stats">View stats</a></p>
  <h2>Entries</h2>
  <ul>{entry_html}</ul>
</body>
</html>"""


@app.get("/stats")
async def stats():
    most_recent = max((e["created"] for e in entries), default=None)
    return {"total_entries": len(entries), "most_recent_entry": most_recent}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": AGENT_ID}


@app.post("/entries")
async def create_entry(entry: JournalEntry):
    record = {
        "title": entry.title,
        "body": entry.body,
        "created": datetime.now().isoformat(),
    }
    entries.append(record)
    return record


@app.get("/entries")
async def list_entries():
    return entries
