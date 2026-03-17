---
name: F11 Feedback Panel — review status
description: Quality notes and open issues found during code review of F11 Feedback Panel feature
type: project
---

Feature reviewed on 2026-03-17.

Overall quality is good — tenant isolation on write is correct, ownership enforcement is solid, and test coverage is broad. One critical correctness bug must be fixed before shipping.

## Critical

1. CRITICAL — `create_feedback_handler.py` line 40: `datetime.now()` (naive, local time) compared against `appointment.end_at` (likely UTC or timezone-aware). On developer machines in Europe/Lisbon this will produce incorrect results. Must use `datetime.now(UTC)` consistently, matching the pattern in `BaseRepository.delete`. Same class of issue as the `datetime.utcnow()` deprecation noted in F8.

## High

2. HIGH — `GET /feedback/barber/{barber_id}` has NO authentication. `FeedbackResponse` returns `client_id`, `appointment_id`, and `tenant_id`. If this endpoint is public, the schema must be narrowed. If private, add `require_roles`.

3. HIGH — `NotFoundError` is imported inside the function body in `list_barber_feedback_handler.py` (line 21). Should be a top-level import.

## Medium

4. MEDIUM — `FeedbackCreate.comentario` has no `max_length` constraint. Unbounded text field is an input-size risk.

5. MEDIUM — Google-style docstrings missing on all new handlers and the Feedback model. Third time this pattern has appeared across F8 and F11.

6. MEDIUM — Migration creates `ix_feedback_id` index on the primary key column — this is redundant (PK already indexed). Remove it.

7. MEDIUM — Rating validation duplicated between Pydantic schema (`Field(ge=1, le=5)`) and handler (`if command.rating < 1 or command.rating > 5`). Both should stay, but a comment explaining the dual-guard intent would prevent future removal of one.

8. MEDIUM — `command.tenant_id` used for appointment lookup but `appointment.tenant_id` used for the write. Correct behavior, but non-obvious without a comment.

## Low

9. LOW — `list_my_feedback_handler` silently returns `[]` for unknown client, while `list_barber_feedback_handler` raises `NotFoundError` for unknown barber. Inconsistency should be documented with a comment.

10. LOW — `_get_user_id` helper in routes handles both dict and ORM object — if the dict path is dead code, remove it.

**Why:** Recorded to track open items for the PR and future reviews.
**How to apply:** Raise these when reviewing the F11 PR or when the user asks about feedback/review-related endpoints.
