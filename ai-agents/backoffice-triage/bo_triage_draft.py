"""Action drafting: one short next step per queue.

The draft is the *proposed* outbound action. It is never sent by this module —
the approval gate in :mod:`bo_triage_audit` owns that. In the live lane an LLM
phrases the draft (``prompts/draft.task.v1.txt``); here the templates in
``config/router.json`` keep the demo deterministic.
"""

from __future__ import annotations

from bo_triage_config import RouterConfig


def render_action(router: RouterConfig, queue: str, subject: str) -> str:
    """Render the action template for a queue against the message subject."""

    template = router.action_templates.get(queue, router.action_templates["general"])
    return template.format(subject=subject)


SENSITIVE_QUEUES = frozenset({"billing", "security"})


def is_sensitive(queue: str) -> bool:
    """Whether a queue handles access or money and is flagged for priority review.

    Sensitivity never bypasses the gate — it only flags the audit row so a human
    reviewing the queue sees the higher-risk items first.
    """

    return queue in SENSITIVE_QUEUES
