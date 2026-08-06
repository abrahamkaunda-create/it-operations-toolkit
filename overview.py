"""Overview page for the Streamlit IT Operations Toolkit."""

import streamlit as st


st.title("IT Operations Toolkit")
st.write(
    "Three small Python utilities demonstrating network calculations, "
    "technical log analysis and structured IT-support decisions."
)

source_column, portfolio_column = st.columns(2)
with source_column:
    st.link_button(
        "View source on GitHub",
        "https://github.com/abrahamkaunda-create/it-operations-toolkit",
        use_container_width=True,
    )
with portfolio_column:
    st.link_button(
        "View Abraham's portfolio",
        "https://abrahamkaunda-create.github.io/",
        use_container_width=True,
    )

st.divider()

st.subheader("Utilities")
subnet_column, log_column, ticket_column = st.columns(3, gap="large")

with subnet_column:
    with st.container(border=True):
        st.markdown("### 🌐 Subnet calculator")
        st.write("Calculate IPv4 network details from an address and CIDR prefix.")
        st.page_link(
            "pages/1_Network_Subnet_Calculator.py",
            label="Open calculator",
            use_container_width=True,
        )

with log_column:
    with st.container(border=True):
        st.markdown("### 📋 Log analyser")
        st.write("Parse sample or uploaded text logs and filter extracted fields.")
        st.page_link(
            "pages/2_IT_Log_Analyser.py",
            label="Open analyser",
            use_container_width=True,
        )

with ticket_column:
    with st.container(border=True):
        st.markdown("### 🎫 Ticket prioritiser")
        st.write("Explore a transparent P1–P4 support-priority scoring model.")
        st.page_link(
            "pages/3_Support_Ticket_Prioritiser.py",
            label="Open prioritiser",
            use_container_width=True,
        )

st.subheader("Project principles")
principle_one, principle_two, principle_three = st.columns(3)

with principle_one:
    st.markdown("**Clear logic**")
    st.write("The interfaces are kept separate from the reusable Python functions.")

with principle_two:
    st.markdown("**Tested behaviour**")
    st.write("Thirty unit tests cover calculations, parsing and scoring boundaries.")

with principle_three:
    st.markdown("**Honest scope**")
    st.write("Each utility documents its assumptions and practical limitations.")

st.caption("Built as a practical learning project by Abraham Kaunda.")
