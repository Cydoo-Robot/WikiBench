# Decision: Database Choice for User Service

**Date:** 2026-01-15
**Status:** Accepted

## Context

The user-service needs a reliable relational store for user profiles and role assignments.

## Decision

We chose **PostgreSQL 16** over MySQL and MongoDB because:
1. Strong ACID guarantees are required for billing-related role changes.
2. JSONB columns provide schema flexibility for profile metadata.
3. Team expertise is stronger in PostgreSQL.

## Consequences

- All user-service migrations use Alembic.
- The DBA team owns the `users` database in the production cluster.
- MongoDB is **not** used in user-service; any document claiming otherwise is incorrect.
