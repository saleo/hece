# HEMouse - Hands-Free Mouse Control

**Version**: MVP v1.0
**Status**: Early Development Build
**Platform**: Windows 10/11 (x64)

---

## 🎯 What is HEMouse?

HEMouse is a keyboard-driven mouse control tool inspired by Vimium and Homerow. It allows you to control your mouse cursor and click UI elements using only your keyboard, eliminating the need to reach for your mouse.

### Core Features

- ✅ **Hint Mode**: Press CapsLock to show labels on all clickable UI elements
- ✅ **Label Selection**: Type labels (a-z) to instantly click elements
- ✅ **Grid Mode**: Fallback grid-based positioning when Hint mode fails
- ✅ **Universal**: Works with most Windows applications (Chrome, VSCode, Office, etc.)

### Not Yet Implemented

- ⏳ **Normal Mode**: IJKL arrow key navigation
- ⏳ **Head Tracking**: Computer vision-based cursor control
- ⏳ **Code Signing**: Digital signature for security

---

## 🚀 Quick Start

### Installation

#### Option 1: Run from Source (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/yourusername/hemouse.git
cd hemouse

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

#### Option 2: Download Executable (Coming Soon)

Pre-built `HEMouse.exe` will be available in GitHub Releases.

---

## 📖 Usage Guide

### Starting HEMouse

```bash
python main.py
```

You should see:
```
============================================================
HEMouse - Hands-Free Mouse Control
============================================================
✅ HEMouse is ready!
============================================================

📖 Quick Start Guide:
   1. Press CapsLock to activate Hint mode
   2. Type labels (a-z) to select elements
   3. Press Space to switch to Grid mode
   4. Press ESC to exit current mode
   5. Press Ctrl+C to exit HEMouse
```

### Using Hint Mode

1. **Activate**: Press `CapsLock`
2. **Select Element**: Type the label letters (e.g., `a`, `sj`, `dk`)
   - Single letter labels: 1-9 elements
   - Two letter labels: 10+ elements
3. **Cancel**: Press `ESC` or press `CapsLock` again

**Example**:
- Open Chrome and press `CapsLock`
- Labels appear on links, buttons, input fields
- Type `a` to click the element labeled 'A'
- Type `sj` to click the element labeled 'SJ'

### Using Grid Mode

1. **Activate from Hint Mode**: Press `Space`
2. **Select Grid**: Press `1-9` to move cursor to that grid cell
3. **Refine**: If the grid cell is large, it will subdivide automatically
4. **Cancel**: Press `ESC`

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `CapsLock` | Activate/Deactivate Hint mode |
| `a-z` | Type labels to select elements |
| `Space` | Switch to Grid mode (from Hint mode) |
| `1-9` | Select grid cell (in Grid mode) |
| `ESC` | Exit current mode |
| `Ctrl+C` | Exit HEMouse |

---

## 🏗️ Architecture

```
hemouse/
├── src/
│   ├── core/
│   │   ├── hotkey_manager.py      # CapsLock detection
│   │   ├── element_detector.py    # UI element detection (Windows UIA)
│   │   └── label_generator.py     # Label generation algorithm
│   ├── modes/
│   │   ├── mode_manager.py        # Mode state management
│   │   ├── hint_mode.py           # Hint mode controller
│   │   └── grid_mode.py           # Grid mode controller
│   ├── ui/
│   │   └── overlay_window.py      # Transparent overlay window
│   └── utils/
│       └── logger.py              # Logging utility
├── tests/                         # Unit tests
├── docs/                          # Documentation
├── main.py                        # Application entry point
└── requirements.txt               # Python dependencies
```

---

## 🧪 Testing

### Manual Testing

**Test Scenario 1: Chrome**
```
1. Open Chrome with Google homepage
2. Press CapsLock
3. Verify labels appear on search box, buttons, links
4. Type a label to click a link
5. Verify click works correctly
```

**Test Scenario 2: VSCode**
```
1. Open VSCode
2. Press CapsLock
3. Verify labels on menu items, file explorer, buttons
4. Type a label to click a file
5. Verify file opens
```

**Test Scenario 3: Grid Mode**
```
1. Press CapsLock
2. Press Space to switch to Grid mode
3. Press 5 to move cursor to center
4. Verify cursor moves correctly
```

---

## 🐛 Known Issues

### Compatibility
- ❌ Some applications may not be detected (games, admin-level apps)
- ⚠️ Password fields are intentionally excluded for security
- ⚠️ Performance may be slow on very complex UIs (>100 elements)

### Windows Defender Warning
- ⚠️ Unsigned executable may trigger Windows Defender SmartScreen
- **Solution**: Click "More info" → "Run anyway" or run from source

### Label Positioning
- ⚠️ Labels may overlap on densely packed UIs
- **Workaround**: Use Grid mode as fallback

---

## 🛠️ Development

### Prerequisites

- Python 3.10+
- Windows 10/11
- UV (recommended) or pip
- pywin32, pywinauto, tkinter

### Setup with UV (Recommended)

UV is a fast, modern Python package manager:

```bash
# Install UV if not already installed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment
uv venv

# Activate virtual environment (PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -e .

# Run HEMouse
python main.py
```

See `UV_GUIDE.md` for complete UV documentation.

### Setup with pip (Alternative)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run HEMouse
python main.py
```

### Running Tests

```bash
# Run complete test suite
python tests/test_all.py

# Test individual modules
python src/core/label_generator.py
python src/core/element_detector.py
```

### Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name=HEMouse main.py
```

Output: `dist/HEMouse.exe`

---

## 📋 Roadmap

### v1.1 (Performance & Polish)
- [ ] Performance optimization (element detection < 500ms)
- [ ] Label collision avoidance algorithm
- [ ] Better error handling and user feedback
- [ ] Configuration file support

### v1.2 (Advanced Features)
- [ ] Low-level keyboard hook (C++ DLL) for better input capture
- [ ] Custom label character sets
- [ ] Blacklist/whitelist for applications
- [ ] Hotkey customization

### v2.0 (Computer Vision)
- [ ] Head tracking using MediaPipe
- [ ] Gaze-assisted cursor control (GADS algorithm)
- [ ] Eye blink detection for clicks

### v3.0 (Normal Mode)
- [ ] IJKL arrow key navigation
- [ ] Scroll mode
- [ ] Drag-and-drop support

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update README for user-facing changes

---

## 📄 License

MIT License

Copyright (c) 2025 HEMouse Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Acknowledgments

- **Vimium**: Inspiration for keyboard-driven navigation
- **Homerow**: macOS Hint mode inspiration
- **pywinauto**: Windows UI Automation library
- **Community**: All contributors and testers

---

## 📞 Support

- **GitHub Issues**: https://github.com/yourusername/hemouse/issues
- **Email**: support@hemouse.dev (placeholder)
- **Documentation**: See `docs/` folder for detailed guides

---

**Made with ❤️ for hands-free computing**