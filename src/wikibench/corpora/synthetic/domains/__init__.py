"""Domain templates for synthetic corpus generation."""

from __future__ import annotations

from wikibench.corpora.synthetic.domains._base import DomainTemplate
from wikibench.corpora.synthetic.domains.clinical_trials import ClinicalTrialsDomain
from wikibench.corpora.synthetic.domains.saas_engineering import SaaSEngineeringDomain

_DOMAINS: dict[str, DomainTemplate] = {
    SaaSEngineeringDomain.id: SaaSEngineeringDomain(),
    ClinicalTrialsDomain.id: ClinicalTrialsDomain(),
}

_ALIASES: dict[str, str] = {
    "saas": "saas_engineering",
    "clinical": "clinical_trials",
}


def get_domain(name: str) -> DomainTemplate:
    """Resolve a domain id or alias to a :class:`DomainTemplate` instance."""
    key = name.strip().lower().replace("-", "_")
    key = _ALIASES.get(key, key)
    if key not in _DOMAINS:
        avail = ", ".join(sorted(_DOMAINS))
        raise KeyError(f"Unknown domain {name!r}. Available: {avail}")
    return _DOMAINS[key]


def list_domains() -> list[str]:
    """Return sorted registered domain ids."""
    return sorted(_DOMAINS)
