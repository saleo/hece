"""
HEMouse Element Detector
Detects clickable UI elements using Windows UI Automation
"""
from pywinauto import Desktop
import win32gui
import win32api
import win32con


class ElementDetector:
    """UI element detector using Windows UIA"""

    def __init__(self):
        self.desktop = Desktop(backend="uia")

    def get_clickable_elements(self, exclude_password=True, max_depth=10):
        """
        Get all clickable elements on current screen

        Args:
            exclude_password: Skip password fields
            max_depth: Maximum recursion depth

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
            self._traverse_elements(window, elements, exclude_password, depth=0, max_depth=max_depth)
            print(f"✅ Detected {len(elements)} clickable elements")
        except Exception as e:
            print(f"❌ Error detecting elements: {e}")

        return elements

    def _traverse_elements(self, element, result_list, exclude_password, depth=0, max_depth=10):
        """
        Recursively traverse UI element tree

        Args:
            element: Current element
            result_list: List to append found elements
            exclude_password: Skip password fields
            depth: Current recursion depth
            max_depth: Maximum recursion depth
        """
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
                self._traverse_elements(child, result_list, exclude_password, depth + 1, max_depth)

        except Exception:
            pass  # Ignore inaccessible elements

    def _is_clickable(self, element):
        """Check if element is clickable"""
        clickable_types = [
            'Button', 'Hyperlink', 'MenuItem', 'TabItem',
            'ListItem', 'TreeItem', 'CheckBox', 'RadioButton',
            'ComboBox', 'Edit', 'Document', 'Text'
        ]

        try:
            control_type = element.element_info.control_type
            return any(t in control_type for t in clickable_types)
        except:
            return False

    def _is_password_field(self, element):
        """Check if element is a password field"""
        try:
            return element.element_info.control_type == "Edit" and element.is_password()
        except:
            return False

    def _is_visible_on_screen(self, rect):
        """Check if element is visible on screen"""
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        return (rect.left >= -100 and rect.top >= -100 and
                rect.right <= screen_width + 100 and rect.bottom <= screen_height + 100 and
                rect.width() > 5 and rect.height() > 5)


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