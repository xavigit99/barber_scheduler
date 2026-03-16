---
name: master-hub integration tests
description: Patterns used when testing the shared/main.py Master Hub FastAPI app, including async httpx mocking strategy
type: project
---

Tests for the Master Hub live at `shared/tests/test_master_hub.py`.

Coverage: 5 tests across 3 classes (`TestMasterHubRoot`, `TestMasterHubHealth`, `TestPortfolioStatus`).

**Why:** Master Hub aggregates stats from 3 demo services via internal httpx calls. Tests must never touch real network — all httpx calls are intercepted.

**How to apply:**

- Patch target is `shared.main.httpx.AsyncClient` (not `httpx.AsyncClient`), because the module imports `httpx` directly.
- The async context manager pattern for the mock is:
  ```python
  mock_client = MagicMock()
  mock_client.__aenter__ = AsyncMock(return_value=mock_client)
  mock_client.__aexit__ = AsyncMock(return_value=False)
  mock_client.get = AsyncMock(side_effect=<exc or callable>)
  with patch("shared.main.httpx.AsyncClient", return_value=mock_client):
      ...
  ```
- A helper `_make_mock_client(responses: dict[str, Any])` dispatches by URL fragment so per-demo payloads can be returned in a single mock.
- `fetch_stats` catches `Exception` broadly, so both `ConnectError` and `TimeoutException` result in `status="offline"` — tests assert `status in {"offline", "error"}` to stay resilient.
- `GET /` falls back to inline HTML if `shared/templates/index.html` is absent; the test asserts `"AutoBot"` in body (present in both the fallback string and the real template).
- Client fixture uses `ASGITransport(app=app)` imported inside the fixture to pick up the live app instance.
