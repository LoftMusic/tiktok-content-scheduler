# Splice Recorder Backups

## Snapshots

| Date | Time | Description |
|------|------|-------------|
| 2026-03-19 | 21:43 | Initial backup - Mode switch + sample detection + 50ms padding |
| 2026-03-19 | 22:02 | Fixed similar sounds detection - now uses play button click target instead of focus order |
| 2026-03-19 | 22:09 | Added FILLS category to Loop mode + tag mapping |
| 2026-03-19 | 22:12 | Split save paths: Audio/splice_samples/oneshot/\<cat\>/ and Audio/splice_samples/loop/\<cat\>/ |
| 2026-03-19 | 22:14 | Fixed Play Last - now persists to storage and handles background restarts |

## How to Restore

To restore from a backup:
```powershell
# Example: restore from 2026-03-19_22-14
xcopy "C:\Users\Studio3\.openclaw\workspace\splice-recorder\backups\2026-03-19_22-14\*" "C:\Users\Studio3\.openclaw\workspace\splice-recorder\" /Y /E
```

Then reload the extension in Chrome.