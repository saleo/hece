"""
HEMouse - Hands-Free Mouse Control
Main application entry point

Usage:
    python main.py

Controls:
    CapsLock - Activate/Deactivate Hint mode
    a-z - Type labels to select elements
    Space - Switch to Grid mode
    1-9 - Select grid cell (in Grid mode)
    ESC - Exit current mode
    Ctrl+C - Exit application
"""
import sys
import time
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.hotkey_manager import HotkeyManager
from core.element_detector import ElementDetector
from core.label_generator import LabelGenerator
from ui.overlay_window import OverlayWindow
from modes.hint_mode import HintMode
from modes.mode_manager import ModeManager, Mode


class HEMouseApp:
    """HEMouse main application"""

    def __init__(self):
        print("=" * 60)
        print("HEMouse - Hands-Free Mouse Control")
        print("=" * 60)

        # Initialize components
        print("🔧 Initializing components...")
        self.hotkey_manager = HotkeyManager()
        self.mode_manager = ModeManager()
        self.element_detector = ElementDetector()
        self.label_generator = LabelGenerator()

        self.hint_mode = None
        print("✅ Components initialized\n")

    def start(self):
        """Start the application"""
        print("🚀 Starting HEMouse...")

        # Register CapsLock hotkey callbacks
        self.hotkey_manager.register_hotkey('capslock_on', self._on_capslock_on)
        self.hotkey_manager.register_hotkey('capslock_off', self._on_capslock_off)

        # Start hotkey monitoring
        self.hotkey_manager.start_monitoring()

        print("\n" + "=" * 60)
        print("✅ HEMouse is ready!")
        print("=" * 60)
        print("\n📖 Quick Start Guide:")
        print("   1. Press CapsLock to activate Hint mode")
        print("   2. Type labels (a-z) to select elements")
        print("   3. Press Space to switch to Grid mode")
        print("   4. Press ESC to exit current mode")
        print("   5. Press Ctrl+C to exit HEMouse")
        print("\n⌛ Waiting for CapsLock...\n")

        # Main loop
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()

    def _on_capslock_on(self):
        """Handle CapsLock ON event"""
        if self.mode_manager.get_current_mode() == Mode.IDLE:
            self.mode_manager.switch_mode(Mode.HINT)
            self._activate_hint_mode()

    def _on_capslock_off(self):
        """Handle CapsLock OFF event"""
        if self.mode_manager.get_current_mode() == Mode.HINT:
            if self.hint_mode:
                self.hint_mode.deactivate()
            self.mode_manager.switch_mode(Mode.IDLE)

    def _activate_hint_mode(self):
        """Activate Hint mode"""
        overlay = OverlayWindow()
        self.hint_mode = HintMode(overlay, self.element_detector, self.label_generator)

        try:
            self.hint_mode.activate()
        except Exception as e:
            print(f"❌ Hint mode error: {e}")
        finally:
            # Return to IDLE after Hint mode exits
            self.mode_manager.switch_mode(Mode.IDLE)
            print("⌛ Ready for next CapsLock press...\n")

    def stop(self):
        """Stop the application"""
        print("\n" + "=" * 60)
        print("🛑 Stopping HEMouse...")
        print("=" * 60)

        self.hotkey_manager.stop_monitoring()

        print("✅ HEMouse stopped")
        print("👋 Goodbye!\n")
        sys.exit(0)


def main():
    """Main entry point"""
    try:
        app = HEMouseApp()
        app.start()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()