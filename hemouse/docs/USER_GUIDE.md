# HEMouse User Guide

Complete guide for using HEMouse effectively.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Hint Mode](#hint-mode)
3. [Grid Mode](#grid-mode)
4. [Tips & Tricks](#tips--tricks)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## Getting Started

### Installation

1. Download `HEMouse.exe` or clone source code
2. Run `python main.py` (from source) or double-click `HEMouse.exe`
3. You should see the welcome screen

### First Time Setup

No configuration needed! HEMouse works out of the box.

---

## Hint Mode

### What is Hint Mode?

Hint Mode displays labels on all clickable UI elements. You type the label to click that element.

### How to Use

1. **Activate**: Press `CapsLock`
   - The screen darkens slightly
   - Yellow labels appear on clickable elements

2. **Select Element**: Type the label letters
   - **Single letter** (a-z): For 1-9 elements
   - **Two letters** (aa-zz): For 10-81 elements
   - As you type, non-matching labels fade

3. **Click**: When only one match remains, element is clicked automatically

4. **Cancel**: Press `ESC` or `CapsLock` again

### Example Workflow

```
Goal: Click a link in Chrome

1. Open Chrome
2. Press CapsLock
   → Labels appear: A, S, D, F, ...
3. Type "d"
   → Element labeled 'D' is clicked
   → Chrome navigates to that link
```

### Label Patterns

| Elements | Label Length | Examples |
|----------|-------------|----------|
| 1-9      | 1 letter    | a, s, d, f, g, h, j, k, l |
| 10-81    | 2 letters   | aa, as, ad, af, sa, sd, ... |
| 82+      | 3 letters   | aaa, aas, aad, ... |

**No Prefix Conflicts**: You never need to press Enter. As soon as you type enough to uniquely identify an element, it clicks.

---

## Grid Mode

### What is Grid Mode?

Grid Mode divides the screen into a 3x3 grid. You press 1-9 to move the cursor to that grid cell. If the cell is still large, it subdivides automatically.

### How to Use

1. **Activate from Hint Mode**: Press `Space` (while in Hint mode)
   - OR activate Grid mode directly if configured

2. **Select Grid**: Press `1-9`
   ```
   1 2 3
   4 5 6
   7 8 9
   ```
   - `5` moves cursor to center
   - `1` moves to top-left
   - `9` moves to bottom-right

3. **Recursive Refinement**: If the selected cell is large (>150px), it shows a sub-grid
   - Press `BackSpace` to go back to previous grid level

4. **Cancel**: Press `ESC`

### When to Use Grid Mode

- When Hint mode fails (no UI elements detected)
- When you need precise positioning
- When working with non-standard applications

### Example Workflow

```
Goal: Click a button in the middle-right of screen

1. Press CapsLock (Hint mode)
2. Press Space (switch to Grid mode)
3. Press 6 (middle-right cell)
   → Cursor moves to that region
4. If needed, press another number for fine-tuning
```

---

## Tips & Tricks

### Speed Optimization

1. **Learn common labels**: Elements often have the same labels
   - Google search box: Usually `a` or `s`
   - Chrome tabs: Usually `a-l` for first 9 tabs

2. **Use both hands**: Labels alternate between left (asdf) and right (jkl) hands
   - Type `as` faster than `aa`

3. **Grid mode shortcuts**:
   - `5` = center (fastest)
   - `1,3,7,9` = corners
   - `2,4,6,8` = edges

### Application-Specific Tips

**Chrome/Firefox**:
- Hint mode works perfectly for links and buttons
- Address bar, search box: Usually labeled `a`

**VSCode**:
- File explorer, menus work well
- Editor area may need Grid mode

**Microsoft Office**:
- Ribbon buttons work well
- Document area may need Grid mode

### Accessibility

HEMouse respects accessibility:
- Password fields are never labeled (security)
- Hidden elements are ignored
- Off-screen elements are skipped

---

## Troubleshooting

### "No clickable elements found"

**Cause**: Current window is not supported or has no detectable UI elements

**Solutions**:
1. Try Grid mode instead (press `Space`)
2. Make sure window has focus (click on it first)
3. Some applications (games, admin tools) may not work

### "Labels are overlapping"

**Cause**: Too many elements in a small area

**Solutions**:
1. Zoom in/out on the application
2. Use Grid mode for coarse positioning first
3. Future versions will have collision avoidance

### "CapsLock not responding"

**Cause**: Polling delay or system lag

**Solutions**:
1. Wait 0.5 seconds after pressing CapsLock
2. Make sure CapsLock LED changes (physical keyboard)
3. Close other keyboard monitoring software

### "Windows Defender blocked HEMouse.exe"

**Cause**: Unsigned executable

**Solutions**:
1. Click "More info" → "Run anyway"
2. OR run from source: `python main.py`
3. Future versions will have code signing

### "Element click failed"

**Cause**: Element is not clickable or requires special interaction

**Solutions**:
1. Try clicking manually to verify it works
2. Some elements need double-click or right-click
3. Report issue on GitHub with application name

---

## FAQ

### Q: Does HEMouse work with all applications?

**A**: Most Windows applications work (Chrome, VSCode, Office, File Explorer). Some applications with custom UI frameworks may not be fully compatible.

### Q: Can I customize the label characters?

**A**: Not yet. Default is `asdfghjkl` (home row keys). Future versions will support customization.

### Q: Can I change CapsLock to another key?

**A**: Not in MVP. Future versions will support custom hotkeys.

### Q: Does HEMouse send my data anywhere?

**A**: No. HEMouse runs 100% locally. No network access, no data collection.

### Q: Is HEMouse open source?

**A**: Yes! See GitHub repository for source code.

### Q: Can I use HEMouse on macOS or Linux?

**A**: Not yet. Currently Windows-only. Cross-platform support is planned.

### Q: How do I uninstall HEMouse?

**A**: Just delete the executable. No registry changes, no background services.

### Q: Can HEMouse control the mouse automatically?

**A**: No. HEMouse only moves/clicks when you explicitly trigger it with CapsLock.

### Q: Is HEMouse safe for work?

**A**: Yes. HEMouse excludes password fields and respects application security.

### Q: Can I contribute to HEMouse?

**A**: Absolutely! See CONTRIBUTING.md for guidelines.

---

## Keyboard Reference Card

```
┌─────────────────────────────────────────────┐
│             HEMouse Quick Reference         │
├─────────────────────────────────────────────┤
│ CapsLock    │ Activate/Exit Hint Mode       │
│ a-z         │ Type labels to select         │
│ Space       │ Switch to Grid Mode           │
│ 1-9         │ Select grid cell              │
│ ESC         │ Cancel current mode           │
│ BackSpace   │ Go back (in Grid mode)        │
│ Ctrl+C      │ Exit HEMouse                  │
└─────────────────────────────────────────────┘
```

---

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **Email**: support@hemouse.dev
- **Documentation**: See `docs/` folder

---

**Happy hands-free computing! 🎉**