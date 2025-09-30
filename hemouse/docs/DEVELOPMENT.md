# HEMouse Development Guide

Guide for developers contributing to HEMouse.

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Windows 10/11 (x64)
- Git
- Code editor (VSCode, PyCharm, etc.)

### Clone and Install

```bash
# Clone repository
git clone https://github.com/yourusername/hemouse.git
cd hemouse

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py
```

---

## Project Structure

```
hemouse/
├── src/                  # Source code
│   ├── core/            # Core functionality
│   ├── modes/           # Mode implementations
│   ├── ui/              # User interface
│   └── utils/           # Utilities
├── tests/               # Test suite
├── docs/                # Documentation
├── main.py              # Entry point
└── build.py             # Build script
```

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

```python
# Imports
import sys
import os
from typing import List, Dict

# Constants
MAX_RECURSION_DEPTH = 10
DEFAULT_CHARSET = "asdfghjkl"

# Classes
class MyClass:
    """Class docstring"""

    def __init__(self):
        """Constructor docstring"""
        self.attribute = value

    def my_method(self, arg: str) -> bool:
        """
        Method docstring

        Args:
            arg: Argument description

        Returns:
            Return value description
        """
        pass

# Functions
def my_function(param1: int, param2: str) -> Dict:
    """
    Function docstring

    Args:
        param1: Parameter description
        param2: Parameter description

    Returns:
        Return value description
    """
    pass
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `HotkeyManager`)
- **Functions/Methods**: `snake_case` (e.g., `get_clickable_elements`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_DEPTH`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

### Documentation

- All public classes/functions must have docstrings
- Use Google-style docstrings
- Include type hints where possible

---

## Testing

### Running Tests

```bash
# Run all tests
python tests/test_all.py

# Test individual components
python src/core/label_generator.py
python src/core/element_detector.py
```

### Writing Tests

```python
# tests/test_my_feature.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_my_feature():
    """Test description"""
    # Arrange
    component = MyComponent()

    # Act
    result = component.my_method()

    # Assert
    assert result == expected_value, "Failure message"

if __name__ == "__main__":
    test_my_feature()
    print("✅ Test passed")
```

---

## Adding New Features

### Adding a New Mode

1. Create mode file: `src/modes/my_mode.py`

```python
class MyMode:
    """My custom mode"""

    def __init__(self):
        self.active = False

    def activate(self):
        """Activate mode"""
        self.active = True
        # Implementation

    def deactivate(self):
        """Deactivate mode"""
        self.active = False
        # Cleanup
```

2. Add mode to `ModeManager`:

```python
# src/modes/mode_manager.py
class Mode(Enum):
    IDLE = "idle"
    HINT = "hint"
    GRID = "grid"
    MY_MODE = "my_mode"  # Add new mode
```

3. Integrate in `main.py`:

```python
# Import
from modes.my_mode import MyMode

# Register callback
def _on_trigger():
    mode = MyMode()
    mode.activate()
```

### Adding a New Hotkey

```python
# main.py
def __init__(self):
    # ...
    self.hotkey_manager.register_hotkey('my_key', self._on_my_key)

def _on_my_key(self):
    """Handle my key press"""
    print("My key pressed!")
```

---

## Debugging

### Enabling Debug Logging

```python
# src/utils/logger.py
logger = HEMouseLogger()
logger.debug("Debug message")
```

Logs are saved to `logs/hemouse_YYYYMMDD.log`

### Common Issues

**Issue**: Element detection is slow
```python
# Add timing
import time
start = time.time()
elements = detector.get_clickable_elements()
print(f"Detection took {time.time() - start:.2f}s")
```

**Issue**: Labels not showing
```python
# Check overlay creation
print(f"Overlay root: {overlay.root}")
print(f"Canvas: {overlay.canvas}")
```

**Issue**: Keyboard input not captured
```python
# Check focus
print(f"Focus window: {win32gui.GetForegroundWindow()}")
```

---

## Building

### Create Executable

```bash
python build.py
```

Output: `dist/HEMouse.exe`

### Build Options

```python
# build.py
PyInstaller.__main__.run([
    'main.py',
    '--onefile',           # Single file
    '--windowed',          # No console
    '--name=HEMouse',     # Output name
    '--icon=icon.ico',    # Custom icon
])
```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile element detection
profiler = cProfile.Profile()
profiler.enable()

elements = detector.get_clickable_elements()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(10)
```

### Optimization Targets

1. **Element Detection**: < 500ms
2. **Label Generation**: < 10ms
3. **Overlay Rendering**: < 100ms
4. **Keyboard Response**: < 50ms

---

## Contributing

### Workflow

1. **Fork** repository on GitHub
2. **Clone** your fork
3. **Create branch**: `git checkout -b feature/my-feature`
4. **Make changes** and test
5. **Commit**: `git commit -m "Add my feature"`
6. **Push**: `git push origin feature/my-feature`
7. **Open Pull Request** on GitHub

### PR Guidelines

- Clear description of changes
- Include tests if applicable
- Update documentation
- Follow coding standards
- One feature per PR

### Code Review Process

1. Automated tests must pass
2. Code review by maintainer
3. Address feedback
4. Merge when approved

---

## Release Process

### Version Numbers

Format: `MAJOR.MINOR.PATCH` (Semantic Versioning)

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

Example: `1.2.3`

### Creating a Release

1. Update version in `README.md`
2. Update CHANGELOG (create if missing)
3. Tag release: `git tag v1.0.0`
4. Build executable: `python build.py`
5. Create GitHub release with binary

---

## Troubleshooting Development

### Import Errors

```bash
# Add src to Python path
set PYTHONPATH=%PYTHONPATH%;src  # Windows CMD
$env:PYTHONPATH += ";src"        # PowerShell
```

### PyInstaller Issues

```bash
# Clean build
pyinstaller --clean main.spec

# Debug mode
pyinstaller --debug=all main.py
```

### Windows Permissions

Some operations require admin:
```bash
# Run as admin
runas /user:Administrator python main.py
```

---

## Resources

### Documentation

- [pywin32 Docs](https://github.com/mhammond/pywin32)
- [pywinauto Docs](https://pywinauto.readthedocs.io/)
- [Windows UIA](https://docs.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32)

### Related Projects

- [Vimium](https://github.com/philc/vimium) - Browser hint mode
- [Homerow](https://www.homerow.app/) - macOS hint mode
- [Talon](https://talonvoice.com/) - Voice control

---

## Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: dev@hemouse.dev (placeholder)

---

**Happy coding! 🚀**