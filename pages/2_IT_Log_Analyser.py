"""Streamlit interface for the plain-text IT log analyser."""

from pathlib import Path

import streamlit as st

from toolkit import LogInputError, decode_log_bytes, filter_entries, parse_log


SAMPLE_LOG_PATH = (
    Path(__file__).resolve().parents[1] / "sample_data" / "sample_system.log"
)
MAX_UPLOAD_BYTES = 1_000_000
MAX_DISPLAY_ENTRIES = 500


st.title("IT Log Analyser")
st.write(
    "Summarise a plain-text technical log, count severity levels, extract "
    "timestamps and valid IPv4 addresses, and filter the parsed entries."
)
st.warning(
    "Use the included sample or a sanitised test log. Do not upload sensitive "
    "production logs, credentials or personal information to this public demonstration."
)

with st.sidebar:
    st.header("Scope")
    st.write(
        "This utility performs deterministic text parsing. It does not detect "
        "attacks, identify root causes or replace a monitoring platform."
    )
    st.info("Uploaded content is processed for the current session and is not saved by the app.")

source = st.radio(
    "Log source",
    options=("Included sample", "Upload a text log"),
    horizontal=True,
)

log_text = ""
source_name = ""

if source == "Included sample":
    sample_text = SAMPLE_LOG_PATH.read_text(encoding="utf-8")
    log_text = st.text_area(
        "Sample log content",
        value=sample_text,
        height=280,
        help="You can edit this sample before running the analysis.",
    )
    source_name = SAMPLE_LOG_PATH.name
else:
    uploaded_file = st.file_uploader(
        "Upload a UTF-8 `.log` or `.txt` file",
        type=("log", "txt"),
        help="Maximum size for this demonstration: 1 MB.",
    )
    if uploaded_file is not None:
        if uploaded_file.size > MAX_UPLOAD_BYTES:
            st.error("The selected file is larger than the 1 MB demonstration limit.")
        else:
            try:
                log_text = decode_log_bytes(uploaded_file.getvalue())
            except LogInputError as error:
                st.error(str(error))
            else:
                source_name = uploaded_file.name
                st.text_area("Uploaded log preview", value=log_text, height=260, disabled=True)

if st.button("Analyse log", type="primary", use_container_width=True):
    try:
        analysis = parse_log(log_text)
    except LogInputError as error:
        st.error(str(error))
    else:
        st.session_state["log_analysis"] = analysis
        st.session_state["log_source_name"] = source_name or "entered text"

analysis = st.session_state.get("log_analysis")
if analysis is not None:
    st.success(f"Analysis completed for {st.session_state['log_source_name']}.")

    st.subheader("Summary")
    line_column, error_column, warning_column, ip_column = st.columns(4)
    line_column.metric("Analysed entries", f"{analysis.non_empty_lines:,}")
    error_column.metric("Errors", f"{analysis.severity_counts['ERROR']:,}")
    warning_column.metric("Warnings", f"{analysis.severity_counts['WARNING']:,}")
    ip_column.metric("Unique IPv4 addresses", f"{analysis.unique_ip_count:,}")

    severity_rows = [
        {"Severity": severity, "Count": count}
        for severity, count in analysis.severity_counts.items()
        if count > 0
    ]
    ip_rows = [
        {"IPv4 address": address, "Occurrences": count}
        for address, count in analysis.ip_counts.items()
    ]

    severity_column, address_column = st.columns(2)
    with severity_column:
        st.markdown("#### Severity breakdown")
        st.dataframe(severity_rows, hide_index=True, use_container_width=True)
    with address_column:
        st.markdown("#### Extracted IPv4 addresses")
        if ip_rows:
            st.dataframe(ip_rows, hide_index=True, use_container_width=True)
        else:
            st.info("No valid IPv4 addresses were found.")

    st.subheader("Filter entries")
    severity_filter_column, ip_filter_column, keyword_filter_column = st.columns(3)

    available_severities = [
        severity
        for severity, count in analysis.severity_counts.items()
        if count > 0
    ]
    selected_severity = severity_filter_column.selectbox(
        "Severity",
        options=("All", *available_severities),
    )
    selected_ip = ip_filter_column.selectbox(
        "IPv4 address",
        options=("All", *analysis.ip_counts.keys()),
    )
    keyword = keyword_filter_column.text_input(
        "Keyword",
        placeholder="For example: backup",
    )

    filtered_entries = filter_entries(
        analysis.entries,
        severity=None if selected_severity == "All" else selected_severity,
        ip_address=None if selected_ip == "All" else selected_ip,
        keyword=keyword,
    )

    st.write(f"Showing **{len(filtered_entries):,}** matching entries.")
    displayed_entries = filtered_entries[:MAX_DISPLAY_ENTRIES]
    entry_rows = [
        {
            "Line": entry.line_number,
            "Timestamp": entry.timestamp or "—",
            "Severity": entry.severity,
            "IPv4 addresses": ", ".join(entry.ip_addresses) or "—",
            "Entry": entry.raw_text,
        }
        for entry in displayed_entries
    ]

    if entry_rows:
        st.dataframe(entry_rows, hide_index=True, use_container_width=True, height=420)
    else:
        st.info("No entries match the selected filters.")

    if len(filtered_entries) > MAX_DISPLAY_ENTRIES:
        st.caption(
            f"Only the first {MAX_DISPLAY_ENTRIES:,} matching entries are displayed "
            "to keep the demonstration responsive."
        )

with st.expander("Recognised patterns"):
    st.markdown(
        """
        - ISO-style timestamps such as `2026-08-06 08:15:21`
        - `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR` and `CRITICAL`
        - `WARN` is normalised to `WARNING`
        - `FATAL` is normalised to `CRITICAL`
        - Valid dotted-decimal IPv4 addresses
        - Lines without a recognised severity are retained as `UNCLASSIFIED`
        """
    )
