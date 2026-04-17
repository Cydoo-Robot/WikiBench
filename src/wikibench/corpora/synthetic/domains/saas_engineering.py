"""SaaS Engineering domain template (Phase 1 Week 5)."""

from wikibench.corpora.synthetic.domains._base import DomainTemplate


class SaaSEngineeringDomain(DomainTemplate):
    id = "saas_engineering"
    description = "Internal engineering knowledge base for a fictional SaaS company."

    def seed_concepts(self) -> list[str]:
        return [
            "microservices architecture",
            "API gateway",
            "CI/CD pipeline",
            "database sharding",
            "incident response",
            "on-call rotation",
            "feature flags",
            "multi-tenancy",
            "SLA / SLO / SLI",
            "data retention policy",
        ]
