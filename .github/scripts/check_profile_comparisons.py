"""Check that simplified profile exit triggers use canonical comparisons."""

from __future__ import annotations

import json
from pathlib import Path


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


def main() -> int:
    errors: list[str] = []
    checked_triggers = 0

    for path in profile_paths():
        try:
            profile = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {error}")
            continue

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

    if errors:
        print("\n".join(errors))
        return 1

    print(
        f"Checked {checked_triggers} numeric exit triggers in "
        f"{len(profile_paths())} profiles; all comparisons are canonical."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
