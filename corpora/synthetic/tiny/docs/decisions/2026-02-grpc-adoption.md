# Decision: gRPC for Inter-Service Communication

**Date:** 2026-02-03
**Status:** Accepted

## Context

As the number of microservices grew, REST-over-HTTP/1.1 caused latency and schema-drift issues.

## Decision

All internal service-to-service calls migrate to **gRPC** with protobuf schemas stored in the
`proto/` monorepo directory.  REST APIs remain only for external clients via api-gateway.

## Migration Plan

| Service        | gRPC migration target | Status      |
|----------------|-----------------------|-------------|
| user-service   | Q1 2026               | Complete    |
| billing-service| Q2 2026               | In progress |
| api-gateway    | External-facing, REST kept | N/A    |

## Consequences

- Protobuf schemas become the contract; breaking changes require a major version bump.
- Engineers must install the `grpcio-tools` dev dependency.
