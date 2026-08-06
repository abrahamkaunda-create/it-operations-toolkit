"""Transparent scoring logic for the demonstrative ticket prioritiser."""

from __future__ import annotations

from dataclasses import dataclass


IMPACT_SCORES = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Widespread": 4,
}

URGENCY_SCORES = {
    "Low": 1,
    "Normal": 2,
    "High": 3,
    "Immediate": 4,
}

AFFECTED_USER_SCORES = {
    "One user": 1,
    "Small group": 2,
    "Department or team": 3,
    "Multiple departments": 4,
}

SERVICE_CRITICALITY_SCORES = {
    "Low": 1,
    "Standard": 2,
    "Important": 3,
    "Business-critical": 4,
}

PRIORITY_BANDS = {
    "P1": (14, 16),
    "P2": (10, 13),
    "P3": (7, 9),
    "P4": (4, 6),
}

PRIORITY_DESCRIPTIONS = {
    "P1": "Critical disruption requiring the fastest response in this demonstration.",
    "P2": "Significant disruption requiring prompt attention.",
    "P3": "Moderate or contained disruption that should be scheduled appropriately.",
    "P4": "Routine or low-impact work that can follow the normal support queue.",
}

MAXIMUM_SCORE = 16


class TicketInputError(ValueError):
    """Raised when a ticket factor is not one of the documented choices."""


@dataclass(frozen=True)
class PriorityResult:
    """The calculated priority and transparent factor breakdown."""

    priority: str
    score: int
    impact: str
    urgency: str
    affected_users: str
    service_criticality: str
    factor_scores: dict[str, int]
    explanation: str
    priority_description: str


def _normalise_choice(value: str, choices: dict[str, int], field_name: str) -> str:
    if not isinstance(value, str):
        raise TicketInputError(f"{field_name} must be selected from the documented choices.")

    cleaned_value = value.strip().casefold()
    for choice in choices:
        if choice.casefold() == cleaned_value:
            return choice

    available_choices = ", ".join(choices)
    raise TicketInputError(
        f"Unknown {field_name.lower()} value: {value!r}. Choose from: {available_choices}."
    )


def _priority_from_score(score: int) -> str:
    for priority, (minimum, maximum) in PRIORITY_BANDS.items():
        if minimum <= score <= maximum:
            return priority

    raise TicketInputError("The calculated score falls outside the supported priority bands.")


def prioritise_ticket(
    impact: str,
    urgency: str,
    affected_users: str,
    service_criticality: str,
) -> PriorityResult:
    """Assign a demonstrative P1–P4 priority from four equally weighted factors.

    This function models a transparent learning exercise. It is not an official
    ITIL matrix, service-level agreement or employer-specific process.
    """

    selected_impact = _normalise_choice(impact, IMPACT_SCORES, "Impact")
    selected_urgency = _normalise_choice(urgency, URGENCY_SCORES, "Urgency")
    selected_users = _normalise_choice(
        affected_users,
        AFFECTED_USER_SCORES,
        "Affected users",
    )
    selected_criticality = _normalise_choice(
        service_criticality,
        SERVICE_CRITICALITY_SCORES,
        "Service criticality",
    )

    factor_scores = {
        "Impact": IMPACT_SCORES[selected_impact],
        "Urgency": URGENCY_SCORES[selected_urgency],
        "Affected users": AFFECTED_USER_SCORES[selected_users],
        "Service criticality": SERVICE_CRITICALITY_SCORES[selected_criticality],
    }
    score = sum(factor_scores.values())
    priority = _priority_from_score(score)
    minimum, maximum = PRIORITY_BANDS[priority]

    explanation = (
        f"{priority} was assigned from a score of {score}/{MAXIMUM_SCORE}: "
        f"impact {selected_impact} ({factor_scores['Impact']}), "
        f"urgency {selected_urgency} ({factor_scores['Urgency']}), "
        f"affected users {selected_users} ({factor_scores['Affected users']}) and "
        f"service criticality {selected_criticality} "
        f"({factor_scores['Service criticality']}). "
        f"The {priority} demonstration band covers scores from {minimum} to {maximum}."
    )

    return PriorityResult(
        priority=priority,
        score=score,
        impact=selected_impact,
        urgency=selected_urgency,
        affected_users=selected_users,
        service_criticality=selected_criticality,
        factor_scores=factor_scores,
        explanation=explanation,
        priority_description=PRIORITY_DESCRIPTIONS[priority],
    )
