"""Check or migrate simplified profile exit-trigger comparisons."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NUMERIC_TRIGGER_TYPES = {
    "weight",
    "time",
    "pressure",
    "flow",
    "piston_position",
    "power",
}
CANONICAL_COMPARISONS = {">", "<="}


def profile_paths() -> list[Path]:
    return sorted(ROOT.glob("*.json")) + sorted((ROOT / "community").glob("*.json"))


def migrate_profile(profile: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Return a canonical copy and the number of migrated numeric triggers."""
    migrated_profile = deepcopy(profile)
    migration_count = 0

    for stage in migrated_profile.get("stages", []):
        for trigger in stage.get("exit_triggers", []):
            if trigger.get("type") not in NUMERIC_TRIGGER_TYPES:
                continue
            if trigger.get("comparison") in (None, ">="):
                trigger["comparison"] = ">"
                migration_count += 1

    return migrated_profile, migration_count


def comparison_errors(profile: dict[str, Any], path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    checked_triggers = 0

    for stage_index, stage in enumerate(profile.get("stages", [])):
        for trigger_index, trigger in enumerate(stage.get("exit_triggers", [])):
            if trigger.get("type") not in NUMERIC_TRIGGER_TYPES:
                continue

            checked_triggers += 1
            comparison = trigger.get("comparison")
            if comparison not in CANONICAL_COMPARISONS:
                location = (
                    f"{path.relative_to(ROOT)}: stages[{stage_index}]"
                    f".exit_triggers[{trigger_index}]"
                )
                errors.append(
                    f"{location}: comparison must be '>' or '<=', got {comparison!r}"
                )

    return errors, checked_triggers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="migrate legacy >= and omitted numeric comparisons to > before checking",
    )
    args = parser.parse_args()

    errors: list[str] = []
    checked_triggers = 0
    migrated_triggers = 0
    paths = profile_paths()

    for path in paths:
        try:
            profile = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {error}")
            continue

        if args.write:
            profile, migration_count = migrate_profile(profile)
            if migration_count:
                path.write_text(
                    json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                migrated_triggers += migration_count

        profile_errors, profile_trigger_count = comparison_errors(profile, path)
        errors.extend(profile_errors)
        checked_triggers += profile_trigger_count

    if errors:
        print("\n".join(errors))
        return 1

    print(
        f"Checked {checked_triggers} numeric exit triggers in "
        f"{len(paths)} profiles; all comparisons are canonical."
    )
    if args.write:
        print(f"Migrated {migrated_triggers} legacy comparisons.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
