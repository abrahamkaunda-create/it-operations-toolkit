"""Navigation entry point for the Streamlit IT Operations Toolkit."""

import streamlit as st


st.set_page_config(
    page_title="IT Operations Toolkit",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("overview.py", title="Overview", icon="🏠", default=True),
    st.Page(
        "pages/1_Network_Subnet_Calculator.py",
        title="Network Subnet Calculator",
        icon="🌐",
    ),
    st.Page(
        "pages/2_IT_Log_Analyser.py",
        title="IT Log Analyser",
        icon="📋",
    ),
    st.Page(
        "pages/3_Support_Ticket_Prioritiser.py",
        title="Support Ticket Prioritiser",
        icon="🎫",
    ),
]

navigation = st.navigation(pages)
navigation.run()
