# AI build log

1. Design three services with strict Python/TypeScript task boundaries and one API-owned Knowledge Brain.
2. Make the Knowledge Brain honest when no source supports an answer.
3. Define an auto-send rule that is measurable and reversible.
4. Turn a follow-up meeting into a scope diff rather than a new project.
5. Write a one-command local runner and synthetic fixtures.

Rejected approach: a shared Python library for Task 2 would violate the language boundary and make the required API handoff untestable, so Task 2 calls Task 1 over HTTP.
