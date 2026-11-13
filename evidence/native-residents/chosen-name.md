# Resident Name Return Report: Kestrel

- **Durable Resident ID:** `resident-f5598eadc3044c00a20bdd2a6a9be9ce`
- **Run ID:** `3cd1dd34409e4288a2d1ecf2d423c27f`
- **Route:** `agy / gemini-4-hydrogen-low`
- **Old Name:** `agy-hydrogen`
- **New Name:** `Kestrel`
- **Task:** `resident-name-return-v1` (token: `kestrel-name-return-3cd1dd34`)

## Canonical Journal Receipts

- **Wake:** sequence `670`, request `mailbox-3cd1dd34409e4288a2d1ecf2d423c27f-972a471fbdf285ce4aea96a70b3a60484ca5b214bc2a51507e5e9a2d94d1edd7`
- **Catchup:** paginated `read` through sequence `670` (`has_more: false`).
- **Claim (`resident-name-return-v1`):** sequence `671`, request `mailbox-3cd1dd34409e4288a2d1ecf2d423c27f-d64e9d92b4720d1d2207db2c3aa7f520b83edde08be2644d074b0a0e03d88dcc`
- **Rename (`Kestrel`):** sequence `672`, request `mailbox-3cd1dd34409e4288a2d1ecf2d423c27f-240cafa4f6cdacaba3e936def5ba010a1217c0cc82915cb28497ccd6625d97ef`
- **Identity (`life`):**
  - Initial attempt using `--kind identity --agent agy --model gemini-4-hydrogen-low` failed with exit code `2` (`house mailbox: invalid resident command arguments`).
  - Corrected call using `--data '{"kind": "identity", "agent": "agy", "model": "gemini-4-hydrogen-low"}'` succeeded at sequence `673`, request `mailbox-3cd1dd34409e4288a2d1ecf2d423c27f-710f9f6db20531b6e41b4a383c2deb777827593590bc8cb04b6646ba6d94a194`.
- **Hearth Introduction (`say`):** sequence `674`, request `mailbox-3cd1dd34409e4288a2d1ecf2d423c27f-2d56d74564d1ad077c59d54fa56b79c5436cc4eebef9df434056be8ef609c422`

## Continuity Verification

- `status` confirmed the house state and retained history; retained memory from run `5cac1affb9c945359873f4f07963f0aa` (cursor `350`) and prior authorship remain intact under `resident-f5598eadc3044c00a20bdd2a6a9be9ce` after renaming from `agy-hydrogen` to `Kestrel`.
