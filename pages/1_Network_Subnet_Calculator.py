"""Streamlit interface for the IPv4 subnet calculator."""

import streamlit as st

from toolkit import SubnetInputError, analyse_subnet


st.title("Network Subnet Calculator")
st.write(
    "Calculate the key details of an IPv4 network from an address and CIDR prefix. "
    "The entered address can be any host within the network."
)

with st.sidebar:
    st.header("About this tool")
    st.write(
        "This utility uses Python's standard `ipaddress` module. It supports "
        "IPv4 prefixes from `/0` through `/32`."
    )
    st.info("The application does not save submitted addresses.")

with st.form("subnet-calculator-form"):
    submitted_value = st.text_input(
        "IPv4 address and CIDR prefix",
        value="192.168.10.25/24",
        placeholder="For example: 192.168.10.25/24",
        help="Enter one IPv4 address followed by a numeric prefix between 0 and 32.",
    )
    calculate = st.form_submit_button(
        "Calculate subnet",
        type="primary",
        use_container_width=True,
    )

if calculate:
    try:
        result = analyse_subnet(submitted_value)
    except SubnetInputError as error:
        st.error(str(error))
    else:
        st.success(f"Calculated the network containing {result.cidr_notation}.")

        st.subheader("Network details")
        network_column, broadcast_column, mask_column = st.columns(3)
        address_values = (
            (network_column, "Network address", result.network_address),
            (broadcast_column, "Broadcast address", result.broadcast_address),
            (mask_column, "Subnet mask", result.subnet_mask),
        )
        for column, label, value in address_values:
            with column:
                st.caption(label)
                st.code(value, language=None)

        count_column, usable_column, prefix_column = st.columns(3)
        count_column.metric("Total addresses", f"{result.total_addresses:,}")
        usable_column.metric("Usable hosts", f"{result.usable_hosts:,}")
        prefix_column.metric("Prefix length", f"/{result.prefix_length}")

        st.subheader("Usable host range")
        first_host_column, last_host_column = st.columns(2)
        with first_host_column:
            st.caption("First usable host")
            st.code(result.first_usable_host, language=None)
        with last_host_column:
            st.caption("Last usable host")
            st.code(result.last_usable_host, language=None)

        st.subheader("Address classification")
        st.info(f"{result.entered_address} is classified as **{result.classification}**.")

        if result.prefix_length == 31:
            st.warning(
                "A `/31` is treated as a point-to-point network. Both addresses "
                "are counted as usable, following modern point-to-point behaviour."
            )
        elif result.prefix_length == 32:
            st.warning(
                "A `/32` represents a single-host route, so the network, broadcast "
                "and usable host values refer to the same address."
            )

with st.expander("Example inputs and expected use"):
    st.markdown(
        """
        | Example | What it demonstrates |
        | --- | --- |
        | `192.168.10.25/24` | Private network with 254 traditional usable hosts |
        | `10.0.0.5/30` | Small four-address subnet |
        | `10.0.0.4/31` | Point-to-point network |
        | `8.8.8.8/24` | Public IPv4 classification |
        | `127.0.0.1/8` | Special-purpose loopback range |
        """
    )

with st.expander("Limitations"):
    st.markdown(
        """
        - IPv6 is not supported in this version.
        - Classification is intentionally broad and is not a live ownership lookup.
        - The results are a calculation aid, not approval for a production network design.
        """
    )
