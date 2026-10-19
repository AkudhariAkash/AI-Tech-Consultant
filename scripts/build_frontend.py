"""Inject Render build-time API URLs into the static frontend."""
import os
from pathlib import Path

root=Path(__file__).resolve().parents[1]
cfg={
    "kb":os.getenv("KB_API_URL","http://localhost:8000"),
    "scope":os.getenv("SCOPE_API_URL","http://localhost:8001"),
    "inbox":os.getenv("INBOX_API_URL","http://localhost:3000"),
}
(root/"frontend"/"config.js").write_text("window.RUNTIME_CONFIG = "+repr(cfg).replace("'",'"')+";\n",encoding="utf-8")
print("Generated frontend/config.js")
