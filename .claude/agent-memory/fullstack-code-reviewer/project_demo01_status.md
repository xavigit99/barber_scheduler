---
name: project_demo01_status
description: Code review results and quality status for Demo 01 — Instagram Auto-Responder
type: project
---

Reviewed on 2026-03-15.

Demo 01 (Instagram Auto-Responder) is a well-structured MVP. It is fully functional in demo mode without any real credentials. No hardcoded secrets were found. Loguru is used consistently. Type hints and Google-style docstrings are present throughout.

**Key issues found (not yet fixed as of review date):**

1. `models.py` line 219-224: Dead/duplicated code — `one_hour_ago` is assigned twice; the first assignment is immediately overwritten and the `.replace(tzinfo=None)` comment says "SQLite does not support timezone" but the fix is incomplete. The variable on line 219 is unused.

2. `rules.py` `get_response()`: Double sort — rules are sorted on every call even though `add_rule()` already maintains sorted order. Minor inefficiency, not a correctness bug.

3. `rules.py` type annotations use `list[dict[str, list[str] | str | int]]` everywhere instead of a typed dataclass or TypedDict, causing multiple `# type: ignore` comments throughout the codebase.

4. `dashboard.py` `_simulator` global is typed as `Any` — no type safety on the simulator reference.

5. `dashboard.py` `RuleCreate` Pydantic model lacks field validators: empty strings for `response` and individual keywords are not rejected at the schema level; validation is done manually inside the endpoint with an inconsistency (keywords is checked for truthiness but not for empty individual keyword strings).

6. `main.py` line 93: `asyncio.create_task()` is called inside a startup event handler. If the event loop is not yet fully running or the task raises before being awaited, the exception is silently dropped. The task should be stored in a variable and an `on_done` callback should log any unexpected exit.

7. `conftest.py` monkey-patches `shared.database.async_session` at module level. This is fragile — if tests run in parallel or if import order changes, the patch may not apply correctly. A better approach is to use dependency injection (`Depends`) in the FastAPI endpoints rather than monkey-patching the global session factory.

8. `test_simulator.py`: No tests for `process_message()` with a real DB session. The method that actually writes to the database is untested.

9. `.env.example` lists `DATABASE_URL=sqlite:///./autobot.db` (synchronous driver) but `shared/config.py` defaults to `sqlite+aiosqlite:///./autobot.db` (async driver). This discrepancy would cause a runtime error if a user copies the example verbatim.

10. Frontend `index.html`: No user feedback on failed API calls (errors are only logged to the browser console). Silent failures are poor UX for a client demo.

11. `dashboard.py` mounts `/static` pointing at the `templates/` folder — this exposes the raw `index.html` source at `/static/index.html` as well as at `/`, which is a minor but unnecessary duplication.

**Quality rating:** Good — suitable for demo use with the issues above fixed before client presentation. The architecture, logging, and demo mode are all handled correctly.
