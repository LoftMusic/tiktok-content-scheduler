# Learnings Log

Log corrections, knowledge gaps, and best practices here.

Format: See SKILL.md in self-improving-agent

---

## [LRN-20260307-001] KSP_SYNTAX

**Logged**: 2026-03-07T23:06:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Important KSP syntax rules discovered during MIDI Player development

### Details
- Variables can ONLY be declared in `on init` callback - NOT in other callbacks
- Use `$CONST` naming (with $) for constants in KSP
- `declare const` must be in on init
- `set_ui_color()` causes errors in some KONTAKT versions - avoid or use valid hex
- `$CONTROL_PAR_FONT_COLOR` doesn't work in all contexts - test first

### Suggested Action
Always declare variables at top of on init. Remember: KSP is strict about variable declaration location.

### Metadata
- Source: error
- Related Files: MIDI_Player.ksp, Stradivari_Violine_Trasa.ksp
- Tags: ksp, kontakt, scripting

---

## [LRN-20260307-002] DAW_SYNC

**Logged**: 2026-03-07T23:06:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
How to sync KSP MIDI player with DAW transport

### Details
KSP provides built-in listeners for DAW sync:
- `$NI_SIGNAL_TRANSP_START` - fires when DAW play is pressed
- `$NI_SIGNAL_TRANSP_STOP` - fires when DAW stop is pressed  
- `$NI_SONG_POSITION` - current DAW playhead position in ticks

Usage:
```
set_listener($NI_SIGNAL_TRANSP_START, 1)
set_listener($NI_SIGNAL_TRANSP_STOP, 1)

on listener
  if ($NI_SIGNAL_TYPE = $NI_SIGNAL_TRANSP_START)
    { Start playback at DAW position }
    $cur_pos := $NI_SONG_POSITION mod $mf_length
  end if
end on
```

### Suggested Action
Use these listeners for tight DAW integration in MIDI players

### Metadata
- Source: conversation
- Related Files: MIDI_Player.ksp
- Tags: daw, sync, kontakt, midi

---
