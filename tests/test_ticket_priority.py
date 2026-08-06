"""Unit tests for the demonstrative P1–P4 priority model."""

import unittest

from toolkit.ticket_priority import TicketInputError, prioritise_ticket


class PrioritiseTicketTests(unittest.TestCase):
    def test_assigns_p4_at_minimum_score(self) -> None:
        result = prioritise_ticket("Low", "Low", "One user", "Low")

        self.assertEqual(result.priority, "P4")
        self.assertEqual(result.score, 4)

    def test_assigns_p4_at_upper_boundary(self) -> None:
        result = prioritise_ticket("Moderate", "Low", "One user", "Standard")

        self.assertEqual(result.priority, "P4")
        self.assertEqual(result.score, 6)

    def test_assigns_p3_at_lower_boundary(self) -> None:
        result = prioritise_ticket("Moderate", "Normal", "One user", "Standard")

        self.assertEqual(result.priority, "P3")
        self.assertEqual(result.score, 7)

    def test_assigns_p3_at_upper_boundary(self) -> None:
        result = prioritise_ticket("Moderate", "Normal", "Small group", "Important")

        self.assertEqual(result.priority, "P3")
        self.assertEqual(result.score, 9)

    def test_assigns_p2_at_lower_boundary(self) -> None:
        result = prioritise_ticket("High", "High", "Small group", "Standard")

        self.assertEqual(result.priority, "P2")
        self.assertEqual(result.score, 10)

    def test_assigns_p2_at_upper_boundary(self) -> None:
        result = prioritise_ticket(
            "High",
            "High",
            "Department or team",
            "Business-critical",
        )

        self.assertEqual(result.priority, "P2")
        self.assertEqual(result.score, 13)

    def test_assigns_p1_at_lower_boundary(self) -> None:
        result = prioritise_ticket(
            "Widespread",
            "High",
            "Department or team",
            "Business-critical",
        )

        self.assertEqual(result.priority, "P1")
        self.assertEqual(result.score, 14)

    def test_assigns_p1_at_maximum_score(self) -> None:
        result = prioritise_ticket(
            "Widespread",
            "Immediate",
            "Multiple departments",
            "Business-critical",
        )

        self.assertEqual(result.priority, "P1")
        self.assertEqual(result.score, 16)

    def test_normalises_case_and_surrounding_spaces(self) -> None:
        result = prioritise_ticket(
            " high ",
            " immediate ",
            " SMALL GROUP ",
            " business-critical ",
        )

        self.assertEqual(result.priority, "P2")
        self.assertEqual(result.score, 13)
        self.assertEqual(result.impact, "High")

    def test_explanation_contains_each_factor_and_score(self) -> None:
        result = prioritise_ticket(
            "Widespread",
            "High",
            "Department or team",
            "Business-critical",
        )

        self.assertIn("score of 14/16", result.explanation)
        self.assertIn("impact Widespread (4)", result.explanation)
        self.assertIn("urgency High (3)", result.explanation)
        self.assertIn("affected users Department or team (3)", result.explanation)
        self.assertIn("service criticality Business-critical (4)", result.explanation)

    def test_rejects_unknown_factor_values(self) -> None:
        invalid_cases = (
            ("Severe", "Normal", "One user", "Standard"),
            ("Low", "Urgent", "One user", "Standard"),
            ("Low", "Normal", "Everyone", "Standard"),
            ("Low", "Normal", "One user", "Essential"),
        )

        for values in invalid_cases:
            with self.subTest(values=values):
                with self.assertRaises(TicketInputError):
                    prioritise_ticket(*values)


if __name__ == "__main__":
    unittest.main()
