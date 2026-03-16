---
name: patterns_antipatterns
description: Recurring anti-patterns and confirmed conventions discovered during AutoBot Pro code reviews
type: project
---

## Confirmed Conventions (follow these)

- All logging via loguru — zero `print()` or stdlib `logging` calls allowed
- `.env` + pydantic-settings for all config; demo mode with safe defaults
- `shared/database.py` provides `Base`, `async_session`, `init_db`, `get_db` — all demos import from here
- `shared/config.py` provides a `settings` singleton — never instantiate `Settings()` directly in demo code
- `shared/notifications.py` wraps Telegram; always checks `settings.is_demo` before real API calls
- Google-style docstrings in Portuguese for all public functions and classes
- `sys.path` injection pattern used in every demo file to resolve `shared/` — this is intentional and consistent
- Each demo mounts its own FastAPI app and runs on its own port (Demo 01 = 8001)

## Anti-Patterns Found (avoid these)

### Dead / Duplicated Code
- Found in `models.py` `get_message_stats()`: variable `one_hour_ago` is assigned twice on lines 219 and 224; first assignment is unreachable code. Check for similar patterns when computing time deltas.

### Type Safety Shortcuts
- Using `list[dict[str, list[str] | str | int]]` for rule structures instead of a TypedDict causes `# type: ignore` comments to proliferate. Prefer a `TypedDict` or dataclass for any structured dict that is passed between modules.

### Missing Pydantic Field Validation
- Pydantic `BaseModel` schemas in `dashboard.py` (`RuleCreate`) rely on endpoint-level manual checks instead of `@field_validator` decorators. This means invalid data can reach the validator inconsistently. Always use Pydantic validators for schema-level constraints.

### Fragile Test Monkey-Patching
- `conftest.py` replaces `shared.database.async_session` with a test session factory at module import time. This is fragile when tests run in parallel. Prefer FastAPI `app.dependency_overrides` for injecting test DB sessions into API tests.

### Unguarded asyncio.create_task
- Background tasks created with `asyncio.create_task()` without storing the reference will be garbage-collected if the event loop is not holding a reference. Always assign the task to a variable at module or app level and attach an error callback.

### .env.example Driver Mismatch
- `.env.example` used the synchronous SQLite driver (`sqlite:///`) while `shared/config.py` defaults to the async driver (`sqlite+aiosqlite:///`). Always keep these in sync. A copy-paste from `.env.example` must produce a working configuration.

### Static Files Exposing Templates
- Mounting `/static` directly on the `templates/` directory exposes HTML source at a secondary URL. This is harmless but redundant. Keep static assets (CSS, JS, images) separate from server-rendered templates if using a different serving strategy.

### Silent Frontend Errors
- API call failures in Alpine.js components are caught and only logged to the browser console. For client demos, always show a visible error state (toast, banner, or inline message) so the demo never appears broken during a presentation.
