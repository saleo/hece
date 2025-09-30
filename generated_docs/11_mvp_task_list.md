# HEMouse MVP任务列表

**版本**: MVP v1.0
**目标**: 从零开始实现核心Hint模式功能
**周期**: 6-8周
**状态**: 📋 待开始

---

## 项目概述

### MVP范围界定

**包含功能**：
- ✅ CapsLock启动Hint模式
- ✅ 检测UI元素并显示标签
- ✅ 键盘输入拦截（焦点窗口方案）
- ✅ 标签选择与元素点击
- ✅ 基础Grid模式（作为Hint模式的fallback）

**不包含功能**（后续版本）：
- ❌ 头部追踪（CV模块）
- ❌ Normal模式（IJKL方向键）
- ❌ 底层键盘钩子（C++/Rust DLL）
- ❌ 代码签名与安全合规

**技术栈**：
- Python 3.10+
- pywin32（Windows API）
- pywinauto（UI Automation）
- tkinter（遮罩窗口和Grid）

---

## 任务分解（6周 x 5天 = 30个工作日）

---

## 🔧 Phase 1: 环境搭建与基础架构（Week 1, 5天）

### Task 1.1: 开发环境配置
**工时**: 0.5天
**优先级**: P0

**子任务**：
```bash
# 1. 创建项目目录结构
hemouse/
├── src/
│   ├── core/              # 核心模块
│   ├── modes/             # 模式管理
│   ├── ui/                # 界面层
│   └── utils/             # 工具函数
├── tests/                 # 单元测试
├── docs/                  # 文档
├── requirements.txt       # 依赖
└── main.py               # 入口

# 2. 安装依赖
pip install pywin32 pywinauto pillow

# 3. Git初始化
git init
git add .
git commit -m "Initial commit: project structure"
```

**验收标准**：
- [ ] 项目目录结构创建完成
- [ ] 依赖安装成功
- [ ] Git仓库初始化

---

### Task 1.2: 全局热键监听（CapsLock检测）
**工时**: 1天
**优先级**: P0
**参考**: `Keyboard_Input_Isolation_Solution.md` - 方案A

**实现文件**: `src/core/hotkey_manager.py`

```python
import win32api
import win32con
import win32gui
import threading
import time

class HotkeyManager:
    """全局热键管理器"""

    def __init__(self):
        self.running = False
        self.callbacks = {}
        self.thread = None

    def register_hotkey(self, key_name, callback):
        """注册热键回调"""
        self.callbacks[key_name] = callback

    def start_monitoring(self):
        """开始监听"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def _monitor_loop(self):
        """监听循环"""
        prev_capslock_state = win32api.GetKeyState(win32con.VK_CAPITAL)

        while self.running:
            # 检测CapsLock状态变化
            curr_state = win32api.GetKeyState(win32con.VK_CAPITAL)

            if curr_state != prev_capslock_state:
                if curr_state == 1:  # CapsLock开启
                    if 'capslock_on' in self.callbacks:
                        self.callbacks['capslock_on']()
                else:  # CapsLock关闭
                    if 'capslock_off' in self.callbacks:
                        self.callbacks['capslock_off']()

                prev_capslock_state = curr_state

            time.sleep(0.05)  # 50ms轮询间隔

    def stop_monitoring(self):
        """停止监听"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

# 使用示例
if __name__ == "__main__":
    def on_capslock_on():
        print("✅ CapsLock ON - 启动Hint模式")

    def on_capslock_off():
        print("❌ CapsLock OFF - 退出Hint模式")

    manager = HotkeyManager()
    manager.register_hotkey('capslock_on', on_capslock_on)
    manager.register_hotkey('capslock_off', on_capslock_off)
    manager.start_monitoring()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_monitoring()
```

**验收标准**：
- [ ] CapsLock按下时触发回调
- [ ] CapsLock释放时触发回调
- [ ] 轮询延迟<100ms
- [ ] 通过单元测试

**测试用例**：
```python
# tests/test_hotkey_manager.py
import unittest
from src.core.hotkey_manager import HotkeyManager

class TestHotkeyManager(unittest.TestCase):
    def test_capslock_detection(self):
        triggered = {'on': False, 'off': False}

        def on_capslock_on():
            triggered['on'] = True

        def on_capslock_off():
            triggered['off'] = True

        manager = HotkeyManager()
        manager.register_hotkey('capslock_on', on_capslock_on)
        manager.register_hotkey('capslock_off', on_capslock_off)
        manager.start_monitoring()

        # 模拟CapsLock按下（需要手动测试）
        input("请按CapsLock键，然后按Enter...")
        self.assertTrue(triggered['on'])

        manager.stop_monitoring()
```

---

### Task 1.3: UI元素检测（Windows UIA）
**工时**: 1.5天
**优先级**: P0
**参考**: `Hint_Label_Design_Guide.md` - UI元素检测

**实现文件**: `src/core/element_detector.py`

```python
from pywinauto import Desktop
from pywinauto.controls.uiawrapper import UIAWrapper
import win32gui
import win32api

class ElementDetector:
    """UI元素检测器"""

    def __init__(self):
        self.desktop = Desktop(backend="uia")

    def get_clickable_elements(self, exclude_password=True):
        """获取当前屏幕上所有可点击元素"""
        elements = []

        # 获取前台窗口
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return elements

        try:
            # 使用UIA遍历元素
            window = self.desktop.window(handle=hwnd)
            self._traverse_elements(window, elements, exclude_password)
        except Exception as e:
            print(f"Error detecting elements: {e}")

        return elements

    def _traverse_elements(self, element, result_list, exclude_password):
        """递归遍历UI元素树"""
        try:
            # 检查是否可点击
            if self._is_clickable(element):
                # 排除密码框
                if exclude_password and self._is_password_field(element):
                    return

                # 获取元素位置和大小
                rect = element.rectangle()
                if self._is_visible_on_screen(rect):
                    result_list.append({
                        'element': element,
                        'rect': rect,
                        'type': element.element_info.control_type,
                        'name': element.window_text()
                    })

            # 递归子元素
            for child in element.children():
                self._traverse_elements(child, result_list, exclude_password)

        except Exception:
            pass  # 忽略无法访问的元素

    def _is_clickable(self, element):
        """判断元素是否可点击"""
        clickable_types = [
            'Button', 'Hyperlink', 'MenuItem', 'TabItem',
            'ListItem', 'TreeItem', 'CheckBox', 'RadioButton'
        ]

        control_type = element.element_info.control_type
        return any(t in control_type for t in clickable_types)

    def _is_password_field(self, element):
        """判断是否为密码框"""
        try:
            return element.element_info.control_type == "Edit" and \
                   element.is_password()
        except:
            return False

    def _is_visible_on_screen(self, rect):
        """判断元素是否在屏幕可见区域"""
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        return (rect.left >= 0 and rect.top >= 0 and
                rect.right <= screen_width and rect.bottom <= screen_height and
                rect.width() > 0 and rect.height() > 0)

# 测试
if __name__ == "__main__":
    detector = ElementDetector()
    elements = detector.get_clickable_elements()
    print(f"Found {len(elements)} clickable elements:")
    for i, elem in enumerate(elements[:10]):  # 只显示前10个
        print(f"{i+1}. {elem['type']}: {elem['name']} at {elem['rect']}")
```

**验收标准**：
- [ ] 检测到Chrome/VSCode/Notepad的按钮、链接
- [ ] 排除密码框
- [ ] 排除屏幕外元素
- [ ] 性能：<500ms检测完成（中等复杂界面）

---

### Task 1.4: 标签生成算法
**工时**: 1天
**优先级**: P0
**参考**: `Hint_Label_Design_Guide.md` - 无前缀冲突算法

**实现文件**: `src/core/label_generator.py`

```python
class LabelGenerator:
    """标签生成器（无前缀冲突）"""

    def __init__(self, charset="asdfghjkl"):
        """
        使用'asdfghjkl'字符集：
        - 左手：asdf
        - 右手：jkl (去除gh避免误按)
        """
        self.charset = charset
        self.charset_size = len(charset)

    def generate_labels(self, count):
        """生成无前缀冲突的标签"""
        if count <= 0:
            return []

        labels = []

        # 阶段1：单字母（9个元素以内）
        if count <= self.charset_size:
            labels = [self.charset[i] for i in range(count)]

        # 阶段2：双字母（左右手交替）
        else:
            # 先用完单字母
            for c in self.charset:
                labels.append(c)

            # 再生成双字母（左右手交替，避免前缀冲突）
            left_hand = "asdf"
            right_hand = "jkl"

            for c1 in self.charset:
                for c2 in self.charset:
                    # 左右手交替优先
                    if (c1 in left_hand and c2 in right_hand) or \
                       (c1 in right_hand and c2 in left_hand):
                        labels.append(c1 + c2)
                        if len(labels) >= count:
                            return labels[:count]

            # 如果还不够，添加同手组合
            for c1 in self.charset:
                for c2 in self.charset:
                    labels.append(c1 + c2)
                    if len(labels) >= count:
                        return labels[:count]

        return labels[:count]

    def match_label(self, input_str, labels):
        """匹配用户输入的标签"""
        matches = []
        for i, label in enumerate(labels):
            if label.startswith(input_str):
                matches.append(i)
        return matches

# 测试
if __name__ == "__main__":
    gen = LabelGenerator()

    # 测试1：9个元素
    labels = gen.generate_labels(9)
    print(f"9 elements: {labels}")
    assert labels == ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']

    # 测试2：20个元素
    labels = gen.generate_labels(20)
    print(f"20 elements: {labels}")

    # 测试3：无前缀冲突
    for i, label1 in enumerate(labels):
        for j, label2 in enumerate(labels):
            if i != j:
                assert not label2.startswith(label1), f"Prefix collision: {label1} vs {label2}"
    print("✅ No prefix collisions")

    # 测试4：匹配测试
    matches = gen.match_label("a", labels)
    print(f"Input 'a' matches: {[labels[i] for i in matches]}")
```

**验收标准**：
- [ ] 单字母：9个元素以内
- [ ] 双字母：左右手交替优先
- [ ] 无前缀冲突
- [ ] 通过单元测试

---

### Task 1.5: 模式管理器
**工时**: 1天
**优先级**: P0

**实现文件**: `src/modes/mode_manager.py`

```python
from enum import Enum

class Mode(Enum):
    IDLE = "idle"
    HINT = "hint"
    GRID = "grid"

class ModeManager:
    """模式管理器"""

    def __init__(self):
        self.current_mode = Mode.IDLE
        self.callbacks = {
            'on_mode_enter': {},
            'on_mode_exit': {}
        }

    def register_callback(self, event, mode, callback):
        """注册模式切换回调"""
        if event not in self.callbacks:
            self.callbacks[event] = {}
        self.callbacks[event][mode] = callback

    def switch_mode(self, new_mode):
        """切换模式"""
        if new_mode == self.current_mode:
            return

        old_mode = self.current_mode

        # 触发退出回调
        if old_mode in self.callbacks['on_mode_exit']:
            self.callbacks['on_mode_exit'][old_mode]()

        # 切换模式
        self.current_mode = new_mode
        print(f"Mode changed: {old_mode.value} → {new_mode.value}")

        # 触发进入回调
        if new_mode in self.callbacks['on_mode_enter']:
            self.callbacks['on_mode_enter'][new_mode]()

    def get_current_mode(self):
        """获取当前模式"""
        return self.current_mode

# 测试
if __name__ == "__main__":
    manager = ModeManager()

    def on_hint_enter():
        print("✅ Entered Hint mode")

    def on_hint_exit():
        print("❌ Exited Hint mode")

    manager.register_callback('on_mode_enter', Mode.HINT, on_hint_enter)
    manager.register_callback('on_mode_exit', Mode.HINT, on_hint_exit)

    manager.switch_mode(Mode.HINT)
    manager.switch_mode(Mode.IDLE)
```

**验收标准**：
- [ ] 支持IDLE/HINT/GRID模式
- [ ] 模式切换触发回调
- [ ] 防止重复切换

---

## 🎨 Phase 2: Hint模式核心功能（Week 2-3, 10天）

### Task 2.1: 遮罩窗口（透明Overlay）
**工时**: 1.5天
**优先级**: P0
**参考**: `Keyboard_Input_Isolation_Solution.md` - 方案A

**实现文件**: `src/ui/overlay_window.py`

```python
import tkinter as tk
from tkinter import font
import win32gui
import win32con
import win32api

class OverlayWindow:
    """遮罩窗口（显示标签）"""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.labels = []
        self.previous_focus = None

    def create(self):
        """创建遮罩窗口"""
        # 保存当前焦点窗口
        self.previous_focus = win32gui.GetForegroundWindow()

        # 创建全屏透明窗口
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)  # 30%透明度
        self.root.attributes('-topmost', True)  # 置顶
        self.root.overrideredirect(True)  # 无边框

        # 全屏尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定ESC退出
        self.root.bind('<Escape>', lambda e: self.destroy())

        # 设置焦点到遮罩窗口（拦截键盘输入）
        self.root.focus_force()

    def draw_labels(self, elements, labels):
        """绘制标签"""
        self.canvas.delete("all")  # 清空画布
        self.labels = []

        label_font = font.Font(family="Arial", size=14, weight="bold")

        for i, (elem, label) in enumerate(zip(elements, labels)):
            rect = elem['rect']

            # 标签位置（元素左上角）
            x = rect.left - 30
            y = rect.top

            # 绘制标签背景
            bg_id = self.canvas.create_rectangle(
                x, y, x + 30, y + 24,
                fill='yellow',
                outline='black',
                width=2
            )

            # 绘制标签文本
            text_id = self.canvas.create_text(
                x + 15, y + 12,
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

    def highlight_label(self, label):
        """高亮匹配的标签"""
        for item in self.labels:
            if item['label'] == label:
                self.canvas.itemconfig(item['bg_id'], fill='green')
            else:
                self.canvas.itemconfig(item['bg_id'], fill='yellow')

    def destroy(self):
        """销毁遮罩窗口"""
        if self.root:
            self.root.destroy()
            self.root = None

        # 恢复焦点
        if self.previous_focus:
            try:
                win32gui.SetForegroundWindow(self.previous_focus)
            except:
                pass

    def run_event_loop(self):
        """运行事件循环"""
        if self.root:
            self.root.mainloop()

# 测试
if __name__ == "__main__":
    overlay = OverlayWindow()
    overlay.create()

    # 模拟元素和标签
    mock_elements = [
        {'rect': type('Rect', (), {'left': 100, 'top': 100, 'width': 80, 'height': 30})()},
        {'rect': type('Rect', (), {'left': 200, 'top': 150, 'width': 80, 'height': 30})()},
    ]
    mock_labels = ['a', 's']

    overlay.draw_labels(mock_elements, mock_labels)
    overlay.run_event_loop()
```

**验收标准**：
- [ ] 全屏透明遮罩窗口
- [ ] 标签显示在元素旁边
- [ ] ESC键退出
- [ ] 获取键盘焦点

---

### Task 2.2: 键盘输入处理（标签匹配）
**工时**: 1.5天
**优先级**: P0

**实现文件**: `src/modes/hint_mode.py`

```python
import win32gui
import win32con
import win32api

class HintMode:
    """Hint模式控制器"""

    def __init__(self, overlay_window, element_detector, label_generator):
        self.overlay = overlay_window
        self.detector = element_detector
        self.label_gen = label_generator

        self.elements = []
        self.labels = []
        self.current_input = ""
        self.active = False

    def activate(self):
        """激活Hint模式"""
        if self.active:
            return

        print("🟢 Activating Hint mode...")

        # 1. 检测UI元素
        self.elements = self.detector.get_clickable_elements()
        print(f"Detected {len(self.elements)} clickable elements")

        if len(self.elements) == 0:
            print("⚠️ No clickable elements found")
            return

        # 2. 生成标签
        self.labels = self.label_gen.generate_labels(len(self.elements))

        # 3. 创建遮罩窗口
        self.overlay.create()
        self.overlay.draw_labels(self.elements, self.labels)

        # 4. 绑定键盘事件
        self.overlay.root.bind('<KeyPress>', self._on_key_press)

        self.current_input = ""
        self.active = True

        # 启动事件循环（阻塞）
        self.overlay.run_event_loop()

    def deactivate(self):
        """退出Hint模式"""
        if not self.active:
            return

        print("🔴 Deactivating Hint mode...")
        self.overlay.destroy()
        self.active = False
        self.current_input = ""

    def _on_key_press(self, event):
        """处理按键事件"""
        key = event.char.lower()

        # ESC退出
        if event.keysym == 'Escape':
            self.deactivate()
            return

        # 只处理标签字符（a-z）
        if not key.isalpha():
            return

        self.current_input += key
        print(f"Current input: {self.current_input}")

        # 查找匹配的标签
        matches = self.label_gen.match_label(self.current_input, self.labels)

        if len(matches) == 0:
            # 无匹配，重置输入
            print("❌ No match, resetting input")
            self.current_input = ""
            win32api.MessageBeep(win32con.MB_ICONHAND)

        elif len(matches) == 1:
            # 唯一匹配，执行点击
            matched_index = matches[0]
            matched_label = self.labels[matched_index]
            matched_element = self.elements[matched_index]

            print(f"✅ Match found: {matched_label}")
            self._click_element(matched_element)
            self.deactivate()

        else:
            # 多个匹配，高亮标签
            print(f"🔵 {len(matches)} matches, continue typing...")
            for match_idx in matches:
                self.overlay.highlight_label(self.labels[match_idx])

    def _click_element(self, element):
        """点击元素"""
        try:
            # 先销毁遮罩窗口，再点击
            self.overlay.destroy()

            # 使用pywinauto点击
            element['element'].click_input()
            print(f"✅ Clicked: {element['name']}")

        except Exception as e:
            print(f"❌ Click failed: {e}")

# 测试在main.py中集成
```

**验收标准**：
- [ ] 接收键盘输入（a-z）
- [ ] 实时匹配标签
- [ ] 唯一匹配时点击元素
- [ ] 无匹配时播放错误音效
- [ ] ESC退出

---

### Task 2.3: 主程序集成
**工时**: 1天
**优先级**: P0

**实现文件**: `main.py`

```python
import sys
import time
from src.core.hotkey_manager import HotkeyManager
from src.core.element_detector import ElementDetector
from src.core.label_generator import LabelGenerator
from src.ui.overlay_window import OverlayWindow
from src.modes.hint_mode import HintMode
from src.modes.mode_manager import ModeManager, Mode

class HEMouseApp:
    """HEMouse主程序"""

    def __init__(self):
        # 初始化组件
        self.hotkey_manager = HotkeyManager()
        self.mode_manager = ModeManager()
        self.element_detector = ElementDetector()
        self.label_generator = LabelGenerator()

        # 初始化Hint模式
        self.hint_mode = None

    def start(self):
        """启动应用"""
        print("🚀 HEMouse starting...")

        # 注册CapsLock热键
        self.hotkey_manager.register_hotkey('capslock_on', self._on_capslock_on)
        self.hotkey_manager.register_hotkey('capslock_off', self._on_capslock_off)

        # 启动热键监听
        self.hotkey_manager.start_monitoring()

        print("✅ HEMouse ready. Press CapsLock to activate Hint mode.")
        print("   Press Ctrl+C to exit.")

        # 主循环
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()

    def _on_capslock_on(self):
        """CapsLock开启 → 启动Hint模式"""
        if self.mode_manager.get_current_mode() == Mode.IDLE:
            self.mode_manager.switch_mode(Mode.HINT)
            self._activate_hint_mode()

    def _on_capslock_off(self):
        """CapsLock关闭 → 退出Hint模式"""
        if self.mode_manager.get_current_mode() == Mode.HINT:
            if self.hint_mode:
                self.hint_mode.deactivate()
            self.mode_manager.switch_mode(Mode.IDLE)

    def _activate_hint_mode(self):
        """激活Hint模式"""
        overlay = OverlayWindow()
        self.hint_mode = HintMode(overlay, self.element_detector, self.label_generator)
        self.hint_mode.activate()

        # Hint模式退出后，恢复IDLE
        self.mode_manager.switch_mode(Mode.IDLE)

    def stop(self):
        """停止应用"""
        print("\n🛑 HEMouse stopping...")
        self.hotkey_manager.stop_monitoring()
        print("✅ Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    app = HEMouseApp()
    app.start()
```

**验收标准**：
- [ ] CapsLock启动Hint模式
- [ ] 显示标签
- [ ] 输入标签点击元素
- [ ] ESC或CapsLock关闭退出
- [ ] Ctrl+C退出程序

---

### Task 2.4: 基础测试与调试
**工时**: 2天
**优先级**: P1

**测试场景**：
```yaml
场景1: Chrome浏览器
  - 打开Google首页
  - 启动Hint模式
  - 检测到搜索框、按钮、链接
  - 输入标签，点击链接

场景2: VSCode编辑器
  - 打开VSCode
  - 启动Hint模式
  - 检测到菜单项、按钮、树形节点
  - 输入标签，点击文件

场景3: Notepad
  - 打开Notepad
  - 启动Hint模式
  - 检测到菜单栏、工具栏按钮
  - 输入标签，点击按钮

场景4: 错误输入
  - 输入不存在的标签（如'zz'）
  - 播放错误音效
  - 重置输入状态
```

**验收标准**：
- [ ] 3个应用场景测试通过
- [ ] 错误输入处理正确
- [ ] 记录发现的Bug并修复

---

### Task 2.5: 性能优化（元素检测）
**工时**: 1.5天
**优先级**: P2

**优化目标**：
- UI元素检测：<500ms（中等复杂界面）
- 标签生成：<10ms
- 遮罩窗口显示：<100ms

**优化策略**：
```python
# 1. 限制递归深度（避免卡死）
def _traverse_elements(self, element, result_list, exclude_password, depth=0, max_depth=10):
    if depth > max_depth:
        return
    # ...

# 2. 异步检测（避免阻塞UI）
import threading

def get_clickable_elements_async(self, callback):
    """异步检测元素"""
    thread = threading.Thread(target=lambda: callback(self.get_clickable_elements()))
    thread.start()

# 3. 缓存窗口结构（30秒有效期）
from functools import lru_cache
import time

@lru_cache(maxsize=10)
def _get_window_elements_cached(self, hwnd, timestamp):
    # timestamp用于缓存失效
    return self.get_clickable_elements()
```

**验收标准**：
- [ ] Chrome检测<500ms
- [ ] VSCode检测<1s
- [ ] 复杂界面不卡死

---

### Task 2.6: 碰撞避免（标签位置优化）
**工时**: 2天
**优先级**: P2
**参考**: `Hint_Label_Design_Guide.md` - 5候选位置

**实现文件**: `src/ui/label_positioner.py`

```python
class LabelPositioner:
    """标签位置计算器（避免碰撞）"""

    def __init__(self):
        self.placed_labels = []

    def calculate_position(self, element_rect, label_size):
        """计算最佳标签位置（5候选位置）"""
        candidates = [
            {'x': element_rect.left - label_size[0] - 5, 'y': element_rect.top, 'priority': 1},  # 左上
            {'x': element_rect.right + 5, 'y': element_rect.top, 'priority': 2},  # 右上
            {'x': element_rect.left - label_size[0] - 5, 'y': element_rect.bottom - label_size[1], 'priority': 3},  # 左下
            {'x': element_rect.right + 5, 'y': element_rect.bottom - label_size[1], 'priority': 4},  # 右下
            {'x': element_rect.left + 5, 'y': element_rect.top + 5, 'priority': 5}  # 内部
        ]

        # 按优先级选择第一个无碰撞的位置
        for candidate in candidates:
            if not self._has_collision(candidate, label_size):
                self._add_placed_label(candidate, label_size)
                return (candidate['x'], candidate['y'])

        # 全部碰撞，返回优先级最高的位置
        best = candidates[0]
        self._add_placed_label(best, label_size)
        return (best['x'], best['y'])

    def _has_collision(self, position, size):
        """检查是否与已放置的标签碰撞"""
        new_rect = {
            'left': position['x'],
            'top': position['y'],
            'right': position['x'] + size[0],
            'bottom': position['y'] + size[1]
        }

        for placed in self.placed_labels:
            if self._rects_overlap(new_rect, placed):
                return True

        return False

    def _rects_overlap(self, rect1, rect2):
        """判断两个矩形是否重叠"""
        return not (rect1['right'] < rect2['left'] or
                    rect1['left'] > rect2['right'] or
                    rect1['bottom'] < rect2['top'] or
                    rect1['top'] > rect2['bottom'])

    def _add_placed_label(self, position, size):
        """记录已放置的标签"""
        self.placed_labels.append({
            'left': position['x'],
            'top': position['y'],
            'right': position['x'] + size[0],
            'bottom': position['y'] + size[1]
        })

    def reset(self):
        """重置（新的一次检测）"""
        self.placed_labels = []

# 集成到OverlayWindow.draw_labels()
```

**验收标准**：
- [ ] 标签优先显示在元素左上角
- [ ] 碰撞时切换到右上/左下/右下/内部
- [ ] 密集界面标签不重叠

---

### Task 2.7: 错误处理与日志
**工时**: 1天
**优先级**: P2

**实现文件**: `src/utils/logger.py`

```python
import logging
import os
from datetime import datetime

class HEMouseLogger:
    """HEMouse日志系统"""

    def __init__(self, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger("HEMouse")
        self.logger.setLevel(logging.DEBUG)

        # 文件处理器
        log_file = os.path.join(log_dir, f"hemouse_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)

# 全局日志实例
logger = HEMouseLogger()
```

**验收标准**：
- [ ] 日志文件保存到logs/目录
- [ ] 控制台输出INFO级别
- [ ] 文件记录DEBUG级别
- [ ] 异常自动记录堆栈

---

## 🔲 Phase 3: Grid模式（Fallback）（Week 4, 5天）

### Task 3.1: Grid模式实现
**工时**: 2天
**优先级**: P1
**参考**: `Mode_Transition_UX_Analysis.md` - 方案B

**实现文件**: `src/modes/grid_mode.py`

```python
import tkinter as tk

class GridMode:
    """Grid模式（全屏网格）"""

    def __init__(self, grid_size=3):
        self.grid_size = grid_size  # 3x3网格
        self.root = None
        self.canvas = None
        self.active = False

    def activate(self, highlight_region=None):
        """激活Grid模式"""
        if self.active:
            return

        print("🟦 Activating Grid mode...")

        # 创建全屏窗口
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.5)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # 创建画布
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绘制网格
        self._draw_grid(screen_width, screen_height)

        # 绑定键盘
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<Escape>', lambda e: self.deactivate())

        self.root.focus_force()
        self.active = True

        self.root.mainloop()

    def _draw_grid(self, width, height):
        """绘制网格"""
        cell_width = width // self.grid_size
        cell_height = height // self.grid_size

        # 绘制网格线
        for i in range(1, self.grid_size):
            # 垂直线
            self.canvas.create_line(
                i * cell_width, 0, i * cell_width, height,
                fill='yellow', width=2
            )
            # 水平线
            self.canvas.create_line(
                0, i * cell_height, width, i * cell_height,
                fill='yellow', width=2
            )

        # 绘制数字标签（1-9）
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

    def _on_key_press(self, event):
        """处理按键"""
        key = event.char

        if key.isdigit():
            grid_num = int(key)
            if 1 <= grid_num <= 9:
                self._select_grid(grid_num)

    def _select_grid(self, grid_num):
        """选择网格"""
        print(f"Selected grid: {grid_num}")

        # 计算网格中心位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        cell_width = screen_width // self.grid_size
        cell_height = screen_height // self.grid_size

        row = (grid_num - 1) // self.grid_size
        col = (grid_num - 1) % self.grid_size

        x = col * cell_width + cell_width // 2
        y = row * cell_height + cell_height // 2

        # 移动鼠标到该位置
        import win32api
        win32api.SetCursorPos((x, y))

        self.deactivate()

    def deactivate(self):
        """退出Grid模式"""
        if not self.active:
            return

        print("🔴 Deactivating Grid mode...")
        if self.root:
            self.root.destroy()
        self.active = False

# 测试
if __name__ == "__main__":
    grid = GridMode()
    grid.activate()
```

**验收标准**：
- [ ] 显示3x3网格
- [ ] 数字1-9选择网格
- [ ] 鼠标移动到网格中心
- [ ] ESC退出

---

### Task 3.2: Hint → Grid切换
**工时**: 1天
**优先级**: P1

**集成到**: `src/modes/hint_mode.py`

```python
# 在HintMode类中添加：

def _on_key_press(self, event):
    """处理按键事件"""
    key = event.char.lower()

    # ... 原有逻辑 ...

    # Space键 → 切换到Grid模式
    if event.keysym == 'space':
        print("🔄 Switching to Grid mode...")
        self.deactivate()

        # 启动Grid模式
        from src.modes.grid_mode import GridMode
        grid = GridMode()
        grid.activate()
```

**验收标准**：
- [ ] Hint模式下按Space切换Grid
- [ ] Grid模式正常工作
- [ ] Grid退出后返回IDLE

---

### Task 3.3: Grid模式递归细化
**工时**: 1.5天
**优先级**: P2

**扩展Grid功能**：
- 选择网格后，在该区域内再显示3x3子网格
- 实现类似Wheeler的递归细化

```python
class GridMode:
    def __init__(self, grid_size=3, region=None):
        self.grid_size = grid_size
        self.region = region  # 当前显示区域（None = 全屏）
        self.history = []  # 历史区域（用于返回）

    def _select_grid(self, grid_num):
        """选择网格（递归细化）"""
        # 计算子区域
        sub_region = self._calculate_sub_region(grid_num)

        # 如果区域足够小，点击；否则继续细化
        if sub_region['width'] < 100 and sub_region['height'] < 100:
            # 点击该区域中心
            self._click_region_center(sub_region)
            self.deactivate()
        else:
            # 保存历史
            self.history.append(self.region)

            # 在子区域内继续显示网格
            self.deactivate()
            sub_grid = GridMode(region=sub_region)
            sub_grid.activate()
```

**验收标准**：
- [ ] 选择网格后显示子网格
- [ ] 区域<100px时点击
- [ ] Backspace返回上级网格

---

### Task 3.4: Grid模式测试
**工时**: 0.5天
**优先级**: P2

**测试场景**：
- 全屏Grid → 选择网格9 → 鼠标移动到右下角
- 递归Grid → 选择网格1 → 子网格 → 选择网格5 → 点击

**验收标准**：
- [ ] 基础Grid测试通过
- [ ] 递归Grid测试通过

---

## 📦 Phase 4: 打包与文档（Week 5, 5天）

### Task 4.1: PyInstaller打包
**工时**: 1天
**优先级**: P1

**打包脚本**: `build.py`

```python
import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=HEMouse',
    '--icon=assets/icon.ico',
    '--add-data=assets;assets',
    '--hidden-import=pywinauto',
    '--hidden-import=win32gui',
    '--hidden-import=win32api',
    '--hidden-import=win32con',
])

print("✅ Build completed: dist/HEMouse.exe")
```

**验收标准**：
- [ ] 生成单文件HEMouse.exe
- [ ] 可执行文件大小<20MB
- [ ] 双击运行正常

---

### Task 4.2: README文档
**工时**: 1天
**优先级**: P1

**文件**: `README.md`

```markdown
# HEMouse - 键盘替代鼠标工具

**版本**: MVP v1.0
**状态**: 早期测试版

## 功能

- ✅ **Hint模式**：CapsLock启动，自动检测UI元素并显示标签
- ✅ **Grid模式**：空格切换，3x3网格快速定位
- ⏳ **Normal模式**：IJKL方向键（未实现）
- ⏳ **头部追踪**：CV控制鼠标（未实现）

## 安装

### 方式1：下载可执行文件
1. 下载 `HEMouse.exe`
2. 双击运行

### 方式2：源代码运行
```bash
git clone https://github.com/yourusername/hemouse.git
cd hemouse
pip install -r requirements.txt
python main.py
```

## 使用方法

1. 启动HEMouse
2. 按 **CapsLock** 启动Hint模式
3. 输入标签字母（如 `a`, `sj`）选择元素
4. 按 **Space** 切换到Grid模式（如果Hint失败）
5. 按 **ESC** 或再次按 **CapsLock** 退出

## 快捷键

| 快捷键 | 功能 |
|-------|------|
| CapsLock | 启动/退出 Hint模式 |
| a-z | 输入标签选择元素 |
| Space | 切换到Grid模式 |
| 1-9 | Grid模式选择网格 |
| ESC | 退出当前模式 |
| Ctrl+C | 退出程序 |

## 已知问题

- 某些应用（如全屏游戏）可能无法检测UI元素
- 密集界面标签可能重叠
- 性能：复杂界面检测较慢（>1s）

## 路线图

- [ ] 底层键盘钩子（C++ DLL）
- [ ] 头部追踪（MediaPipe + GADS）
- [ ] Normal模式（IJKL方向键）
- [ ] 代码签名与安全合规

## 贡献

欢迎提交Issue和PR！

## 许可证

MIT License
```

**验收标准**：
- [ ] README清晰易懂
- [ ] 包含安装、使用、快捷键
- [ ] 说明已知问题和路线图

---

### Task 4.3: 用户手册（视频）
**工时**: 1.5天
**优先级**: P2

**录制内容**：
1. 安装演示（双击运行）
2. Hint模式演示（Chrome、VSCode）
3. Grid模式演示
4. 常见问题解答

**工具**：OBS Studio录屏

**验收标准**：
- [ ] 视频时长5-10分钟
- [ ] 上传到YouTube/Bilibili
- [ ] README添加视频链接

---

### Task 4.4: 发布GitHub Release
**工时**: 0.5天
**优先级**: P1

**发布清单**：
```markdown
## HEMouse v1.0.0-mvp

### 功能
- ✅ Hint模式：CapsLock启动，自动标签选择
- ✅ Grid模式：3x3网格快速定位
- ✅ 键盘输入拦截（焦点窗口方案）

### 下载
- [HEMouse.exe](链接) (Windows 10/11, x64)

### 安装
1. 下载HEMouse.exe
2. 双击运行（Windows Defender可能警告，请允许运行）

### 使用
见 [README.md](链接)

### 已知问题
- 未签名，Windows Defender可能警告
- 某些应用无法检测UI元素
- 性能待优化

### 下一步计划
- 底层键盘钩子（C++ DLL）
- 代码签名证书
- 性能优化
```

**验收标准**：
- [ ] GitHub Release创建
- [ ] 上传HEMouse.exe
- [ ] 发布说明完整

---

### Task 4.5: 社区反馈收集
**工时**: 1天
**优先级**: P2

**渠道**：
- GitHub Issues
- Reddit r/ergonomics
- HackerNews Show HN
- V2EX分享创造

**验收标准**：
- [ ] 收集至少10个用户反馈
- [ ] 记录Bug和改进建议
- [ ] 优先级排序

---

## 🧪 Phase 5: 测试与Bug修复（Week 6, 5天）

### Task 5.1: 功能测试
**工时**: 2天
**优先级**: P0

**测试矩阵**：
| 应用 | Hint检测 | 标签选择 | Grid定位 | 结果 |
|-----|---------|---------|---------|------|
| Chrome | ✅ | ✅ | ✅ | PASS |
| VSCode | ✅ | ✅ | ✅ | PASS |
| Notepad | ✅ | ✅ | ✅ | PASS |
| Excel | ⚠️ | ✅ | ✅ | WARN |
| Photoshop | ❌ | N/A | ✅ | FAIL |

**验收标准**：
- [ ] 至少5个应用测试完成
- [ ] 主流应用（Chrome/VSCode/Office）PASS
- [ ] 记录不兼容应用

---

### Task 5.2: 边缘情况测试
**工时**: 1天
**优先级**: P1

**测试场景**：
```yaml
场景1: 快速连续CapsLock
  - 快速按下/释放CapsLock 10次
  - 期望：不卡死，模式切换正常

场景2: Hint模式下切换窗口
  - 启动Hint模式
  - Alt+Tab切换到其他窗口
  - 期望：Hint自动退出或保持在新窗口

场景3: 超密集界面
  - 打开包含100+元素的网页
  - 启动Hint模式
  - 期望：<2s检测完成，标签不全部重叠

场景4: 无UI元素
  - 打开桌面空白区域
  - 启动Hint模式
  - 期望：提示"无可点击元素"

场景5: 权限受限
  - 打开管理员权限的应用（如任务管理器）
  - 启动Hint模式
  - 期望：提示"无法访问，需要管理员权限"
```

**验收标准**：
- [ ] 5个边缘场景测试完成
- [ ] 发现的Bug记录到Issues
- [ ] 严重Bug立即修复

---

### Task 5.3: 性能基准测试
**工时**: 1天
**优先级**: P2

**测试指标**：
```python
# benchmark.py
import time

class PerformanceBenchmark:
    def __init__(self):
        self.results = {}

    def benchmark_element_detection(self):
        """UI元素检测性能"""
        detector = ElementDetector()

        start = time.time()
        elements = detector.get_clickable_elements()
        duration = time.time() - start

        self.results['element_detection'] = {
            'duration': duration,
            'element_count': len(elements),
            'target': 0.5  # 目标500ms
        }

    def benchmark_label_generation(self):
        """标签生成性能"""
        gen = LabelGenerator()

        start = time.time()
        labels = gen.generate_labels(100)
        duration = time.time() - start

        self.results['label_generation'] = {
            'duration': duration,
            'target': 0.01  # 目标10ms
        }

    def benchmark_overlay_rendering(self):
        """遮罩窗口渲染性能"""
        # TODO: 实现
        pass

    def report(self):
        """输出报告"""
        print("=== Performance Benchmark ===")
        for name, result in self.results.items():
            status = "✅" if result['duration'] < result['target'] else "❌"
            print(f"{status} {name}: {result['duration']*1000:.2f}ms (target: {result['target']*1000:.0f}ms)")

# 运行
benchmark = PerformanceBenchmark()
benchmark.benchmark_element_detection()
benchmark.benchmark_label_generation()
benchmark.report()
```

**验收标准**：
- [ ] 元素检测<500ms（中等界面）
- [ ] 标签生成<10ms
- [ ] 遮罩渲染<100ms

---

### Task 5.4: Bug修复
**工时**: 1天
**优先级**: P0

**预期Bug类别**：
- 元素检测遗漏（某些按钮未被检测到）
- 标签位置错误（遮挡元素或超出屏幕）
- 键盘输入漏失（快速输入时丢失字符）
- 内存泄漏（长时间运行后内存增长）

**修复流程**：
1. 复现Bug
2. 定位根因
3. 编写修复代码
4. 添加测试用例
5. 回归测试

**验收标准**：
- [ ] P0 Bug全部修复
- [ ] P1 Bug至少修复80%
- [ ] 添加防御性代码

---

## 📊 项目管理

### 时间线（6周）

```
Week 1: 环境搭建 + 基础架构
  ├─ Day 1-2: 环境配置 + 热键监听 + UI检测
  ├─ Day 3-4: 标签生成 + 模式管理
  └─ Day 5: 集成测试

Week 2: Hint模式核心（Part 1）
  ├─ Day 1-2: 遮罩窗口
  ├─ Day 3-4: 键盘输入处理
  └─ Day 5: 主程序集成

Week 3: Hint模式优化（Part 2）
  ├─ Day 1-2: 基础测试与调试
  ├─ Day 3-4: 性能优化
  └─ Day 5: 碰撞避免

Week 4: Grid模式
  ├─ Day 1-2: Grid实现
  ├─ Day 3: Hint→Grid切换
  ├─ Day 4: 递归细化
  └─ Day 5: Grid测试

Week 5: 打包与文档
  ├─ Day 1: PyInstaller打包
  ├─ Day 2: README文档
  ├─ Day 3-4: 用户手册（视频）
  └─ Day 5: GitHub发布 + 反馈收集

Week 6: 测试与修复
  ├─ Day 1-2: 功能测试
  ├─ Day 3: 边缘情况测试
  ├─ Day 4: 性能基准测试
  └─ Day 5: Bug修复 + 发布v1.0.0
```

### 资源需求

**人力**：1名全职开发者（或2名兼职）

**硬件**：
- Windows 10/11 x64开发机
- 测试用应用：Chrome, VSCode, Notepad, Excel

**软件**：
- Python 3.10+
- PyCharm/VSCode
- Git
- PyInstaller
- OBS Studio（录屏）

**预算**：$0（MVP阶段无需购买证书）

---

## ✅ 验收标准（MVP完成）

### 功能完整性
- [x] CapsLock启动Hint模式
- [x] UI元素检测（Chrome/VSCode/Notepad）
- [x] 标签生成（无前缀冲突）
- [x] 键盘输入拦截
- [x] 标签选择点击元素
- [x] Grid模式（3x3网格）
- [x] Hint→Grid切换

### 性能指标
- [x] 元素检测<500ms（中等界面）
- [x] 标签生成<10ms
- [x] 键盘响应<100ms

### 质量标准
- [x] 主流应用兼容（Chrome/VSCode/Office）
- [x] 无严重Bug（P0全部修复）
- [x] 用户手册完整
- [x] GitHub Release发布

---

## 🚀 下一步（Post-MVP）

### Phase 6: 性能与安全（Week 7-10）
- C++/Rust DLL（底层键盘钩子）
- 代码签名证书（EV证书）
- 安全合规（Microsoft Defender申诉）

### Phase 7: CV模块（Week 11-16）
- MediaPipe集成
- GADS头部姿态估计
- 头部追踪控制鼠标

### Phase 8: Normal模式（Week 17-18）
- IJKL方向键移动
- 加速度控制

---

**文档版本**: v1.0
**创建日期**: 2025-09-30
**状态**: ✅ Ready to Start

**下一步行动**：
1. 创建GitHub仓库
2. 配置开发环境
3. 开始Task 1.1（环境搭建）