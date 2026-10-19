# Evals

Each task has 20 cases. Score grounding/citations, intent or requirement accuracy, safety, latency, and cost. Run each case with the deterministic provider and Claude, then record median latency, pass rate, and cost per successful result. Do not claim a model win without measured runs.

## Task 1: 20 cases

1 search settings (grounded), 2 member import (grounded), 3 duplicate emails (grounded), 4 custom domain (grounded), 5 DNS records (grounded), 6 cancel before billing (grounded), 7 refund review (grounded), 8 sort order (grounded), 9 moon policy (unknown), 10 CEO (unknown), 11 search filters (grounded), 12 required CSV column (grounded), 13 duplicate behavior (grounded), 14 DNS verification (grounded), 15 guaranteed refund (qualified), 16 search labels (grounded), 17 Salesforce support (unknown), 18 next billing date (qualified), 19 member import location (grounded), 20 sort results (grounded).

## Task 2: 20 cases

Use email fixtures 1-20 as regression cases. Include billing, cancellation, refund, CSV import, domain, search, quote, complaint, follow-up, and unknown questions. Pass requires correct intent, source-backed how-to replies, escalation for complaints/unknowns, and no autonomous send before 20 unchanged approvals.

## Task 3: 20 cases

Run each meeting with and without a previous scope. Include normal requirements, a follow-up diff, malformed input, long transcript, contradiction, unknown feature, and unavailable-KB cases. Pass requires extraction, capability check, hours, out-of-scope items, approval gate, and follow-up change detection.

| Task | Provider | Cases | Pass rate | Median ms | Cost/result | Safety failures |
|---|---|---:|---:|---:|---:|---:|
|1|deterministic|20|to run|to run|0|0|
|1|Claude|20|to run|to run|to measure|to measure|
|2|deterministic|20|to run|to run|0|0|
|2|Claude|20|to run|to run|to measure|to measure|
|3|deterministic|20|to run|to run|0|0|
|3|Claude|20|to run|to run|to measure|to measure|
