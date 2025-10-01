"""
HEMouse Hotkey Manager
Monitors CapsLock state changes using Windows API polling
"""
import win32api
import win32con
import threading
import time


class HotkeyManager:
    """Global hotkey manager for CapsLock detection"""

    def __init__(self):
        self.running = False
        self.callbacks = {}
        self.thread = None
        self.poll_interval = 0.015  # 15ms polling interval for faster response

    def register_hotkey(self, key_name, callback):
        """
        Register a callback for hotkey events

        Args:
            key_name: 'capslock_on' or 'capslock_off'
            callback: Function to call when event occurs
        """
        self.callbacks[key_name] = callback

    def start_monitoring(self):
        """Start monitoring hotkeys in background thread"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("🟢 Hotkey monitoring started")

    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)"""
        # Use GetAsyncKeyState for global key state detection
        # Check bit 0 (0x0001) for toggle state (ON/OFF)
        prev_capslock_state = win32api.GetAsyncKeyState(win32con.VK_CAPITAL) & 0x0001

        while self.running:
            try:
                # Check global CapsLock toggle state
                curr_state = win32api.GetAsyncKeyState(win32con.VK_CAPITAL) & 0x0001

                # Detect state change
                if curr_state != prev_capslock_state:
                    if curr_state == 1:  # CapsLock ON
                        print("🔔 CapsLock ON detected (global)")
                        if 'capslock_on' in self.callbacks:
                            self.callbacks['capslock_on']()
                    else:  # CapsLock OFF
                        print("🔔 CapsLock OFF detected (global)")
                        if 'capslock_off' in self.callbacks:
                            self.callbacks['capslock_off']()

                    prev_capslock_state = curr_state

            except Exception as e:
                print(f"❌ Hotkey monitor error: {e}")

            time.sleep(self.poll_interval)

    def stop_monitoring(self):
        """Stop monitoring hotkeys"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        print("🔴 Hotkey monitoring stopped")


# Test code
if __name__ == "__main__":
    def on_capslock_on():
        print("✅ CapsLock ON - Hint mode activated")

    def on_capslock_off():
        print("❌ CapsLock OFF - Hint mode deactivated")

    manager = HotkeyManager()
    manager.register_hotkey('capslock_on', on_capslock_on)
    manager.register_hotkey('capslock_off', on_capslock_off)
    manager.start_monitoring()

    print("Press CapsLock to test... Ctrl+C to exit")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_monitoring()
        print("Goodbye!")