# HEMouse Architecture Documentation

Technical architecture and design decisions for HEMouse MVP.

---

## System Overview

HEMouse is a keyboard-driven mouse control system with three main modes:
1. **IDLE**: Waiting for user activation
2. **HINT**: Label-based element selection
3. **GRID**: Grid-based cursor positioning

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                     (HEMouseApp)                             │
└────┬─────────────────────┬──────────────────────┬───────────┘
     │                     │                      │
     │                     │                      │
┌────▼───────┐    ┌───────▼────────┐    ┌───────▼────────┐
│  Hotkey    │    │  Mode          │    │  Element       │
│  Manager   │    │  Manager       │    │  Detector      │
│            │    │                │    │                │
│ CapsLock   │    │ IDLE/HINT/GRID │    │ Windows UIA    │
│ Detection  │    │                │    │                │
└────┬───────┘    └───────┬────────┘    └───────┬────────┘
     │                     │                      │
     │            ┌────────▼──────┐               │
     │            │  Hint Mode    │◄──────────────┘
     │            │               │
     │            │ - Overlay     │◄──────────┐
     │            │ - Labels      │           │
     │            │ - Input       │           │
     │            └───────┬───────┘           │
     │                    │                   │
     │            ┌───────▼────────┐    ┌─────▼──────┐
     └───────────►│  Grid Mode     │    │  Label     │
                  │                │    │  Generator │
                  │ - 3x3 Grid     │    │            │
                  │ - Recursive    │    │ a-z labels │
                  └────────────────┘    └────────────┘
```

---

## Component Details

### 1. HotkeyManager (`src/core/hotkey_manager.py`)

**Purpose**: Detect CapsLock state changes using Windows API polling

**Key Methods**:
- `register_hotkey(key_name, callback)`: Register callback for hotkey events
- `start_monitoring()`: Start polling loop in background thread
- `stop_monitoring()`: Stop polling loop

**Design Decisions**:
- **Polling vs Hook**: MVP uses polling (50ms interval) for simplicity
  - Pros: No admin privileges needed, easier to implement
  - Cons: Slight delay, higher CPU usage
  - Future: Low-level keyboard hook (C++ DLL) for v1.2

**Thread Safety**:
- Background thread for monitoring
- Main thread for callbacks (via event loop)

---

### 2. ElementDetector (`src/core/element_detector.py`)

**Purpose**: Detect clickable UI elements using Windows UI Automation

**Key Methods**:
- `get_clickable_elements()`: Scan foreground window for elements
- `_traverse_elements()`: Recursively walk UI tree
- `_is_clickable()`: Check if element is clickable type

**Supported Element Types**:
- Button, Hyperlink, MenuItem, TabItem
- ListItem, TreeItem, CheckBox, RadioButton
- ComboBox, Edit, Document, Text

**Performance**:
- Max recursion depth: 10 (prevent infinite loops)
- Typical scan time: 200-800ms depending on UI complexity
- Password fields excluded for security

**Limitations**:
- Cannot detect custom-drawn UI (games, Qt apps)
- Admin-level apps require elevated privileges
- Some apps block UI Automation access

---

### 3. LabelGenerator (`src/core/label_generator.py`)

**Purpose**: Generate unique labels with no prefix conflicts

**Algorithm**:
```
Stage 1 (1-9 elements): Single letters [a-l]
Stage 2 (10-81 elements): Two letters [aa-ll]
  - Prioritize alternating hands (as, ad, ja, jd)
  - Then same-hand combinations (aa, ss, dd)
Stage 3 (82+ elements): Three letters [aaa-lll]
```

**Character Set**: `asdfghjkl` (home row, easy to type)
- Left hand: asdf
- Right hand: jkl (gh removed to avoid accidental presses)

**No Prefix Conflicts**: Ensures `a` and `as` never coexist

---

### 4. OverlayWindow (`src/ui/overlay_window.py`)

**Purpose**: Display transparent overlay with labels

**Technical Details**:
- **Framework**: Tkinter (built-in, no extra dependencies)
- **Transparency**: 30% alpha
- **Position**: Always on top (`-topmost`)
- **No borders**: `overrideredirect(True)`

**Label Rendering**:
- Yellow rectangle background
- Black border (2px)
- Bold Arial 14pt text
- Position: Left of element (or right if no space)

**Keyboard Capture**:
- Window captures focus (`focus_force()`)
- Binds `<KeyPress>` events for label input
- ESC key to exit

**Cleanup**:
- Restores previous window focus on exit
- Destroys Tkinter root properly

---

### 5. HintMode (`src/modes/hint_mode.py`)

**Purpose**: Control Hint mode workflow

**Activation Flow**:
```
1. CapsLock pressed
2. Detect elements (ElementDetector)
3. Generate labels (LabelGenerator)
4. Create overlay (OverlayWindow)
5. Bind keyboard events
6. Wait for user input
```

**Input Matching**:
```
User types: "a"
  → Find all labels starting with "a"
  → If 1 match: Click element
  → If 2+ matches: Highlight matching labels
  → If 0 matches: Beep and reset
```

**Click Methods**:
1. **Primary**: `element.click_input()` (pywinauto)
2. **Fallback**: `win32api.mouse_event()` (low-level)

---

### 6. GridMode (`src/modes/grid_mode.py`)

**Purpose**: Grid-based cursor positioning

**Grid Layout**:
```
1 2 3
4 5 6  (3x3 grid)
7 8 9
```

**Recursive Refinement**:
```
Select grid 5 (center)
  → If region > 150px: Show sub-grid
  → Else: Move cursor to center
```

**Navigation**:
- `1-9`: Select grid cell
- `BackSpace`: Go back to previous grid level
- `ESC`: Exit grid mode

---

### 7. ModeManager (`src/modes/mode_manager.py`)

**Purpose**: Manage mode transitions

**States**: IDLE, HINT, GRID

**Transition Rules**:
```
IDLE → HINT: CapsLock ON
HINT → IDLE: CapsLock OFF or ESC or click
HINT → GRID: Space key
GRID → IDLE: ESC or cursor positioned
```

**Callbacks**:
- `on_mode_enter`: Called when entering mode
- `on_mode_exit`: Called when exiting mode

---

## Data Flow

### Hint Mode Flow

```
1. User presses CapsLock
   ↓
2. HotkeyManager detects state change
   ↓
3. Callback triggers HEMouseApp._on_capslock_on()
   ↓
4. ModeManager switches to HINT mode
   ↓
5. HintMode.activate() called
   ↓
6. ElementDetector scans UI tree
   ↓
7. LabelGenerator creates labels
   ↓
8. OverlayWindow displays labels
   ↓
9. User types label characters
   ↓
10. HintMode._on_key_press() matches input
    ↓
11. If match: Click element
    ↓
12. Overlay destroyed, focus restored
    ↓
13. ModeManager switches to IDLE
```

---

## Performance Considerations

### Bottlenecks

1. **Element Detection** (200-800ms)
   - UI tree traversal is slow for complex windows
   - Mitigation: Max depth limit, skip hidden elements

2. **Overlay Rendering** (50-100ms)
   - Tkinter is not optimized for many labels
   - Mitigation: Future versions may use DirectX overlay

3. **Polling Delay** (50ms)
   - CapsLock detection has inherent delay
   - Mitigation: Future keyboard hook for instant detection

### Optimization Strategies

1. **Lazy Loading**: Only detect elements when Hint mode activates
2. **Caching**: Could cache window structure (not implemented in MVP)
3. **Parallel Detection**: Could use threading (not implemented in MVP)

---

## Security & Privacy

### Security Measures

1. **Password Field Exclusion**: Never show labels on password inputs
2. **No Network Access**: 100% local operation
3. **No Data Collection**: Zero telemetry or logging to external services

### Known Limitations

1. **Unsigned Executable**: Windows Defender may warn users
   - Solution: Code signing certificate (planned for v1.2)

2. **Admin Apps**: Cannot control elevated applications
   - Solution: Run HEMouse as admin (not recommended for normal use)

---

## Error Handling

### Graceful Degradation

1. **No Elements Found**: Suggest Grid mode as fallback
2. **Click Failed**: Try alternative click method
3. **Window Access Denied**: Show warning, continue monitoring

### Logging

- **Console**: INFO level (user-facing messages)
- **File**: DEBUG level (`logs/hemouse_YYYYMMDD.log`)

---

## Testing Strategy

### Unit Tests (`tests/test_all.py`)

1. **LabelGenerator**: Verify label uniqueness, no conflicts
2. **ModeManager**: Verify state transitions
3. **HotkeyManager**: Manual test (requires user input)
4. **ElementDetector**: Manual test (requires active window)

### Integration Tests

Manual testing with real applications:
- Chrome (web browsing)
- VSCode (code editing)
- File Explorer (file management)

---

## Future Improvements

### v1.1 (Performance & Polish)
- Collision avoidance for labels
- Element detection optimization (<300ms)
- Better error messages

### v1.2 (Advanced Features)
- Low-level keyboard hook (C++ DLL)
- Custom hotkeys and label characters
- Application blacklist/whitelist

### v2.0 (Computer Vision)
- Head tracking (MediaPipe)
- Gaze-assisted cursor control (GADS)
- Eye blink detection

### v3.0 (Normal Mode)
- IJKL arrow key navigation
- Scroll mode
- Drag-and-drop support

---

## Dependencies

### Core Dependencies

- **pywin32**: Windows API access (keyboard, mouse, window management)
- **pywinauto**: UI Automation for element detection
- **tkinter**: Overlay window (built-in with Python)
- **Pillow**: Image handling (for future icon support)

### Build Dependencies

- **PyInstaller**: Executable packaging

### Python Version

- Minimum: Python 3.10
- Tested: Python 3.10, 3.11

---

## File Structure

```
hemouse/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── hotkey_manager.py       # CapsLock detection
│   │   ├── element_detector.py     # UI element detection
│   │   └── label_generator.py      # Label generation
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── mode_manager.py         # State management
│   │   ├── hint_mode.py            # Hint mode controller
│   │   └── grid_mode.py            # Grid mode controller
│   ├── ui/
│   │   ├── __init__.py
│   │   └── overlay_window.py       # Transparent overlay
│   └── utils/
│       ├── __init__.py
│       └── logger.py               # Logging utility
├── tests/
│   └── test_all.py                 # Test suite
├── docs/
│   ├── USER_GUIDE.md               # User documentation
│   └── ARCHITECTURE.md             # This file
├── logs/                           # Log files (created at runtime)
├── main.py                         # Application entry point
├── build.py                        # Build script
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # Project overview
```

---

## Conclusion

HEMouse MVP achieves the core goal: keyboard-driven mouse control using Hint mode and Grid mode. The architecture is modular, maintainable, and ready for future enhancements.

**Key Strengths**:
- Simple, understandable codebase
- No external dependencies (beyond pywin32/pywinauto)
- Works with most Windows applications

**Known Limitations**:
- Performance could be better
- Label collision not handled
- Admin apps not supported

**Next Steps**:
- Gather user feedback
- Optimize element detection
- Implement collision avoidance
- Add low-level keyboard hook

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30