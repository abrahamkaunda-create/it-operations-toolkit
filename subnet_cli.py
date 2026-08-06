"""Small command-line demonstration of the subnet calculator."""

from __future__ import annotations

import argparse
import sys

from toolkit import SubnetInputError, analyse_subnet


def display_result(value: str) -> int:
    """Calculate and print one subnet result, returning a process exit code."""

    try:
        result = analyse_subnet(value)
    except SubnetInputError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    rows = (
        ("Entered address", result.entered_address),
        ("CIDR notation", result.cidr_notation),
        ("Subnet mask", result.subnet_mask),
        ("Network address", result.network_address),
        ("Broadcast address", result.broadcast_address),
        ("First usable host", result.first_usable_host),
        ("Last usable host", result.last_usable_host),
        ("Total addresses", str(result.total_addresses)),
        ("Usable hosts", str(result.usable_hosts)),
        ("Classification", result.classification),
    )

    label_width = max(len(label) for label, _ in rows)
    for label, output in rows:
        print(f"{label:<{label_width}} : {output}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate details for an IPv4 address and CIDR prefix."
    )
    parser.add_argument(
        "network",
        nargs="?",
        help="IPv4 address in CIDR notation, for example 192.168.10.25/24",
    )
    arguments = parser.parse_args()

    value = arguments.network
    if value is None:
        value = input("IPv4 address/CIDR: ")

    return display_result(value)


if __name__ == "__main__":
    raise SystemExit(main())
