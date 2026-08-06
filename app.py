"""Home page for the Streamlit IT Operations Toolkit."""

import streamlit as st


st.set_page_config(
    page_title="IT Operations Toolkit",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("IT Operations Toolkit")
st.write(
    "A collection of small Python utilities for network calculations, "
    "technical log analysis and structured IT-support decisions."
)

st.divider()

st.subheader("Available now")
subnet_column, log_column, ticket_column = st.columns(3)

with subnet_column:
    with st.container(border=True):
        st.markdown("### Network Subnet Calculator")
        st.write(
            "Calculate a network, broadcast address, host range, address count "
            "and IPv4 classification from CIDR input."
        )
        st.page_link(
            "pages/1_Network_Subnet_Calculator.py",
            label="Open the subnet calculator",
        )

with log_column:
    with st.container(border=True):
        st.markdown("### IT Log Analyser")
        st.write(
            "Summarise sample or uploaded text logs, extract common fields and "
            "filter the parsed entries."
        )
        st.page_link(
            "pages/2_IT_Log_Analyser.py",
            label="Open the log analyser",
        )

with ticket_column:
    with st.container(border=True):
        st.markdown("### Support Ticket Prioritiser")
        st.write(
            "Assign a transparent demonstrative P1–P4 priority using four "
            "documented operational factors."
        )
        st.page_link(
            "pages/3_Support_Ticket_Prioritiser.py",
            label="Open the ticket prioritiser",
        )

st.subheader("Project principles")
principle_one, principle_two, principle_three = st.columns(3)

with principle_one:
    st.markdown("**Clear logic**")
    st.write("The interface is kept separate from the reusable Python functions.")

with principle_two:
    st.markdown("**Tested behaviour**")
    st.write("Calculation and parsing functions are covered by repeatable unit tests.")

with principle_three:
    st.markdown("**Honest scope**")
    st.write("Each utility states its assumptions and does not claim to replace professional tools.")

st.caption("Built as a practical learning project by Abraham Kaunda.")
