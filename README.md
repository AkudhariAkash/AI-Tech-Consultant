# AI Tech Consultant

An end-to-end capstone implementation with three connected tasks:

1. **Knowledge Brain** (`task1_knowledge_brain`, Python/FastAPI): ingests a sitemap or URLs, stores searchable article text and image metadata, answers questions with citations, and records unanswered questions for human follow-up.
2. **Inbox Agent** (`task2_inbox_agent`, TypeScript/Node): classifies customer email, calls Task 1, drafts a reply, learns from human edits, and only enables auto-send after 20 unchanged approvals for one intent.
3. **Meeting to Scope** (`task3_meeting_scope`, Python/FastAPI): extracts requirements, checks product capability through Task 1, estimates work, produces a proposal, diffs follow-up meetings, and requires approval.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd task2_inbox_agent
npm install
npm run build
cd ..
python run.py
```

Open the dashboard at `http://localhost:8081`. Backend docs are at `http://localhost:8000/docs` and `http://localhost:8001/docs`; Inbox health is at `http://localhost:3000/health`.

To seed the demo knowledge base without network access: `python scripts/seed_demo.py`.

The default demo mode is deterministic and works without API keys. Set `ANTHROPIC_API_KEY` to enable a Claude adapter when added; responses explicitly expose grounding and approval state.

See `DESIGN.md`, `EVALS.md`, `AI_LOG.md`, `data/emails.jsonl`, and `data/meetings/` for submission evidence.

The attached brief is the source specification. The linked Notion page could not be fetched in this environment, so no unsupported Notion-only requirements are claimed.
