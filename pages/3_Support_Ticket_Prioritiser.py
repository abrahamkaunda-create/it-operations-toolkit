"""Streamlit interface for the demonstrative support ticket prioritiser."""

import streamlit as st

from toolkit import TicketInputError, prioritise_ticket
from toolkit.ticket_priority import (
    AFFECTED_USER_SCORES,
    IMPACT_SCORES,
    MAXIMUM_SCORE,
    PRIORITY_BANDS,
    PRIORITY_DESCRIPTIONS,
    SERVICE_CRITICALITY_SCORES,
    URGENCY_SCORES,
)


st.title("Support Ticket Prioritiser")
st.write(
    "Use four documented factors to produce a transparent demonstrative "
    "P1–P4 priority and explanation."
)
st.warning(
    "This is a learning model, not an official ITIL matrix, service-level "
    "agreement or employer-specific support process. Do not enter personal or sensitive data."
)

with st.sidebar:
    st.header("How scoring works")
    st.write(
        "Impact, urgency, affected users and service criticality each contribute "
        "between one and four points. The combined score maps to P1–P4."
    )
    st.info("The optional ticket summary does not affect the calculated score.")

with st.form("ticket-priority-form"):
    ticket_summary = st.text_input(
        "Ticket summary (optional)",
        placeholder="For example: Department cannot access shared drive",
        help="Used only as a label for the displayed result.",
    )

    impact_column, urgency_column = st.columns(2)
    affected_column, criticality_column = st.columns(2)

    impact = impact_column.selectbox(
        "Impact",
        options=tuple(IMPACT_SCORES),
        index=1,
        help="How severely normal work or service functionality is disrupted.",
    )
    urgency = urgency_column.selectbox(
        "Urgency",
        options=tuple(URGENCY_SCORES),
        index=1,
        help="How quickly the issue requires attention in this demonstration.",
    )
    affected_users = affected_column.selectbox(
        "Affected users",
        options=tuple(AFFECTED_USER_SCORES),
        index=1,
        help="The approximate organisational scope of the disruption.",
    )
    service_criticality = criticality_column.selectbox(
        "Service criticality",
        options=tuple(SERVICE_CRITICALITY_SCORES),
        index=1,
        help="How important the affected service is to normal operations.",
    )

    calculate = st.form_submit_button(
        "Calculate demonstration priority",
        type="primary",
        use_container_width=True,
    )

if calculate:
    try:
        result = prioritise_ticket(
            impact,
            urgency,
            affected_users,
            service_criticality,
        )
    except TicketInputError as error:
        st.error(str(error))
    else:
        st.session_state["ticket_priority_result"] = result
        st.session_state["ticket_priority_summary"] = (
            ticket_summary.strip() or "Untitled demonstration ticket"
        )

result = st.session_state.get("ticket_priority_result")
if result is not None:
    st.success(f"Priority calculated for: {st.session_state['ticket_priority_summary']}")

    priority_column, score_column = st.columns(2)
    priority_column.metric("Suggested priority", result.priority)
    score_column.metric("Weighted score", f"{result.score}/{MAXIMUM_SCORE}")
    st.progress(result.score / MAXIMUM_SCORE)

    st.info(result.priority_description)
    st.write(result.explanation)

    st.subheader("Factor breakdown")
    factor_rows = [
        {
            "Factor": "Impact",
            "Selected value": result.impact,
            "Points": result.factor_scores["Impact"],
        },
        {
            "Factor": "Urgency",
            "Selected value": result.urgency,
            "Points": result.factor_scores["Urgency"],
        },
        {
            "Factor": "Affected users",
            "Selected value": result.affected_users,
            "Points": result.factor_scores["Affected users"],
        },
        {
            "Factor": "Service criticality",
            "Selected value": result.service_criticality,
            "Points": result.factor_scores["Service criticality"],
        },
    ]
    st.dataframe(factor_rows, hide_index=True, use_container_width=True)

st.subheader("Demonstration priority bands")
band_rows = [
    {
        "Priority": priority,
        "Score range": f"{minimum}–{maximum}",
        "Meaning": PRIORITY_DESCRIPTIONS[priority],
    }
    for priority, (minimum, maximum) in PRIORITY_BANDS.items()
]
st.dataframe(band_rows, hide_index=True, use_container_width=True)

with st.expander("Model limitations"):
    st.markdown(
        """
        - Each factor has equal weight for clarity; real organisations may weight them differently.
        - No contractual response or resolution times are assigned.
        - A real service desk would use its approved impact-and-urgency matrix and escalation rules.
        - Human judgement and additional context remain necessary.
        """
    )
