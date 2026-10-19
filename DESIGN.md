# Design

## Why

The bottleneck is not typing code. It is finding trustworthy product facts, responding consistently, and converting ambiguous conversations into bounded work. The system makes these three workflows share one source of truth.

## Architecture

```text
Sitemap/URLs -> Task 1 crawler -> SQLite + FTS5 -> /query
                                                   |\
                         Task 2 Inbox Agent ------+ -> draft + feedback
                         Task 3 Scope Team --------+ -> scope + estimate + proposal
                                                        -> human approval
```

Task 1 is Python and owns ingestion, retrieval, citations, image metadata, freshness, and unanswered-question tasks. It batches requests, uses a polite delay, and upserts by content hash. Task 2 is TypeScript only: classifier, Knowledge Brain client, reply writer, and learning ledger. It never sends email itself. Task 3 is Python only: extractor, capability checker, estimator, proposal writer, and change detector.

SQLite/FTS5 keeps the demo one-command and inspectable. A hosted vector database, Gmail OAuth, and a full web UI were dropped to fit the four-day constraint. The API boundaries make those replaceable later. Image understanding is represented as attached image metadata; a Claude vision adapter is the next production step.

The default mode is deterministic and reproducible. A deployed version should put Claude at the center, record provider, grounded sources, human edits, approval streaks, and eval scores, and version prompts. Unknown questions are explicit, factual replies require citations, complaints stay human-reviewed, service failures escalate safely, and scope output never reaches a client without approval.

Next: add a real scheduler, sitemap deletion reconciliation, OCR/vision summaries, persistent feedback, auth/rate limiting, observability, and an approval UI.
