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
