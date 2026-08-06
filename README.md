# IT Operations Toolkit

A collection of small Python utilities for networking, technical log analysis and structured IT-support decisions.

## Utilities

### Network Subnet Calculator

Accepts an IPv4 address in CIDR notation and returns network and broadcast addresses, subnet mask, usable host range, address counts and broad address classification.

### IT Log Analyser

Processes the included sample or an uploaded UTF-8 text log. It counts severity levels, extracts ISO-style timestamps and valid IPv4 addresses, and filters entries by severity, address and keyword.

The analyser is deterministic text parsing. It does not claim to detect attacks, establish root causes or replace a production monitoring platform.

### Support Ticket Prioritiser

Uses impact, urgency, affected users and service criticality to assign a transparent demonstrative P1–P4 priority. Every factor contributes one to four points, and the result includes the complete scoring explanation.

The priority model is not an official ITIL matrix, service-level agreement or employer-specific process.

## Run the application locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

Install Streamlit and start the application:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will display the local address to open in your browser.

## Command-line subnet calculator

The subnet logic can also be used without Streamlit:

```bash
python subnet_cli.py 192.168.10.25/24
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```

The test suite covers subnet edge cases, invalid network input, log parsing and filtering, UTF-8 decoding, priority boundaries, input validation and scoring explanations.

## Project structure

```text
.
├── .streamlit/
│   └── config.toml
├── pages/
│   ├── 1_Network_Subnet_Calculator.py
│   ├── 2_IT_Log_Analyser.py
│   └── 3_Support_Ticket_Prioritiser.py
├── sample_data/
│   └── sample_system.log
├── tests/
│   ├── test_log_analyser.py
│   ├── test_subnet.py
│   └── test_ticket_priority.py
├── toolkit/
│   ├── __init__.py
│   ├── log_analyser.py
│   ├── subnet.py
│   └── ticket_priority.py
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
└── subnet_cli.py
```

## Design decisions

- Keeps Streamlit presentation separate from reusable and tested Python logic.
- Uses Python's standard `ipaddress` module for subnet calculations and IPv4 validation.
- Preserves unrecognised log lines instead of silently discarding them.
- Processes uploaded log content in memory and does not write it to the repository.
- Uses visible ticket-priority scores and bands rather than hidden or unexplained rules.
- Documents assumptions and limitations alongside each utility.

## Limitations

- The subnet calculator supports IPv4 only.
- Log parsing targets documented demonstration patterns rather than every vendor format.
- Log uploads are limited to 1 MB in the interface.
- Public demonstrations should only receive sample or sanitised data.
- Ticket priority is demonstrative and must not be presented as an organisation's approved process.
- These utilities are learning and operational aids, not production approval or monitoring systems.

## Possible future extensions

- Windows system-information parser
- File-integrity hash checker
- Additional log formats and export options
