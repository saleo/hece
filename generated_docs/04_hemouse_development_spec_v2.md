# HEMouse Development Specification v2.0

## Project Overview
**HEMouse** (Head-Eye-Mouth Mouse) - A hands-free mouse control system combining facial gestures, head movements, and advanced keyboard navigation for computer interaction.

**Hybrid Philosophy**: Integrates health-focused CV (Computer Vision) with productivity-focused keyboard control, inspired by mouseMaster's mode-based architecture.

## Core Objectives

### Primary Goals (by priority)
1. **Productivity Enhancement** - Faster input, better mood, reduced context switching
2. **Health-Focused** - Enable neck/eye movement during computer work to prevent RSI
3. **Operational Convenience** - Support scenarios where hands are unavailable (teaching, streaming, mobile work)
4. **Accessibility** - Multiple control modes for different user capabilities and contexts

### Target Users
- Knowledge workers (keyboard-heavy > mouse-heavy users)
- Livestream presenters/teachers
- Users with RSI or ergonomic concerns
- Power users seeking mouse-free workflows
- NOT suitable for: graphic designers requiring continuous precise mouse control

## Technical Requirements

### Hardware Constraints
- **CPU**: Intel i7-1165G7 @ 2.80GHz (4 cores, 8 threads)
- **GPU**: Intel Iris Xe + NVIDIA MX450 (2GB)
- **Camera**: 1280×720p @ 30fps (built-in webcam)
- **Multi-monitor**: 2+ displays support required

### Performance Targets
- Stable, accurate, fast (must exceed manual mouse to gain adoption)
- Low resource usage (≤30% CPU, real-time response <100ms)
- Seamless mode transitions (<50ms)

## Feature Roadmap

### Stage 1: Core Operations (CURRENT)
[ ] Cursor movement via keyboard grid (36-cell vim-like)
[ ] Click (CapsLock tap)
[ ] Double-click (CapsLock double-tap)
[ ] Right-click (CapsLock+Shift)
- [ ] Multi-monitor switching via head tracking

### Stage 2: Enhanced Control (mouseMaster-inspired)
- [ ] **Mode-based architecture** with context awareness
- [ ] **Hint mode**: Screen-labeled quick navigation
- [ ] **Normal mode**: IJKL-style directional cursor control
- [ ] **Adaptive grid mode**: Progressive refinement
- [ ] Mouse scroll
- [ ] Text selection
- [ ] Head+facial gesture integration

### Stage 3: Advanced Features
- [ ] **Timed key holds & nested combinations**
- [ ] **Application-specific mode switching**
- [ ] **Live configuration reloading**
- [ ] Position history & jump-back functionality
- [ ] Mouse drag-drop
- [ ] AI health monitoring & posture reminders
- [ ] Zoom functionality for precision tasks

## Technical Architecture

### Mode-Based Control System (mouseMaster-inspired)

```yaml
Idle Mode:
  - System disabled/passive state
  - Minimal resource usage
  - Quick activation via global hotkey

Normal Mode (Directional Control):
  - IJKL or Arrow keys: Cursor movement
  - Configurable acceleration curves
  - Fine/coarse speed toggle
  - Context: Precise positioning tasks

Hint Mode (Quick Navigation):
  - Display labeled hints (letters/numbers) across focusable elements
  - Type hint label to jump cursor instantly
  - Auto-detect: buttons, links, input fields, menu items
  - Context: Fast UI navigation, web browsing
  - Inspired by: Vimium, mouseMaster

Grid Mode (Progressive Refinement):
  - Level 1: 36-cell grid (current implementation)
  - Level 2: Sub-grid within selected cell
  - Number-based selection (avoid letter conflicts)
  - Scope options: Full screen, active monitor, active window
  - Context: Precise positioning in non-interactive areas

Screen Selection Mode:
  - Quick monitor switching
  - Head tracking integration
  - Keyboard shortcuts: CapsLock+Arrow
  - Context: Multi-monitor workflows

Facial Gesture Mode (Health-Focused):
  - Head Movement: Multi-monitor focus detection, directional control
  - Eye Tracking: Fine adjustment (optional, 4cm+ radius)
  - Mouth Actions:
    - Smile levels → Grid size/speed selection
    - Lip reading → Control commands
    - Whistle → Activation toggle
    - Deep breath action → Health reminder
  - Context: Hands-free operation, health breaks
```

### Key Design Principles (Integrated)

#### From Original HEMouse:
1. **Health First**: Micro-movements, posture variation, breathing reminders
2. **Keyboard Hybrid**: Reliable fallback when CV fails
3. **Context-Aware Detection**: Window-focus based (not just cursor)
4. **Non-Intrusive**: Avoid disturbing others

#### From mouseMaster:
5. **Mode Separation**: Clear contexts for different tasks
6. **Complex Input Handling**: Timed holds, sequences, nested combinations
7. **Configuration Flexibility**: Live reload, per-app settings
8. **Visual Feedback**: Overlays, indicators, minimal interference
9. **Many-to-Many Mapping**: Multiple triggers → same action

### Key Binding System

```yaml
Global Triggers (Always Active):
  - CapsLock (double-tap): Toggle system on/off
  - CapsLock+Esc: Exit application

Grid Mode Bindings:
  - CapsLock+Space: Grid on current monitor
  - CapsLock+Arrow: Grid on specific monitor
  - 0-9: Select cell/region
  - Arrow keys: Fine-tune within cell
  - CapsLock (tap): Click
  - CapsLock (double-tap): Double-click
  - CapsLock+Shift: Right-click

Normal Mode Bindings (To Implement):
  - IJKL: Move cursor (I=up, J=left, K=down, L=right)
  - Shift+IJKL: Fast movement
  - Ctrl+IJKL: Pixel-precise movement
  - Space: Click
  - Shift+Space: Right-click

Hint Mode Bindings (To Implement):
  - Enter hint labels (auto-generated 1-2 char codes)
  - Esc: Cancel hint mode
  - Tab: Cycle through hints

Advanced Combinations (To Implement):
  - Timed holds: Hold key >300ms for alternative action
  - Sequential: Key1 → Key2 within 500ms
  - Nested: Modifier+Key while in specific mode
```

### Configuration System

```yaml
Configuration Architecture:
  - Base config: config.properties (mouseMaster-inspired)
  - User overrides: user_config.json
  - Per-application: app_specific/*.json
  - Live reload: Watch file changes, hot-swap settings

Configurable Parameters:
  - Key bindings per mode
  - Movement speed/acceleration
  - Grid size and levels
  - Hint label generation (letters vs numbers)
  - CV thresholds (smile detection, head angle)
  - Multi-monitor behavior
  - Visual overlay style

Application-Specific Profiles:
  - Auto-switch modes based on active window
  - Example: Browser → Hint mode, Text editor → Normal mode
  - Whitelist/blacklist for gesture control
```

## Competitive Analysis

### Feature Comparison Matrix

| Feature | HEMouse v2 | mouseMaster | CameraMouse | SmyleMouse | PGM | mouse-free |
|---------|------------|-------------|-------------|------------|-----|------------|
| Health focus | ✅ | ❌ | ❌ | ⚠️ | ⚠️ | ❌ |
| Multi-monitor | ✅ | ✅ | ❌ | ? | ⚠️ | ✅ |
| Keyboard hybrid | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| Hint mode | 🔄 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Mode-based | 🔄 | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| Facial gestures | 🔄 | ❌ | ✅ | ✅ | ✅ | ❌ |
| Grid navigation | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Live config | 🔄 | ✅ | ❌ | ? | ❌ | ❌ |
| Price | TBD | Free | Free | $29/mo | Free | Free |

Legend: ✅ Full support | 🔄 In development | ⚠️ Partial | ❌ Not supported

### Unique Value Propositions

**HEMouse v2 = mouseMaster (productivity) + Health-focused CV**

1. **Only solution combining**:
   - Advanced keyboard modes (mouseMaster)
   - Health-promoting facial/head control
   - Context-aware automation

2. **Hybrid flexibility**:
   - Pure keyboard when lighting poor
   - Pure gestures when hands busy
   - Combined mode for optimal ergonomics

3. **Intelligence layer**:
   - Auto-mode selection based on context
   - Health monitoring & reminders
   - Adaptive learning of user patterns

## Implementation Notes

### Technology Stack

```yaml
Core:
  - Language: Python 3.12.2
  - CV Framework: MediaPipe, OpenCV
  - GUI Overlay: PyQt5/Qt (for mouseMaster compatibility)
  - Input Control: pynput, keyboard
  - Config: JSON + Properties file support

Platform:
  - Primary: Windows 11 (PowerShell)
  - Future: Cross-platform via Qt abstraction layer
  - Package Manager: UV

Architecture Pattern:
  - Mode Manager: State machine with transitions
  - Input Handler: Complex key combination parser
  - CV Pipeline: Separate thread, async updates
  - Overlay Renderer: Transparent window, low-latency
  - Config Manager: Hot-reload watcher
```

### Branch Structure
- `HECE_main`: Current baseline (keyboard + head tracking)
- `mode-system`: Mode architecture implementation
- `hint-mode`: Hint system development
- Former branches: keyboardReplaceMouse, moreMonitorsRelevance

### Development Priorities

#### Phase 1: Mode System Foundation (Weeks 1-2)
1. Implement mode manager state machine
2. Refactor existing grid code into Grid Mode
3. Add mode transition logic
4. Create overlay rendering system

#### Phase 2: Hint Mode (Weeks 3-4)
1. UI element detection (accessibility APIs)
2. Hint label generation algorithm
3. Visual hint overlay
4. Input handling for hint selection

#### Phase 3: Normal Mode (Weeks 5-6)
1. IJKL cursor movement with acceleration
2. Speed toggle system
3. Click/scroll integration
4. Fine-tuning controls

#### Phase 4: Configuration System (Week 7)
1. Config file structure
2. Live reload mechanism
3. Per-app profile system
4. GUI config editor (optional)

#### Phase 5: CV Integration (Weeks 8-10)
1. Head tracking for monitor switching
2. Facial gesture recognition
3. Mode triggering via gestures
4. Calibration system

#### Phase 6: Polish & Advanced (Weeks 11-12)
1. Position history
2. Timed/nested key combinations
3. Zoom functionality
4. Performance optimization

### Critical Paths
1. Mode system architecture (foundation for all features)
2. Hint mode implementation (high user value)
3. CV gesture integration (unique differentiator)
4. Configuration flexibility (power user adoption)

## Known Limitations & Solutions

### Current Issues
✅ LibreOffice Calc: Double-click behavior fixed via CapsLock double-tap
✅ Text editors: Caret positioning works correctly after recent fixes
✅ Vimium conflicts: Grid numbers avoid single-letter shortcuts

### New Challenges (mouseMaster integration)
- **Key binding conflicts**: Need comprehensive conflict detection
  - Solution: Priority system, context awareness, per-app overrides
- **Mode confusion**: Users may forget current mode
  - Solution: Persistent visual indicator, audio feedback (optional)
- **Learning curve**: Multiple modes increase complexity
  - Solution: Tutorial system, progressive disclosure, smart defaults

### Platform Limitations
- Windows-only initially (Python + Qt allows future expansion)
- Webcam quality dependency for CV features
- Accessibility API variations across applications

## Business Model

### Dual-Version Strategy

**Open Source (Core)**:
- Grid Mode navigation
- Normal Mode (IJKL control)
- Basic multi-monitor support
- Single config file

**Commercial (Pro)**:
- Hint Mode with AI element detection
- Facial gesture control
- Health monitoring & reminders
- Live config reload
- Per-application profiles
- Priority support
- Cloud config sync

### Pricing (Tentative)
- Free: Open source version
- Pro: $19/month or $149/year (vs SmyleMouse $29/mo)
- Lifetime: $399 (vs SmyleMouse $400+)

### Benefits
- **Privacy trust**: Core code visible
- **Community contribution**: Extensions, translations, profiles
- **Revenue generation**: Sustainable development
- **Market differentiation**: Unique health+productivity combo

## Quality Assurance

### Testing Matrix
```yaml
Functional Tests:
  - All modes: Activation, operation, deactivation
  - Key bindings: Simple, timed, sequential, nested
  - Multi-monitor: Switching, cursor wrap, focus tracking
  - CV features: Various lighting, angles, distances

Performance Tests:
  - CPU usage: <30% during active use
  - Latency: <100ms input-to-action
  - Memory: <200MB baseline
  - Mode transitions: <50ms

Compatibility Tests:
  - Applications: Browsers, IDEs, Office, CAD tools
  - Keyboards: Different layouts, languages
  - Monitors: 1-4 displays, mixed DPI
  - Webcams: Various resolutions, framerates

Usability Tests:
  - Learning curve: Time to proficiency
  - Mode discovery: Intuitive transitions
  - Error recovery: Graceful handling
  - Accessibility: Screen reader compatibility
```

### Success Metrics
- **Adoption**: Daily active usage >30 days
- **Performance**: Mouse speed parity within 2 weeks practice
- **Health**: User-reported RSI improvement
- **Productivity**: Task completion time reduction

## Documentation Plan

### User Documentation
1. Quick Start Guide (5 minutes to first click)
2. Mode Reference Card (printable cheatsheet)
3. Tutorial Videos (one per mode)
4. Configuration Cookbook (common scenarios)
5. Troubleshooting Guide (common issues)

### Developer Documentation
1. Architecture Overview (mode system, CV pipeline)
2. API Reference (extension points)
3. Configuration Schema (all options documented)
4. Contribution Guide (code style, testing)

## Future Vision

### Advanced Features (Post-1.0)
- **AI Agent Integration**: Voice commands, context prediction
- **Collaborative Modes**: Share control schemes, crowdsourced profiles
- **VR/AR Support**: Spatial gestures for 3D interfaces
- **Biometric Feedback**: Heart rate → break reminders, stress detection
- **Cross-Device**: Control multiple computers with one setup
- **Gesture Recording**: Macro-like automation with gestures

### Platform Expansion
- macOS support (Qt already cross-platform)
- Linux support (X11/Wayland compatibility)
- Mobile companion app (config, health tracking)

### Ecosystem
- Plugin marketplace (custom modes, gestures)
- Profile sharing community
- Integration APIs (automation tools, accessibility software)

---

## Appendix: Design Rationale

### Why Mode-Based Architecture?
- **Cognitive clarity**: Users know what inputs do in each context
- **Key efficiency**: Reuse same keys for different purposes
- **Conflict avoidance**: Isolate bindings to relevant contexts
- **Scalability**: Easy to add new modes without breaking existing ones

### Why Facial Gestures + Keyboard?
- **Redundancy**: Multiple fallbacks increase reliability
- **Optimization**: Best tool for each scenario
- **Health**: Movement variety prevents repetitive strain
- **Accessibility**: Users with different capabilities can all participate

### Why Grid + Hint Modes?
- **Complementary**: Grid for anywhere, Hints for interactive elements
- **Speed/Precision tradeoff**: Hints faster, Grid more precise
- **Universal coverage**: Together handle 100% of screen area

---

**Last Updated**: 2025-09-28
**Status**: Stage 1 complete, Stage 2 design phase (mouseMaster integration planning)
**Next Milestone**: Mode system architecture implementation (2-week sprint)