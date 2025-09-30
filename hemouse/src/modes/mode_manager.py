"""
HEMouse Mode Manager
Manages mode transitions (IDLE, HINT, GRID)
"""
from enum import Enum


class Mode(Enum):
    """Available modes"""
    IDLE = "idle"
    HINT = "hint"
    GRID = "grid"


class ModeManager:
    """Mode state manager"""

    def __init__(self):
        self.current_mode = Mode.IDLE
        self.callbacks = {
            'on_mode_enter': {},
            'on_mode_exit': {}
        }

    def register_callback(self, event, mode, callback):
        """
        Register mode transition callback

        Args:
            event: 'on_mode_enter' or 'on_mode_exit'
            mode: Mode enum value
            callback: Function to call
        """
        if event not in self.callbacks:
            self.callbacks[event] = {}
        self.callbacks[event][mode] = callback

    def switch_mode(self, new_mode):
        """
        Switch to new mode

        Args:
            new_mode: Mode enum value
        """
        if new_mode == self.current_mode:
            return

        old_mode = self.current_mode

        # Trigger exit callback
        if old_mode in self.callbacks['on_mode_exit']:
            try:
                self.callbacks['on_mode_exit'][old_mode]()
            except Exception as e:
                print(f"❌ Exit callback error: {e}")

        # Switch mode
        self.current_mode = new_mode
        print(f"🔄 Mode changed: {old_mode.value} → {new_mode.value}")

        # Trigger enter callback
        if new_mode in self.callbacks['on_mode_enter']:
            try:
                self.callbacks['on_mode_enter'][new_mode]()
            except Exception as e:
                print(f"❌ Enter callback error: {e}")

    def get_current_mode(self):
        """Get current mode"""
        return self.current_mode


# Test code
if __name__ == "__main__":
    manager = ModeManager()

    def on_hint_enter():
        print("✅ Entered Hint mode")

    def on_hint_exit():
        print("❌ Exited Hint mode")

    def on_grid_enter():
        print("✅ Entered Grid mode")

    manager.register_callback('on_mode_enter', Mode.HINT, on_hint_enter)
    manager.register_callback('on_mode_exit', Mode.HINT, on_hint_exit)
    manager.register_callback('on_mode_enter', Mode.GRID, on_grid_enter)

    print(f"Current mode: {manager.get_current_mode()}")
    manager.switch_mode(Mode.HINT)
    print(f"Current mode: {manager.get_current_mode()}")
    manager.switch_mode(Mode.GRID)
    print(f"Current mode: {manager.get_current_mode()}")
    manager.switch_mode(Mode.IDLE)