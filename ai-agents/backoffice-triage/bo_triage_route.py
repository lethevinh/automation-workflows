"""The router: a deterministic rule table with the LLM at the edges.

The shipped classifier is a rule table (``RouterConfig.rules``): it scans the
lowercased subject and body for regex patterns and keeps the strongest match.
When the strongest match is at or above the configured threshold the rule table
decides; when it is below, the decision is handed to the **LLM edge** — which in
the mock lane is a deterministic stand-in that returns a confident decision for
the same message every time. That keeps the demo reproducible while showing
exactly where a live model would slot in.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from bo_triage_config import RouterConfig


@dataclass(frozen=True)
class Route:
    """The routing decision for one message."""

    queue: str
    confidence: float
    classifier: str
    reason: str


def classify(subject: str, body: str, router: RouterConfig) -> Route:
    """Classify one message into a queue.

    Deterministic: the same text always yields the same route. Ties are broken
    by rule order (the first rule of equal strength wins), so the rule table in
    ``config/router.json`` fully explains every outcome.
    """

    text = f"{subject}\n{body}".lower()

    best = None
    for rule in router.rules:
        if re.search(rule.pattern, text):
            if best is None or rule.strength > best.strength:
                best = rule

    if best is None:
        return Route(
            queue=router.default_queue,
            confidence=0.5,
            classifier="rules",
            reason="no rule matched",
        )

    if best.strength >= router.classifier_threshold:
        return Route(
            queue=best.queue,
            confidence=best.strength,
            classifier="rules",
            reason=f"matched {best.reason}",
        )

    # Below threshold: the LLM edge decides. The mock classifier is
    # deterministic and returns the strongest-signal queue with high confidence.
    return Route(
        queue=best.queue,
        confidence=0.9,
        classifier="llm-mock",
        reason=(
            f"matched {best.reason} ({best.strength:.2f} < "
            f"{router.classifier_threshold:.2f}) -> LLM classifier (mock)"
        ),
    )
