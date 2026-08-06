"""IPv4 subnet calculations used by the toolkit interface and tests."""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network, ip_interface


PRIVATE_NETWORKS = (
    IPv4Network("10.0.0.0/8"),
    IPv4Network("172.16.0.0/12"),
    IPv4Network("192.168.0.0/16"),
)


class SubnetInputError(ValueError):
    """Raised when a subnet value cannot be interpreted safely."""


@dataclass(frozen=True)
class SubnetResult:
    """The calculated details for one IPv4 address and CIDR prefix."""

    entered_address: str
    cidr_notation: str
    prefix_length: int
    subnet_mask: str
    network_address: str
    broadcast_address: str
    first_usable_host: str
    last_usable_host: str
    total_addresses: int
    usable_hosts: int
    classification: str


def classify_address(address: IPv4Address) -> str:
    """Classify an address as RFC 1918 private, public or special-purpose."""

    if any(address in network for network in PRIVATE_NETWORKS):
        return "Private (RFC 1918)"

    if address.is_global:
        return "Public"

    return "Special-purpose"


def _usable_host_details(network: IPv4Network) -> tuple[IPv4Address, IPv4Address, int]:
    """Return the first host, last host and usable count for a network.

    Traditional subnets reserve the network and broadcast addresses. A /31 is
    treated as a point-to-point network where both addresses are usable, and a
    /32 represents one host route.
    """

    if network.prefixlen <= 30:
        return (
            network.network_address + 1,
            network.broadcast_address - 1,
            network.num_addresses - 2,
        )

    if network.prefixlen == 31:
        return network.network_address, network.broadcast_address, 2

    return network.network_address, network.network_address, 1


def analyse_subnet(value: str) -> SubnetResult:
    """Calculate subnet information from an IPv4 address in CIDR notation.

    Args:
        value: An IPv4 address and numeric prefix, for example
            ``192.168.10.25/24``.

    Raises:
        SubnetInputError: If the value is empty, is not IPv4, or does not use a
            valid prefix between 0 and 32.
    """

    if not isinstance(value, str):
        raise SubnetInputError("Enter the address as text, for example 192.168.10.25/24.")

    cleaned_value = value.strip()
    if not cleaned_value:
        raise SubnetInputError("Enter an IPv4 address with a CIDR prefix.")

    address_text, separator, prefix_text = cleaned_value.partition("/")
    if not separator:
        raise SubnetInputError("Include a CIDR prefix, for example /24.")

    if ":" in address_text:
        raise SubnetInputError("Only IPv4 addresses are supported in this version.")

    if not prefix_text.isdigit():
        raise SubnetInputError("Use a numeric CIDR prefix between 0 and 32.")

    prefix_length = int(prefix_text)
    if not 0 <= prefix_length <= 32:
        raise SubnetInputError("The IPv4 CIDR prefix must be between 0 and 32.")

    try:
        interface = ip_interface(cleaned_value)
    except ValueError as error:
        raise SubnetInputError(
            "Enter a valid IPv4 address in CIDR notation, for example 192.168.10.25/24."
        ) from error

    if not isinstance(interface.ip, IPv4Address):
        raise SubnetInputError("Only IPv4 addresses are supported in this version.")

    network = interface.network
    first_host, last_host, usable_hosts = _usable_host_details(network)

    return SubnetResult(
        entered_address=str(interface.ip),
        cidr_notation=f"{interface.ip}/{network.prefixlen}",
        prefix_length=network.prefixlen,
        subnet_mask=str(network.netmask),
        network_address=str(network.network_address),
        broadcast_address=str(network.broadcast_address),
        first_usable_host=str(first_host),
        last_usable_host=str(last_host),
        total_addresses=network.num_addresses,
        usable_hosts=usable_hosts,
        classification=classify_address(interface.ip),
    )
