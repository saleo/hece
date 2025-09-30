"""
HEMouse Hint Mode
Core Hint mode controller with element detection and label matching
"""
import win32gui
import win32con
import win32api


class HintMode:
    """Hint mode controller"""

    def __init__(self, overlay_window, element_detector, label_generator):
        """
        Initialize Hint mode

        Args:
            overlay_window: OverlayWindow instance
            element_detector: ElementDetector instance
            label_generator: LabelGenerator instance
        """
        self.overlay = overlay_window
        self.detector = element_detector
        self.label_gen = label_generator

        self.elements = []
        self.labels = []
        self.current_input = ""
        self.active = False

    def activate(self):
        """Activate Hint mode"""
        if self.active:
            return

        print("\n🟢 Activating Hint mode...")

        # Step 1: Detect UI elements
        print("🔍 Detecting clickable elements...")
        self.elements = self.detector.get_clickable_elements()

        if len(self.elements) == 0:
            print("⚠️ No clickable elements found")
            win32api.MessageBeep(win32con.MB_ICONWARNING)
            return

        # Step 2: Generate labels
        print(f"🏷️ Generating labels for {len(self.elements)} elements...")
        self.labels = self.label_gen.generate_labels(len(self.elements))

        # Step 3: Create overlay window
        print("🎨 Creating overlay window...")
        self.overlay.create()
        self.overlay.draw_labels(self.elements, self.labels)

        # Step 4: Bind keyboard events
        self.overlay.root.bind('<KeyPress>', self._on_key_press)
        self.overlay.root.bind('<space>', self._on_space_press)

        self.current_input = ""
        self.active = True

        print("✅ Hint mode ready! Type labels to select elements")
        print("   Press Space for Grid mode, ESC to exit\n")

        # Run event loop (blocking)
        self.overlay.run_event_loop()

        # Cleanup when window closes
        self.active = False

    def deactivate(self):
        """Deactivate Hint mode"""
        if not self.active:
            return

        print("🔴 Deactivating Hint mode...")
        self.overlay.destroy()
        self.active = False
        self.current_input = ""

    def _on_key_press(self, event):
        """Handle keyboard input"""
        key = event.char.lower()

        # ESC to exit
        if event.keysym == 'Escape':
            self.deactivate()
            return

        # Only process alphabetic characters
        if not key.isalpha():
            return

        self.current_input += key
        print(f"📝 Current input: '{self.current_input}'")

        # Find matching labels
        matches = self.label_gen.match_label(self.current_input, self.labels)

        if len(matches) == 0:
            # No match - reset and beep
            print(f"❌ No match for '{self.current_input}'")
            self.current_input = ""
            win32api.MessageBeep(win32con.MB_ICONHAND)

        elif len(matches) == 1:
            # Unique match - click element
            matched_index = matches[0]
            matched_label = self.labels[matched_index]
            matched_element = self.elements[matched_index]

            print(f"✅ Matched: {matched_label} → Clicking element...")
            self._click_element(matched_element)
            self.deactivate()

        else:
            # Multiple matches - highlight
            matching_labels = [self.labels[i] for i in matches]
            print(f"🔵 {len(matches)} matches: {matching_labels}")
            self.overlay.highlight_matches(matching_labels)

    def _on_space_press(self, event):
        """Handle Space key - switch to Grid mode"""
        print("🔄 Space pressed - switching to Grid mode")
        self.deactivate()

        # Import and activate Grid mode
        try:
            from .grid_mode import GridMode
            grid = GridMode()
            grid.activate()
        except Exception as e:
            print(f"❌ Failed to activate Grid mode: {e}")

    def _click_element(self, element):
        """
        Click the selected element

        Args:
            element: Element dictionary
        """
        try:
            # Destroy overlay first
            self.overlay.destroy()

            # Click using pywinauto
            element['element'].click_input()
            print(f"✅ Clicked: {element['name']}")

        except Exception as e:
            print(f"❌ Click failed: {e}")
            # Try alternative click method
            try:
                rect = element['rect']
                x = rect.left + rect.width() // 2
                y = rect.top + rect.height() // 2

                # Move mouse and click
                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                print(f"✅ Clicked at position ({x}, {y})")
            except Exception as e2:
                print(f"❌ Alternative click also failed: {e2}")