"""
HEMouse Overlay Window
Transparent overlay window for displaying labels
"""
import tkinter as tk
from tkinter import font as tkfont
import win32gui
import win32con
import win32api


class OverlayWindow:
    """Transparent overlay window for Hint mode labels"""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.labels = []
        self.previous_focus = None
        self.label_size = (35, 26)  # Width x Height of label box

    def create(self):
        """Create fullscreen transparent overlay window"""
        # Save current focus window
        self.previous_focus = win32gui.GetForegroundWindow()

        # Create transparent fullscreen window
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)  # 30% transparency
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window borders

        # Fullscreen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind ESC key to exit
        self.root.bind('<Escape>', lambda e: self.destroy())

        # Force focus to capture keyboard input
        self.root.focus_force()

        print("✅ Overlay window created")

    def draw_labels(self, elements, labels):
        """
        Draw labels on overlay

        Args:
            elements: List of element dictionaries
            labels: List of label strings
        """
        if not self.canvas:
            return

        self.canvas.delete("all")  # Clear canvas
        self.labels = []

        # Create font
        label_font = tkfont.Font(family="Arial", size=14, weight="bold")

        for i, (elem, label) in enumerate(zip(elements, labels)):
            rect = elem['rect']

            # Label position (to the left of element)
            x = rect.left - self.label_size[0] - 5
            y = rect.top

            # Ensure label is on screen
            if x < 0:
                x = rect.right + 5
            if y < 0:
                y = 0

            # Draw label background
            bg_id = self.canvas.create_rectangle(
                x, y, x + self.label_size[0], y + self.label_size[1],
                fill='yellow',
                outline='black',
                width=2
            )

            # Draw label text
            text_id = self.canvas.create_text(
                x + self.label_size[0] // 2,
                y + self.label_size[1] // 2,
                text=label.upper(),
                font=label_font,
                fill='black'
            )

            self.labels.append({
                'label': label,
                'element': elem,
                'bg_id': bg_id,
                'text_id': text_id
            })

        print(f"✅ Drew {len(self.labels)} labels")

    def highlight_matches(self, matching_labels):
        """
        Highlight matching labels

        Args:
            matching_labels: List of label strings to highlight
        """
        if not self.canvas:
            return

        for item in self.labels:
            if item['label'] in matching_labels:
                self.canvas.itemconfig(item['bg_id'], fill='green')
            else:
                self.canvas.itemconfig(item['bg_id'], fill='yellow')

    def destroy(self):
        """Destroy overlay window"""
        if self.root:
            try:
                self.root.destroy()
                self.root = None
                print("✅ Overlay window destroyed")
            except:
                pass

        # Restore focus
        if self.previous_focus:
            try:
                win32gui.SetForegroundWindow(self.previous_focus)
            except:
                pass

    def run_event_loop(self):
        """Run Tkinter event loop (blocking)"""
        if self.root:
            self.root.mainloop()


# Test code
if __name__ == "__main__":
    import time

    overlay = OverlayWindow()
    overlay.create()

    # Mock elements and labels
    class MockRect:
        def __init__(self, left, top, width, height):
            self.left = left
            self.top = top
            self.width = width
            self.height = height

    mock_elements = [
        {'rect': MockRect(100, 100, 80, 30), 'name': 'Button 1'},
        {'rect': MockRect(200, 150, 80, 30), 'name': 'Button 2'},
        {'rect': MockRect(300, 200, 80, 30), 'name': 'Button 3'},
    ]
    mock_labels = ['a', 's', 'd']

    overlay.draw_labels(mock_elements, mock_labels)

    # Test highlighting after 2 seconds
    def test_highlight():
        time.sleep(2)
        overlay.highlight_matches(['a', 'd'])

    import threading
    threading.Thread(target=test_highlight, daemon=True).start()

    overlay.run_event_loop()