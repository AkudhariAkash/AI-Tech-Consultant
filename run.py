"""One-command local runner for all three tasks."""
from __future__ import annotations
import os, subprocess, sys, time
ROOT = os.path.dirname(os.path.abspath(__file__))
procs = []
try:
    inbox_entry = "task2_inbox_agent/dist/server.js" if os.path.exists(os.path.join(ROOT,"task2_inbox_agent","dist","server.js")) else "task2_inbox_agent/src/server.js"
    for cmd in [[sys.executable,"-m","uvicorn","task1_knowledge_brain.app:app","--port","8000"],[sys.executable,"-m","uvicorn","task3_meeting_scope.app:app","--port","8001"],["node",inbox_entry],[sys.executable,"web.py"]]:
        procs.append(subprocess.Popen(cmd, cwd=ROOT))
    print("Knowledge Brain: http://localhost:8000/docs")
    print("Meeting to Scope: http://localhost:8001/docs")
    print("Inbox Agent: http://localhost:3000/health")
    print("Dashboard: http://localhost:8081")
    while True:
        if any(p.poll() is not None for p in procs): raise SystemExit("A service exited; inspect its console output.")
        time.sleep(1)
except KeyboardInterrupt: pass
finally:
    for p in procs:
        if p.poll() is None: p.terminate()
