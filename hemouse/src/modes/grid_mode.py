"""
HEMouse Grid Mode
Grid-based mouse positioning mode (fallback when Hint mode fails)
"""
import tkinter as tk
import win32api
import win32con


class GridMode:
    """Grid mode for coarse mouse positioning"""

    def __init__(self, grid_size=3, region=None):
        """
        Initialize Grid mode

        Args:
            grid_size: Size of grid (default 3x3)
            region: Region to display grid (None = fullscreen)
                   Dict with 'left', 'top', 'width', 'height'
        """
        self.grid_size = grid_size
        self.region = region
        self.root = None
        self.canvas = None
        self.active = False
        self.history = []  # For recursive refinement

    def activate(self):
        """Activate Grid mode"""
        if self.active:
            return

        print("\n🟦 Activating Grid mode...")

        # Create fullscreen window
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.5)  # 50% transparency
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)

        # Determine region
        if self.region:
            x = self.region['left']
            y = self.region['top']
            width = self.region['width']
            height = self.region['height']
        else:
            x = 0
            y = 0
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Create canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw grid
        self._draw_grid(width, height)

        # Bind keyboard
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<Escape>', lambda e: self.deactivate())
        self.root.bind('<BackSpace>', lambda e: self._go_back())

        self.root.focus_force()
        self.active = True

        print("✅ Grid mode ready! Press 1-9 to select grid, ESC to exit")

        # Run event loop
        self.root.mainloop()
        self.active = False

    def _draw_grid(self, width, height):
        """Draw grid with numbered cells"""
        cell_width = width // self.grid_size
        cell_height = height // self.grid_size

        # Draw grid lines
        for i in range(1, self.grid_size):
            # Vertical lines
            self.canvas.create_line(
                i * cell_width, 0, i * cell_width, height,
                fill='yellow', width=2
            )
            # Horizontal lines
            self.canvas.create_line(
                0, i * cell_height, width, i * cell_height,
                fill='yellow', width=2
            )

        # Draw numbered labels (1-9)
        label_num = 1
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * cell_width + cell_width // 2
                y = row * cell_height + cell_height // 2

                self.canvas.create_text(
                    x, y,
                    text=str(label_num),
                    font=('Arial', 48, 'bold'),
                    fill='yellow'
                )
                label_num += 1

        print(f"✅ Drew {self.grid_size}x{self.grid_size} grid")

    def _on_key_press(self, event):
        """Handle keyboard input"""
        key = event.char

        if key.isdigit():
            grid_num = int(key)
            if 1 <= grid_num <= 9:
                self._select_grid(grid_num)

    def _select_grid(self, grid_num):
        """
        Select a grid cell

        Args:
            grid_num: Grid number (1-9)
        """
        print(f"🎯 Selected grid: {grid_num}")

        # Calculate grid region
        region = self._calculate_grid_region(grid_num)

        # If region is small enough, click center
        if region['width'] < 150 or region['height'] < 150:
            x = region['left'] + region['width'] // 2
            y = region['top'] + region['height'] // 2

            print(f"✅ Moving mouse to ({x}, {y})")
            win32api.SetCursorPos((x, y))

            self.deactivate()
        else:
            # Region is large - recurse with sub-grid
            print(f"🔍 Region too large - showing sub-grid")
            self.history.append(self.region)
            self.deactivate()

            # Create sub-grid
            sub_grid = GridMode(grid_size=self.grid_size, region=region)
            sub_grid.activate()

    def _calculate_grid_region(self, grid_num):
        """
        Calculate region for grid cell

        Args:
            grid_num: Grid number (1-9)

        Returns:
            Dict with 'left', 'top', 'width', 'height'
        """
        # Determine current region
        if self.region:
            left = self.region['left']
            top = self.region['top']
            width = self.region['width']
            height = self.region['height']
        else:
            left = 0
            top = 0
            width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        cell_width = width // self.grid_size
        cell_height = height // self.grid_size

        # Calculate row and column
        row = (grid_num - 1) // self.grid_size
        col = (grid_num - 1) % self.grid_size

        return {
            'left': left + col * cell_width,
            'top': top + row * cell_height,
            'width': cell_width,
            'height': cell_height
        }

    def _go_back(self):
        """Go back to previous grid level"""
        if len(self.history) > 0:
            print("⬅️ Going back to previous grid")
            prev_region = self.history.pop()
            self.deactivate()

            # Show previous grid
            prev_grid = GridMode(grid_size=self.grid_size, region=prev_region)
            prev_grid.history = self.history
            prev_grid.activate()
        else:
            print("⚠️ Already at top level")

    def deactivate(self):
        """Deactivate Grid mode"""
        if not self.active:
            return

        print("🔴 Deactivating Grid mode...")
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
        self.active = False


# Test code
if __name__ == "__main__":
    grid = GridMode()
    grid.activate()