# CONTRIBUTING.md

## Development Setup

1. Copy `.env.example` to `.env`
2. Set `DATABASE_URL` and `AUTH_SECRET`
3. Install dependencies with `make install`
4. Run `make test`

Local default example:

`DATABASE_URL=sqlite:///./barber_scheduler.db`

## Daily Commands

- `make install`
- `make clean`
- `make test`
- `make run`

## Branching

Use one branch per feature or fix.

Recommended patterns:

- `feature/<short-scope>`
- `fix/<short-scope>`

Examples:

- `feature/client-endpoints`
- `feature/auth-and-roles`
- `fix/database-config`

## Code Expectations

- keep routes focused on HTTP concerns
- keep business logic in commands, queries and handlers
- add or update automated tests for every meaningful behavior change
- prefer small, reviewable changes over broad rewrites
- avoid committing secrets, local environments or generated files

## Pull Requests

Every PR should include:

- objective summary
- main technical decisions
- tests executed
- open risks or limitations
