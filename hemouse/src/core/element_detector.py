"""
HEMouse Element Detector
Detects clickable UI elements using Windows UI Automation
"""
from pywinauto import Desktop
import win32gui
import win32api
import win32con
import time


class ElementDetector:
    """UI element detector using Windows UIA"""

    def __init__(self):
        self.desktop = Desktop(backend="uia")

    def get_clickable_elements(self, exclude_password=True, max_depth=6):
        """
        Get all clickable elements on current screen

        Args:
            exclude_password: Skip password fields
            max_depth: Maximum recursion depth (default: 6 for performance)

        Returns:
            List of element dictionaries with 'element', 'rect', 'type', 'name'
        """
        elements = []

        # Get foreground window
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            print("⚠️ No foreground window found")
            return elements

        try:
            # Get window using UIA
            window = self.desktop.window(handle=hwnd)

            # Add timeout protection for slow windows
            import time
            start_time = time.time()
            self._traverse_elements(window, elements, exclude_password, depth=0, max_depth=max_depth, start_time=start_time, timeout=2.0)

            elapsed = time.time() - start_time
            print(f"✅ Detected {len(elements)} clickable elements in {elapsed:.2f}s")
        except Exception as e:
            print(f"❌ Error detecting elements: {e}")

        return elements

    def _traverse_elements(self, element, result_list, exclude_password, depth=0, max_depth=6, start_time=None, timeout=2.0):
        """
        Recursively traverse UI element tree with timeout protection

        Args:
            element: Current element
            result_list: List to append found elements
            exclude_password: Skip password fields
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            start_time: Start time for timeout check
            timeout: Maximum time in seconds (default: 2.0s)
        """
        # Check timeout to prevent hanging on slow windows
        if start_time and (time.time() - start_time) > timeout:
            return

        if depth > max_depth:
            return

        try:
            # Check if element is clickable
            if self._is_clickable(element):
                # Exclude password fields
                if exclude_password and self._is_password_field(element):
                    return

                # Get element rectangle
                rect = element.rectangle()
                if self._is_visible_on_screen(rect):
                    result_list.append({
                        'element': element,
                        'rect': rect,
                        'type': element.element_info.control_type,
                        'name': element.window_text()
                    })

            # Recursively process children
            for child in element.children():
                self._traverse_elements(child, result_list, exclude_password, depth + 1, max_depth, start_time, timeout)

        except Exception:
            pass  # Ignore inaccessible elements

    def _is_clickable(self, element):
        """Check if element is clickable with priority filtering"""
        # High priority: Interactive UI controls
        high_priority_types = [
            'Button', 'Hyperlink', 'MenuItem', 'TabItem',
            'CheckBox', 'RadioButton', 'ComboBox'
        ]

        # Medium priority: Input and selection
        medium_priority_types = [
            'Edit', 'ListItem', 'TreeItem'
        ]

        # Low priority (excluded): Too generic, causes noise
        # 'Document', 'Text', 'Pane', 'Group'

        try:
            control_type = element.element_info.control_type

            # Check high priority first
            if any(t in control_type for t in high_priority_types):
                return True

            # Medium priority: additional checks for real interactivity
            if any(t in control_type for t in medium_priority_types):
                # Only include if element has meaningful name or is enabled
                name = element.window_text()
                if name and len(name.strip()) > 0:
                    return True

            return False
        except:
            return False

    def _is_password_field(self, element):
        """Check if element is a password field"""
        try:
            return element.element_info.control_type == "Edit" and element.is_password()
        except:
            return False

    def _is_visible_on_screen(self, rect):
        """Check if element is visible on screen with size filtering"""
        # Get virtual screen bounds (all monitors)
        virtual_screen_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        virtual_screen_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        virtual_screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        virtual_screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        # Element must be within virtual screen bounds (with small margin)
        within_bounds = (
            rect.left >= virtual_screen_left - 100 and
            rect.top >= virtual_screen_top - 100 and
            rect.right <= virtual_screen_left + virtual_screen_width + 100 and
            rect.bottom <= virtual_screen_top + virtual_screen_height + 100
        )

        # Element must be reasonably sized (filter out tiny decorations)
        min_width = 20  # Minimum 20 pixels wide
        min_height = 15  # Minimum 15 pixels tall
        reasonable_size = rect.width() >= min_width and rect.height() >= min_height

        # Element should not be too large (likely container/pane, not clickable)
        max_width = virtual_screen_width * 0.8  # Max 80% of screen width
        max_height = virtual_screen_height * 0.8  # Max 80% of screen height
        not_too_large = rect.width() <= max_width and rect.height() <= max_height

        return within_bounds and reasonable_size and not_too_large


# Test code
if __name__ == "__main__":
    print("Testing ElementDetector...")
    print("Please make sure a window is in focus (Chrome, VSCode, etc.)")
    input("Press Enter to start detection...")

    detector = ElementDetector()
    elements = detector.get_clickable_elements()

    print(f"\n📊 Found {len(elements)} clickable elements:")
    for i, elem in enumerate(elements[:20]):  # Show first 20
        print(f"{i+1}. {elem['type']}: {elem['name'][:50]} at ({elem['rect'].left}, {elem['rect'].top})")