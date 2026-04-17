"""Clinical Trials domain template (Phase 1 Week 5)."""

from wikibench.corpora.synthetic.domains._base import DomainTemplate


class ClinicalTrialsDomain(DomainTemplate):
    id = "clinical_trials"
    description = "Clinical trial documentation knowledge base."

    def seed_concepts(self) -> list[str]:
        return [
            "randomised controlled trial",
            "phase I / II / III",
            "informed consent",
            "primary endpoint",
            "adverse event",
            "IRB approval",
            "CONSORT reporting",
            "blinding / placebo",
            "statistical power",
            "regulatory submission",
        ]
