# Profile Defaults

These profiles are used as default profiles on the Espresso Machine when creating new profiles from the Dial App.

## Considerations

- Profiles inside `community` will appear marked with that label in the Dial App.
- To add a description, profiles must include the `display` field with this structure:

```json
"display": {
  "shortDescription": "",
  "description": ""
}
```

- The content in `shortDescription` will appear on screen when creating a new profile.

## Exit-trigger comparisons

Numeric exit triggers (`weight`, `time`, `pressure`, `flow`, `piston_position`,
and `power`) must declare either `>` or `<=` as their `comparison`. The greater
case is strictly greater than: a trigger does not activate at the exact threshold
and activates only after the measured value rises above it. In particular, a
`> 0` weight trigger waits while the measured weight is exactly 0 g.

Legacy `>=` comparisons and omitted comparisons were migrated to `>`. This is a
small exact-boundary behavior change; it does not change `<=` comparisons or any
other profile field. The migration is idempotent and can be safely repeated:

```sh
python .github/scripts/check_profile_comparisons.py --write
```

Run the read-only corpus check before submitting profile changes:

```sh
python .github/scripts/check_profile_comparisons.py
```
