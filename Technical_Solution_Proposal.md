# HEMouse Technical Solution Proposal
**Based on Latest Research & GitHub Repositories (2024-2025)**

---

## Executive Summary

This proposal outlines a **feasible, state-of-the-art technical architecture** for HEMouse v2, integrating:
- **Low-resource facial gesture recognition** (MediaPipe + lightweight models)
- **Mode-based keyboard control** (mouseMaster-inspired architecture)
- **Multi-monitor head tracking** (dual eye-tracker approach)
- **Hint mode with UI element detection** (Windows UIA API)

**Key Innovation**: Hybrid system that seamlessly switches between CV-based and keyboard-based control based on resource availability and user context.

---

## 1. Facial Gesture & Head Tracking Module

### 1.1 Core Technology Stack

#### **Primary Framework: MediaPipe (Google AI Edge)**
- **Face Landmarker**: 478 3D landmarks + 52 blendshape scores
- **Head Pose Estimation**: Yaw, pitch, roll angles via solvePnP
- **Performance**: 30+ FPS on CPU (Intel i7-1165G7 compatible)
- **Resource Usage**: <10W power, <100MB memory

**Implementation**:
```python
import mediapipe as mp
import cv2
import numpy as np

class FacialGestureDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_head_pose(self, landmarks, image_shape):
        """
        Extract head pose (yaw, pitch, roll) from landmarks
        Using landmarks: nose tip, chin, left/right eye corners, mouth corners
        """
        # Key landmark indices (MediaPipe 468 landmarks)
        nose_tip = landmarks[1]
        chin = landmarks[152]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        left_mouth = landmarks[61]
        right_mouth = landmarks[291]

        # 2D image points
        image_points = np.array([
            nose_tip[:2],
            chin[:2],
            left_eye[:2],
            right_eye[:2],
            left_mouth[:2],
            right_mouth[:2]
        ], dtype="double")

        # 3D model points (generic face model)
        model_points = np.array([
            (0.0, 0.0, 0.0),         # Nose tip
            (0.0, -330.0, -65.0),    # Chin
            (-225.0, 170.0, -135.0), # Left eye left corner
            (225.0, 170.0, -135.0),  # Right eye right corner
            (-150.0, -150.0, -125.0),# Left Mouth corner
            (150.0, -150.0, -125.0)  # Right Mouth corner
        ])

        # Camera matrix (approximation)
        focal_length = image_shape[1]
        center = (image_shape[1]/2, image_shape[0]/2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix,
            None, flags=cv2.SOLVEPNP_ITERATIVE
        )

        # Convert rotation vector to Euler angles
        rotation_mat, _ = cv2.Rodrigues(rotation_vector)
        pose_mat = cv2.hconcat((rotation_mat, translation_vector))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)

        pitch, yaw, roll = euler_angles.flatten()[:3]
        return pitch, yaw, roll

    def detect_smile(self, blendshapes):
        """
        Detect smile intensity using MediaPipe blendshapes
        Blendshape indices: mouthSmileLeft (44), mouthSmileRight (45)
        """
        if blendshapes:
            smile_left = blendshapes[44].score
            smile_right = blendshapes[45].score
            smile_intensity = (smile_left + smile_right) / 2.0

            # Classify smile levels
            if smile_intensity > 0.7:
                return "big_smile"
            elif smile_intensity > 0.4:
                return "medium_smile"
            elif smile_intensity > 0.2:
                return "small_smile"
        return "neutral"

    def detect_mouth_gesture(self, blendshapes):
        """
        Detect mouth gestures: whistle, open, kiss
        """
        if blendshapes:
            mouth_pucker = blendshapes[36].score  # mouthPucker
            jaw_open = blendshapes[25].score      # jawOpen
            mouth_funnel = blendshapes[28].score  # mouthFunnel

            if mouth_pucker > 0.6:
                return "whistle"
            elif jaw_open > 0.5:
                return "mouth_open"
            elif mouth_funnel > 0.5:
                return "deep_breath"
        return "neutral"
```

**Reference Implementation**:
- https://github.com/shenasa-ai/head-pose-estimation
- https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker

---

### 1.2 Advanced Gesture Recognition (Optional Enhancement)

#### **Lip Reading for Command Input**
**Technology**: LipCoordNet + 3D CNN
**Use Case**: Silent voice commands for advanced users

**GitHub References**:
- https://github.com/Mabhusubhani001/LIP-READING-AI (97%+ accuracy)
- https://github.com/allenye66/Computer-Vision-Lip-Reading-2.0 (99.2% test accuracy)

**Implementation Strategy**:
- Phase 1: Pre-defined gesture set (whistle, kiss, open mouth)
- Phase 2: Word recognition for power users (optional Pro feature)

---

### 1.3 Multi-Monitor Head Tracking

#### **Challenge**: Single webcam tracking across 2+ monitors

**Solution**: Combined approach inspired by dual eye-tracker research

**Algorithm**:
```python
class MultiMonitorTracker:
    def __init__(self, monitors):
        self.monitors = monitors
        self.calibration_data = {}

    def calibrate(self):
        """
        User looks at each monitor center for 2 seconds
        Store head pose angles for each monitor
        """
        for monitor_id, monitor in enumerate(self.monitors):
            print(f"Look at center of Monitor {monitor_id+1}")
            time.sleep(2)

            # Capture multiple samples
            samples = []
            for _ in range(30):  # 1 second at 30fps
                pitch, yaw, roll = self.get_head_pose()
                samples.append((pitch, yaw, roll))

            # Store average pose for this monitor
            self.calibration_data[monitor_id] = {
                'pitch': np.mean([s[0] for s in samples]),
                'yaw': np.mean([s[1] for s in samples]),
                'roll': np.mean([s[2] for s in samples]),
                'bounds': monitor
            }

    def detect_target_monitor(self, current_pitch, current_yaw):
        """
        Determine which monitor user is looking at
        Using angular distance from calibrated positions
        """
        min_distance = float('inf')
        target_monitor = 0

        for monitor_id, calib in self.calibration_data.items():
            # Calculate angular distance (simplified)
            distance = np.sqrt(
                (current_pitch - calib['pitch'])**2 +
                (current_yaw - calib['yaw'])**2
            )

            if distance < min_distance:
                min_distance = distance
                target_monitor = monitor_id

        return target_monitor

    def get_cursor_position_on_monitor(self, pitch, yaw, monitor_id):
        """
        Map head pose to cursor position within target monitor
        Using normalized angles relative to monitor center
        """
        calib = self.calibration_data[monitor_id]
        bounds = calib['bounds']

        # Normalize angles (-1 to 1 range)
        # Sensitivity: 15 degrees = full screen width/height
        norm_x = (yaw - calib['yaw']) / 15.0
        norm_y = (pitch - calib['pitch']) / 15.0

        # Clamp to [-1, 1]
        norm_x = max(-1, min(1, norm_x))
        norm_y = max(-1, min(1, norm_y))

        # Map to monitor coordinates
        monitor_width = bounds['right'] - bounds['left']
        monitor_height = bounds['bottom'] - bounds['top']

        cursor_x = bounds['left'] + (norm_x + 1) * monitor_width / 2
        cursor_y = bounds['top'] + (norm_y + 1) * monitor_height / 2

        return int(cursor_x), int(cursor_y)
```

**Research Reference**: "Combining Low-Cost Eye Trackers for Dual Monitor Eye Tracking" (Springer 2016)

---

## 2. Mode-Based Keyboard Control Module

### 2.1 Architecture Overview

**Inspired by**: mousemaster (petoncle/mousemaster)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Callable

class ControlMode(Enum):
    IDLE = "idle"
    NORMAL = "normal"      # IJKL directional control
    GRID = "grid"          # Progressive grid refinement
    HINT = "hint"          # Element-labeled navigation
    SCREEN_SELECT = "screen_select"  # Multi-monitor switching
    FACIAL_GESTURE = "facial_gesture"  # CV-based control

@dataclass
class KeyBinding:
    keys: tuple
    action: Callable
    mode: ControlMode
    timing: str = "press"  # "press", "hold", "double", "sequence"
    hold_duration: float = 0.3  # For timed holds

class ModeManager:
    def __init__(self):
        self.current_mode = ControlMode.IDLE
        self.mode_stack = []  # For nested modes
        self.key_bindings: Dict[ControlMode, List[KeyBinding]] = {}
        self.mode_transitions = {}

    def register_binding(self, binding: KeyBinding):
        """Register key binding for specific mode"""
        if binding.mode not in self.key_bindings:
            self.key_bindings[binding.mode] = []
        self.key_bindings[binding.mode].append(binding)

    def switch_mode(self, new_mode: ControlMode, push_to_stack=False):
        """Switch to new mode with optional stack push for return"""
        if push_to_stack:
            self.mode_stack.append(self.current_mode)

        self.on_mode_exit(self.current_mode)
        self.current_mode = new_mode
        self.on_mode_enter(new_mode)

    def return_to_previous_mode(self):
        """Pop mode from stack and return"""
        if self.mode_stack:
            previous_mode = self.mode_stack.pop()
            self.switch_mode(previous_mode)

    def handle_key_event(self, key, event_type):
        """Route key event to current mode's handlers"""
        mode_bindings = self.key_bindings.get(self.current_mode, [])

        for binding in mode_bindings:
            if self._matches_binding(key, event_type, binding):
                binding.action()
                return True

        return False

    def on_mode_enter(self, mode: ControlMode):
        """Handle mode entry (show overlays, initialize state)"""
        if mode == ControlMode.GRID:
            self.show_grid_overlay()
        elif mode == ControlMode.HINT:
            self.show_hint_overlay()
        elif mode == ControlMode.FACIAL_GESTURE:
            self.start_cv_pipeline()

    def on_mode_exit(self, mode: ControlMode):
        """Handle mode exit (cleanup)"""
        if mode in [ControlMode.GRID, ControlMode.HINT]:
            self.hide_overlay()
        elif mode == ControlMode.FACIAL_GESTURE:
            self.pause_cv_pipeline()
```

---

### 2.2 Hint Mode Implementation

**Technology**: Windows UI Automation API via pywinauto

**GitHub Reference**: https://github.com/jaywcjlove/mousio-hint

```python
import pywinauto
from pywinauto import Desktop
from pywinauto.uia_defines import IUIA

class HintModeController:
    def __init__(self):
        self.desktop = Desktop(backend="uia")
        self.hints = {}
        self.hint_labels = []

    def generate_hints(self, scope="active_window"):
        """
        Detect focusable UI elements and assign hint labels
        """
        self.hints.clear()
        self.hint_labels.clear()

        # Get elements
        if scope == "active_window":
            window = self.desktop.windows()[0]  # Active window
            elements = self._get_interactive_elements(window)
        else:
            elements = self._get_interactive_elements(self.desktop)

        # Generate labels (a-z, aa-zz pattern)
        labels = self._generate_label_sequence(len(elements))

        for element, label in zip(elements, labels):
            try:
                rect = element.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                self.hints[label] = {
                    'element': element,
                    'position': (center_x, center_y),
                    'rect': rect,
                    'type': element.element_info.control_type
                }
                self.hint_labels.append(label)
            except Exception as e:
                continue

        return self.hints

    def _get_interactive_elements(self, container):
        """
        Find all interactive/clickable UI elements
        """
        interactive_types = [
            'Button', 'CheckBox', 'ComboBox', 'Edit',
            'Hyperlink', 'Image', 'ListItem', 'MenuItem',
            'RadioButton', 'TabItem', 'TreeItem'
        ]

        elements = []
        try:
            for element in container.descendants():
                if element.element_info.control_type in interactive_types:
                    if element.is_visible() and element.is_enabled():
                        elements.append(element)
        except Exception:
            pass

        return elements

    def _generate_label_sequence(self, count):
        """
        Generate hint labels: a-z, aa-az, ba-bz, ..., za-zz
        """
        labels = []
        chars = 'abcdefghijklmnopqrstuvwxyz'

        # Single letters (26)
        for c in chars:
            labels.append(c)
            if len(labels) >= count:
                return labels[:count]

        # Double letters (676)
        for c1 in chars:
            for c2 in chars:
                labels.append(c1 + c2)
                if len(labels) >= count:
                    return labels[:count]

        return labels[:count]

    def jump_to_hint(self, label):
        """
        Move cursor to hint position and optionally click
        """
        if label in self.hints:
            hint = self.hints[label]
            pos = hint['position']

            # Move cursor
            pyautogui.moveTo(pos[0], pos[1], duration=0.1)

            # Optional: Auto-click for buttons
            if hint['type'] == 'Button':
                pyautogui.click()

            return True
        return False
```

**Overlay Rendering** (Qt-based for cross-platform):
```python
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

class HintOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.hints = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Full screen overlay
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def set_hints(self, hints):
        """Update hints to display"""
        self.hints = hints
        self.update()

    def paintEvent(self, event):
        """Draw hint labels on overlay"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont("Arial", 12, QFont.Bold)
        painter.setFont(font)

        for label, hint_data in self.hints.items():
            pos = hint_data['position']

            # Draw background box
            painter.setBrush(QColor(255, 200, 0, 180))
            painter.setPen(QColor(0, 0, 0))
            rect = QRect(pos[0]-20, pos[1]-15, 40, 30)
            painter.drawRoundedRect(rect, 5, 5)

            # Draw label text
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(rect, Qt.AlignCenter, label)
```

---

### 2.3 Grid Mode (Enhanced from Current Implementation)

**Improvements**:
1. **Adaptive grid size**: 6x6, 9x9, 12x12 based on screen resolution
2. **Scope options**: Full screen, active monitor, active window
3. **Multi-level refinement**: Progressive zoom into selected cells

```python
class GridModeController:
    def __init__(self):
        self.grid_levels = []
        self.current_level = 0
        self.grid_size = (6, 6)  # Default 36 cells

    def show_grid(self, scope="active_monitor", grid_size=(6, 6)):
        """
        Display grid overlay on specified scope
        """
        self.grid_size = grid_size
        self.current_level = 0

        # Get bounds
        if scope == "active_monitor":
            bounds = self._get_active_monitor_bounds()
        elif scope == "active_window":
            bounds = self._get_active_window_bounds()
        else:  # full_screen
            bounds = self._get_full_screen_bounds()

        self.grid_levels = [bounds]
        self._render_grid(bounds)

    def select_cell(self, cell_number):
        """
        Select grid cell and zoom into it (or click if final level)
        """
        bounds = self.grid_levels[self.current_level]
        cell_bounds = self._calculate_cell_bounds(bounds, cell_number)

        if self.current_level < 1:  # Multi-level navigation
            # Zoom into cell
            self.current_level += 1
            self.grid_levels.append(cell_bounds)
            self._render_grid(cell_bounds)
        else:
            # Final level: Move cursor to cell center
            center_x = (cell_bounds['left'] + cell_bounds['right']) // 2
            center_y = (cell_bounds['top'] + cell_bounds['bottom']) // 2
            pyautogui.moveTo(center_x, center_y)
            self.hide_grid()

    def _calculate_cell_bounds(self, bounds, cell_number):
        """Calculate bounds for specific cell in grid"""
        rows, cols = self.grid_size
        row = cell_number // cols
        col = cell_number % cols

        width = bounds['right'] - bounds['left']
        height = bounds['bottom'] - bounds['top']

        cell_width = width / cols
        cell_height = height / rows

        return {
            'left': bounds['left'] + col * cell_width,
            'top': bounds['top'] + row * cell_height,
            'right': bounds['left'] + (col + 1) * cell_width,
            'bottom': bounds['top'] + (row + 1) * cell_height
        }
```

---

### 2.4 Normal Mode (IJKL Control)

**Inspired by**: Vim movement, mousemaster normal mode

```python
class NormalModeController:
    def __init__(self):
        self.movement_speed = {
            'slow': 5,      # Pixel-precise
            'normal': 20,   # Standard
            'fast': 50      # Rapid movement
        }
        self.current_speed = 'normal'
        self.acceleration = 1.0

    def move_cursor(self, direction, modifier=None):
        """
        Move cursor in specified direction
        Modifiers: 'shift' (fast), 'ctrl' (slow)
        """
        x, y = pyautogui.position()

        # Determine speed
        if modifier == 'shift':
            speed = self.movement_speed['fast']
        elif modifier == 'ctrl':
            speed = self.movement_speed['slow']
        else:
            speed = self.movement_speed['normal']

        # Apply acceleration (increases with repeated key presses)
        speed = int(speed * self.acceleration)

        # Calculate new position
        if direction == 'up':
            y -= speed
        elif direction == 'down':
            y += speed
        elif direction == 'left':
            x -= speed
        elif direction == 'right':
            x += speed

        pyautogui.moveTo(x, y)

        # Increment acceleration (capped at 3x)
        self.acceleration = min(3.0, self.acceleration + 0.1)

    def reset_acceleration(self):
        """Reset acceleration when movement stops"""
        self.acceleration = 1.0
```

---

## 3. Configuration & Persistence System

### 3.1 Configuration Architecture

**Inspired by**: mousemaster properties system + modern JSON

```yaml
# config/default.json
{
  "global": {
    "startup_mode": "idle",
    "activation_hotkey": "capslock+capslock",
    "exit_hotkey": "capslock+escape"
  },

  "modes": {
    "grid": {
      "grid_size": [6, 6],
      "default_scope": "active_monitor",
      "multi_level": true,
      "animation_speed": 100
    },

    "hint": {
      "label_style": "letters",
      "auto_click_buttons": true,
      "hint_color": "#FFC800",
      "font_size": 12
    },

    "normal": {
      "movement_keys": {
        "up": "i",
        "down": "k",
        "left": "j",
        "right": "l"
      },
      "speed_slow": 5,
      "speed_normal": 20,
      "speed_fast": 50,
      "acceleration_enabled": true
    },

    "facial_gesture": {
      "enabled": true,
      "min_detection_confidence": 0.5,
      "smile_threshold": {
        "small": 0.2,
        "medium": 0.4,
        "big": 0.7
      },
      "head_tracking": {
        "enabled": true,
        "sensitivity": 15,
        "multi_monitor": true
      }
    }
  },

  "key_bindings": {
    "global": {
      "capslock+space": "grid_current_monitor",
      "capslock+up": "grid_monitor_up",
      "capslock+down": "grid_monitor_down",
      "capslock+left": "grid_monitor_left",
      "capslock+right": "grid_monitor_right"
    },

    "grid_mode": {
      "0-9": "select_cell",
      "escape": "exit_mode",
      "backspace": "zoom_out"
    },

    "hint_mode": {
      "a-z": "jump_to_hint",
      "escape": "exit_mode"
    },

    "normal_mode": {
      "i": "move_up",
      "k": "move_down",
      "j": "move_left",
      "l": "move_right",
      "shift+i": "move_up_fast",
      "space": "click",
      "shift+space": "right_click"
    }
  },

  "application_profiles": {
    "chrome.exe": {
      "preferred_mode": "hint",
      "disable_facial_gesture": false
    },
    "code.exe": {
      "preferred_mode": "normal",
      "disable_facial_gesture": true
    }
  }
}
```

### 3.2 Configuration Manager

```python
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config = {}
        self.observers = []
        self.reload_callbacks = []

        self.load_config()
        self.start_file_watcher()

    def load_config(self):
        """Load configuration from JSON files"""
        # Load default config
        default_config = self.config_dir / "default.json"
        with open(default_config) as f:
            self.config = json.load(f)

        # Load user overrides if exists
        user_config = self.config_dir / "user.json"
        if user_config.exists():
            with open(user_config) as f:
                user_overrides = json.load(f)
                self._deep_merge(self.config, user_overrides)

    def start_file_watcher(self):
        """Watch config files for changes and auto-reload"""
        event_handler = ConfigFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.config_dir), recursive=False)
        observer.start()
        self.observers.append(observer)

    def on_config_changed(self):
        """Trigger reload when config files change"""
        print("Config changed, reloading...")
        self.load_config()

        for callback in self.reload_callbacks:
            callback(self.config)

    def get(self, key_path, default=None):
        """Get config value by dot-notation path"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def _deep_merge(self, base, override):
        """Recursively merge override dict into base dict"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if event.src_path.endswith('.json'):
            self.config_manager.on_config_changed()
```

---

## 4. System Integration & Performance

### 4.1 Threading Architecture

```python
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

class HEMouseCore:
    def __init__(self):
        self.mode_manager = ModeManager()
        self.config_manager = ConfigManager()

        # Separate threads for different concerns
        self.cv_thread = None
        self.keyboard_thread = None
        self.overlay_thread = None

        # Communication queues
        self.cv_queue = queue.Queue(maxsize=2)  # Latest CV results
        self.command_queue = queue.Queue()

        self.running = False

    def start(self):
        """Start all system threads"""
        self.running = True

        # CV pipeline (low priority, async)
        self.cv_thread = threading.Thread(
            target=self._cv_pipeline,
            daemon=True,
            name="CV-Pipeline"
        )
        self.cv_thread.start()

        # Keyboard handler (high priority, sync)
        self.keyboard_thread = threading.Thread(
            target=self._keyboard_handler,
            daemon=False,
            name="Keyboard-Handler"
        )
        self.keyboard_thread.start()

        # Overlay renderer (medium priority)
        self.overlay_thread = threading.Thread(
            target=self._overlay_renderer,
            daemon=True,
            name="Overlay-Renderer"
        )
        self.overlay_thread.start()

    def _cv_pipeline(self):
        """Computer vision processing loop"""
        detector = FacialGestureDetector()
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            # Process frame (async, non-blocking)
            results = detector.process_frame(frame)

            # Put latest results in queue (drop old if full)
            if self.cv_queue.full():
                try:
                    self.cv_queue.get_nowait()
                except queue.Empty:
                    pass

            self.cv_queue.put(results)

            # Throttle to 30 FPS max
            time.sleep(1/30)

        cap.release()

    def _keyboard_handler(self):
        """Keyboard event processing loop"""
        keyboard.on_press(self._on_key_press)
        keyboard.on_release(self._on_key_release)
        keyboard.wait()  # Block until exit

    def _on_key_press(self, event):
        """Handle key press events"""
        handled = self.mode_manager.handle_key_event(event.name, 'press')

        # Suppress key if handled (prevent propagation to apps)
        if handled:
            return False

    def _overlay_renderer(self):
        """Qt overlay rendering loop"""
        app = QApplication([])

        self.grid_overlay = GridOverlay()
        self.hint_overlay = HintOverlay()

        app.exec_()
```

### 4.2 Performance Optimizations

**Target Metrics**:
- CV pipeline: 30 FPS @ <10W power
- Keyboard latency: <50ms press-to-action
- Mode transition: <50ms
- Memory usage: <200MB total

**Optimization Strategies**:

1. **CV Pipeline**:
   - Use MediaPipe's lightweight models (no GPU required)
   - Process at 30 FPS, drop frames if processing lags
   - Async processing with non-blocking queue

2. **Keyboard Input**:
   - Direct event hooks (no polling)
   - Priority thread for zero-latency response
   - Efficient key combination matching

3. **Overlay Rendering**:
   - GPU-accelerated Qt rendering
   - Lazy updates (only redraw on change)
   - Transparent window optimization

4. **Memory Management**:
   - Reuse frame buffers
   - Limit queue sizes (drop old data)
   - Lazy load application profiles

---

## 5. Recommended Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up project structure
- [ ] Implement ModeManager with state machine
- [ ] Create configuration system with JSON support
- [ ] Develop Qt overlay base classes
- [ ] Port existing grid mode to new architecture

### Phase 2: Keyboard Modes (Weeks 3-5)
- [ ] Implement Hint Mode with Windows UIA
- [ ] Develop Normal Mode (IJKL control)
- [ ] Add Screen Selection mode
- [ ] Create key binding parser (timed, nested)
- [ ] Build overlay renderers for each mode

### Phase 3: CV Integration (Weeks 6-8)
- [ ] Integrate MediaPipe Face Landmarker
- [ ] Implement head pose estimation
- [ ] Add smile detection with blendshapes
- [ ] Develop multi-monitor calibration system
- [ ] Connect CV pipeline to mode system

### Phase 4: Advanced Features (Weeks 9-10)
- [ ] Application-specific profiles
- [ ] Live config reload
- [ ] Position history (jump-back)
- [ ] Health monitoring (posture reminders)
- [ ] Performance profiling & optimization

### Phase 5: Testing & Polish (Weeks 11-12)
- [ ] Comprehensive testing (functional, performance)
- [ ] User acceptance testing
- [ ] Documentation (user + developer)
- [ ] Installer creation
- [ ] Pro/Free version split

---

## 6. Key Repositories for Reference

### Facial Gesture & Head Tracking
1. **MediaPipe Python**: https://github.com/google-ai-edge/mediapipe
2. **Head Pose Estimation**: https://github.com/shenasa-ai/head-pose-estimation
3. **OpenSeeFace**: https://github.com/emilianavt/OpenSeeFace
4. **Facial Emotion Recognition**: https://github.com/REWTAO/Facial-emotion-recognition-using-mediapipe

### Keyboard Mouse Control
1. **mouseMaster**: https://github.com/petoncle/mousemaster
2. **Mousio + Mousio Hint**: https://github.com/jaywcjlove/mousio
3. **Scoot (macOS)**: https://github.com/mjrusso/scoot
4. **wl-kbptr (Linux)**: https://github.com/moverest/wl-kbptr

### UI Automation
1. **pywinauto**: https://github.com/pywinauto/pywinauto
2. **Python-UIAutomation-for-Windows**: https://github.com/yinkaisheng/Python-UIAutomation-for-Windows

### Lip Reading (Optional)
1. **LIP-READING-AI**: https://github.com/Mabhusubhani001/LIP-READING-AI
2. **Computer-Vision-Lip-Reading-2.0**: https://github.com/allenye66/Computer-Vision-Lip-Reading-2.0

---

## 7. Technical Risks & Mitigation

### Risk 1: CV Performance on Target Hardware
**Mitigation**:
- MediaPipe is optimized for CPU-only execution
- Fallback to keyboard-only mode if FPS drops below 20
- User can disable CV features in config

### Risk 2: UI Element Detection Accuracy
**Mitigation**:
- pywinauto works well with modern Windows apps
- Grid mode as universal fallback
- Application whitelist for hint mode

### Risk 3: Multi-Monitor Calibration Complexity
**Mitigation**:
- Simple 5-point calibration (center of each monitor + center position)
- Re-calibration prompt if accuracy drops
- Manual monitor selection via keyboard shortcuts

### Risk 4: Key Binding Conflicts
**Mitigation**:
- Application-specific profiles
- Whitelist/blacklist system
- Global toggle to disable all bindings

### Risk 5: Learning Curve for Users
**Mitigation**:
- Progressive disclosure (start with grid mode only)
- Interactive tutorial on first launch
- Cheat sheet overlay (toggle with F1)
- Smart defaults that work out-of-box

---

## 8. Success Criteria

### Technical Metrics
- ✅ CV pipeline runs at 30 FPS with <10W power
- ✅ Keyboard input latency <50ms
- ✅ Memory usage <200MB
- ✅ Hint mode detects >90% of interactive elements
- ✅ Multi-monitor switching accuracy >95% after calibration

### User Experience Metrics
- ✅ Time to first successful click: <5 minutes (new users)
- ✅ Mouse speed parity: Within 2 weeks of daily use
- ✅ User-reported RSI improvement: >60% of users
- ✅ Daily active usage retention: >30 days (>70% of users)

### Business Metrics
- ✅ Open-source repo: >1000 stars in 6 months
- ✅ Pro version conversion: >10% of active users
- ✅ Community contributions: >20 PRs merged

---

## Conclusion

This technical solution leverages **state-of-the-art, production-ready technologies**:
- **MediaPipe** for efficient CV (proven at Google scale)
- **Windows UIA** for reliable UI automation
- **mouseMaster-inspired architecture** for keyboard control
- **Qt** for cross-platform overlay rendering

All components have **active GitHub repositories**, **comprehensive documentation**, and **proven performance** on target hardware specs.

The **hybrid design** (CV + keyboard) ensures **reliability** (keyboard fallback) while providing **unique value** (health-focused gestures).

**Estimated effort**: 12 weeks for full implementation by 1-2 experienced developers.

**Next steps**:
1. Set up development environment (Python 3.12, MediaPipe, PyQt5, pywinauto)
2. Create project skeleton with mode system
3. Port existing grid code to new architecture
4. Begin Phase 2 (Hint Mode) development

---

**Document Version**: 1.0
**Date**: 2025-09-28
**Author**: Technical Architecture Team
**Status**: Ready for Implementation