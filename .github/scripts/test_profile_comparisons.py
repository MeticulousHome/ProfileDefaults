"""Focused tests for the profile comparison corpus migration."""

from __future__ import annotations

import unittest
from pathlib import Path

from check_profile_comparisons import (
    NUMERIC_TRIGGER_TYPES,
    comparison_errors,
    migrate_profile,
)


class ProfileComparisonTests(unittest.TestCase):
    def test_migrates_legacy_and_omitted_numeric_comparisons(self) -> None:
        triggers = []
        for trigger_type in sorted(NUMERIC_TRIGGER_TYPES):
            triggers.extend(
                [
                    {
                        "type": trigger_type,
                        "value": 0,
                        "comparison": ">=",
                        "relative": False,
                    },
                    {"type": trigger_type, "value": 1, "relative": True},
                    {
                        "type": trigger_type,
                        "value": 2,
                        "comparison": "<=",
                        "relative": False,
                    },
                ]
            )
        triggers.append({"type": "user_interaction", "value": 3})
        profile = {"name": "unchanged", "stages": [{"exit_triggers": triggers}]}

        migrated, count = migrate_profile(profile)

        self.assertEqual(count, len(NUMERIC_TRIGGER_TYPES) * 2)
        self.assertNotIn("comparison", profile["stages"][0]["exit_triggers"][1])
        for index in range(0, len(NUMERIC_TRIGGER_TYPES) * 3, 3):
            migrated_triggers = migrated["stages"][0]["exit_triggers"]
            self.assertEqual(migrated_triggers[index]["comparison"], ">")
            self.assertEqual(migrated_triggers[index + 1]["comparison"], ">")
            self.assertEqual(migrated_triggers[index + 2]["comparison"], "<=")
        self.assertEqual(migrated["name"], "unchanged")
        self.assertEqual(migrated["stages"][0]["exit_triggers"][-1], triggers[-1])

    def test_migration_is_idempotent(self) -> None:
        profile = {
            "stages": [
                {
                    "exit_triggers": [
                        {"type": "weight", "value": 0, "comparison": ">="}
                    ]
                }
            ]
        }

        migrated, first_count = migrate_profile(profile)
        migrated_again, second_count = migrate_profile(migrated)

        self.assertEqual(first_count, 1)
        self.assertEqual(second_count, 0)
        self.assertEqual(migrated_again, migrated)

    def test_validation_accepts_only_canonical_numeric_comparisons(self) -> None:
        canonical = {
            "stages": [
                {
                    "exit_triggers": [
                        {"type": "weight", "value": 0, "comparison": ">"},
                        {"type": "pressure", "value": 1, "comparison": "<="},
                        {"type": "user_interaction"},
                    ]
                }
            ]
        }
        legacy = {
            "stages": [
                {
                    "exit_triggers": [
                        {"type": "weight", "value": 0, "comparison": ">="},
                        {"type": "time", "value": 1},
                    ]
                }
            ]
        }

        canonical_errors, canonical_count = comparison_errors(canonical, Path(__file__))
        legacy_errors, legacy_count = comparison_errors(legacy, Path(__file__))

        self.assertEqual(canonical_errors, [])
        self.assertEqual(canonical_count, 2)
        self.assertEqual(legacy_count, 2)
        self.assertEqual(len(legacy_errors), 2)
        self.assertIn("got '>='", legacy_errors[0])
        self.assertIn("got None", legacy_errors[1])


if __name__ == "__main__":
    unittest.main()
