"""Unit tests for the IPv4 subnet calculation logic."""

import unittest

from toolkit.subnet import SubnetInputError, analyse_subnet


class AnalyseSubnetTests(unittest.TestCase):
    def test_calculates_private_24_network(self) -> None:
        result = analyse_subnet("192.168.10.25/24")

        self.assertEqual(result.entered_address, "192.168.10.25")
        self.assertEqual(result.subnet_mask, "255.255.255.0")
        self.assertEqual(result.network_address, "192.168.10.0")
        self.assertEqual(result.broadcast_address, "192.168.10.255")
        self.assertEqual(result.first_usable_host, "192.168.10.1")
        self.assertEqual(result.last_usable_host, "192.168.10.254")
        self.assertEqual(result.total_addresses, 256)
        self.assertEqual(result.usable_hosts, 254)
        self.assertEqual(result.classification, "Private (RFC 1918)")

    def test_calculates_public_network(self) -> None:
        result = analyse_subnet("8.8.8.8/24")

        self.assertEqual(result.network_address, "8.8.8.0")
        self.assertEqual(result.classification, "Public")

    def test_calculates_30_network(self) -> None:
        result = analyse_subnet("10.0.0.5/30")

        self.assertEqual(result.network_address, "10.0.0.4")
        self.assertEqual(result.broadcast_address, "10.0.0.7")
        self.assertEqual(result.first_usable_host, "10.0.0.5")
        self.assertEqual(result.last_usable_host, "10.0.0.6")
        self.assertEqual(result.usable_hosts, 2)

    def test_treats_31_as_point_to_point_network(self) -> None:
        result = analyse_subnet("10.0.0.4/31")

        self.assertEqual(result.first_usable_host, "10.0.0.4")
        self.assertEqual(result.last_usable_host, "10.0.0.5")
        self.assertEqual(result.usable_hosts, 2)

    def test_treats_32_as_single_host_route(self) -> None:
        result = analyse_subnet("10.0.0.4/32")

        self.assertEqual(result.network_address, "10.0.0.4")
        self.assertEqual(result.broadcast_address, "10.0.0.4")
        self.assertEqual(result.first_usable_host, "10.0.0.4")
        self.assertEqual(result.last_usable_host, "10.0.0.4")
        self.assertEqual(result.usable_hosts, 1)

    def test_identifies_special_purpose_address(self) -> None:
        result = analyse_subnet("127.0.0.1/8")

        self.assertEqual(result.classification, "Special-purpose")

    def test_ignores_surrounding_whitespace(self) -> None:
        result = analyse_subnet("  172.16.4.20/20  ")

        self.assertEqual(result.network_address, "172.16.0.0")
        self.assertEqual(result.classification, "Private (RFC 1918)")

    def test_rejects_invalid_inputs(self) -> None:
        invalid_values = (
            "",
            "192.168.1.10",
            "999.168.1.10/24",
            "192.168.1.10/33",
            "192.168.1.10/not-a-prefix",
            "192.168.1.10/255.255.255.0",
            "2001:db8::1/64",
        )

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(SubnetInputError):
                    analyse_subnet(value)


if __name__ == "__main__":
    unittest.main()
