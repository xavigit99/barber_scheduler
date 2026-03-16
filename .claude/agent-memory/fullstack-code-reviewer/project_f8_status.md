---
name: F8 Multi-Tenant Hardening — review status
description: Quality notes and open issues found during code review of feature/f8-multi-tenant
type: project
---

Feature reviewed on 2026-03-16.

Overall quality is solid — the tenant isolation pattern through BaseRepository is consistent and the test suite covers the critical paths.

Key open issues to track:

1. CRITICAL — BarbershopMembership model has no `tenant_id` column. The `DeleteMembershipHandler` enforces tenant via a Barbershop lookup (indirect), but `CreateMembershipHandler` creates the membership via `BaseRepository(BarbershopMembership, self.db)` with NO tenant_id, meaning the membership row itself carries no tenant context. This is a data integrity gap.

2. HIGH — `CreateMembershipHandler` (line 40) instantiates `BaseRepository(BarbershopMembership, self.db)` without `tenant_id`, bypassing the `_query()` tenant filter for the create path — acceptable for create, but the pattern is inconsistent and creates confusion.

3. HIGH — `MembershipResponse` schema does not expose `deleted_at`. The `BarbershopMembership` model uses a `deleted` boolean alongside `deleted_at`, diverging from every other model (which only added `deleted_at` to already-existing `deleted` columns). No tenant_id in the membership row means cross-tenant queries are impossible without join.

4. MEDIUM — `datetime.utcnow()` is deprecated in Python 3.12. Used in `delete_membership_handler.py`, `delete_barber_availability_handler.py`, `delete_barber_block_handler.py`, and `base_repository.py`. Should be `datetime.now(UTC)`.

5. MEDIUM — `Barbershop.tenant_id` has `unique=True` constraint — this means only one Barbershop per tenant, which may be intentional but is architecturally limiting.

6. MEDIUM — `barbershop_routes.py`: `GET /barbershops/` and `GET /barbershops/{id}` do NOT require `X-Tenant-Id` header. Cross-tenant data exposure risk for read endpoints.

7. LOW — Google-style docstrings missing on all new handlers and the membership model.

**Why:** Recorded to track open items across future conversations and PRs.
**How to apply:** Raise these when reviewing related PRs or when the user asks about membership/tenant isolation status.
