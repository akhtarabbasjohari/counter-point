# CounterPoint

## Project Goals

- CounterPoint should research a competitor using live web search and summarize their current offerings, pricing, and recent activity.
- It should read an uploaded positioning document (PDF/txt) and compare it against what it finds about a competitor.
- It should remember earlier findings within a session, so follow-up questions build on previous research instead of starting over.
- Every tool call (search, file read) should be logged with a timestamp for traceability.
- The agent should be able to answer multi-hop questions that combine the uploaded document with fresh web research, not just isolated lookups.
- The interface should be simple, a way to enter a competitor name, upload a document, and see the agent's findings clearly, without unnecessary complexity.