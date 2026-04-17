# System Architecture Overview

Acme Corp runs a microservices platform deployed on Kubernetes.
The system consists of three primary services:

- **api-gateway** — public-facing entry point; routes requests to downstream services.
- **user-service** — manages authentication, profiles, and RBAC.
- **billing-service** — handles subscription plans, invoicing, and Stripe integration.

All inter-service communication uses gRPC over mTLS.
Each service owns its own PostgreSQL database; there is no shared database.

## Deployment Model

Services are deployed to the `production` Kubernetes cluster in the `us-east-1` region.
Staging runs in `us-west-2`.
