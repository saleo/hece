# 键盘输入隔离技术方案

## Q2: 如何避免遮罩层的键盘输入被传入到下层窗口应用程序？

---

## 1. 问题分析

### 1.1 核心问题
在Hint模式下，HEMouse需要：
- 在屏幕上显示透明/半透明遮罩层，绘制提示标签
- 接收用户的键盘输入（如"aj"、"sk"等标签快捷键）
- **防止这些键盘输入穿透到下层应用程序**（如浏览器、编辑器、游戏）

### 1.2 典型场景
```
用户操作流程：
1. CapsLock启动Hint模式 → 遮罩层显示，标签出现
2. 用户输入"a" → 期望：选中标签"a"的元素
3. 问题：字母"a"同时被传入到下层的Word文档中

风险：
- 文本编辑器收到字符输入 → 意外修改文档内容
- 游戏收到WASD → 触发游戏内移动
- 浏览器收到快捷键 → 触发浏览器功能（如Ctrl+W关闭标签页）
```

### 1.3 技术挑战
- Windows消息机制会自动将键盘输入路由到焦点窗口
- 透明遮罩层需要"拦截"键盘输入，但不影响鼠标穿透（点击下层窗口）
- 需要处理各种边缘情况（Alt+Tab、Win键、Ctrl+Alt+Del等系统组合键）

---

## 2. 技术调研

### 2.1 Windows键盘输入机制

```
键盘输入的传播路径：
硬件键盘 → 键盘驱动 → 系统消息队列 → 键盘钩子链 → 焦点窗口消息循环 → 应用程序
```

**关键拦截点**：
1. **全局键盘钩子（WH_KEYBOARD）**：用户模式，可被绕过
2. **底层键盘钩子（WH_KEYBOARD_LL）**：系统级，最早拦截点
3. **窗口消息处理（WM_KEYDOWN/WM_CHAR）**：焦点窗口级别

### 2.2 现有方案参考

| 工具 | 拦截方法 | 特点 |
|------|---------|------|
| **Vimium（浏览器扩展）** | Browser API拦截 | 仅限浏览器标签页内，使用`event.preventDefault()` |
| **PowerToys Keyboard Manager** | 底层钩子 + 驱动过滤 | 系统级拦截，需要管理员权限 |
| **AutoHotkey** | 底层键盘钩子（WH_KEYBOARD_LL） | 灵活但需要小心处理竞争条件 |
| **游戏覆盖层（如Steam、Discord）** | 焦点窗口 + 独占输入模式 | 切换焦点到覆盖层窗口 |

---

## 3. 解决方案对比

### 方案A：焦点窗口方案（简单但有副作用）

**原理**：
- Hint模式激活时，将键盘焦点切换到遮罩层窗口
- 遮罩层窗口的消息循环处理`WM_KEYDOWN`等消息
- 退出Hint模式时，恢复焦点到原窗口

**代码示例**：
```python
import win32gui
import win32con

class OverlayWindow:
    def __init__(self):
        self.previous_focus = None

    def activate_hint_mode(self):
        # 保存当前焦点窗口
        self.previous_focus = win32gui.GetForegroundWindow()

        # 创建遮罩窗口（TopMost + ToolWindow）
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW,
            "HEMouse_Overlay",
            "",
            win32con.WS_POPUP,
            0, 0, screen_width, screen_height,
            None, None, None, None
        )

        # 设置焦点到遮罩窗口
        win32gui.SetForegroundWindow(self.hwnd)

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_KEYDOWN:
            key = chr(wparam)
            # 处理标签输入
            self.handle_label_input(key)
            return 0  # 消费掉事件，不传播
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def deactivate_hint_mode(self):
        win32gui.DestroyWindow(self.hwnd)
        # 恢复焦点
        if self.previous_focus:
            win32gui.SetForegroundWindow(self.previous_focus)
```

**优点**：
- ✅ 实现简单，不需要全局钩子
- ✅ 兼容性好，标准Windows API
- ✅ 不需要管理员权限

**缺点**：
- ❌ 焦点切换会触发下层应用的失焦事件（某些应用可能暂停、隐藏UI）
- ❌ 无法处理全局快捷键（如媒体键、音量键）
- ❌ 某些应用可能拒绝失去焦点（如全屏游戏）

**适用场景**：MVP阶段，用于桌面办公环境

---

### 方案B：底层键盘钩子方案（可靠但复杂）

**原理**：
- 使用`SetWindowsHookEx(WH_KEYBOARD_LL, ...)`安装底层键盘钩子
- 在钩子回调中检查HEMouse是否处于Hint模式
- 如果是，消费掉键盘事件（返回1），阻止传播到下层应用

**代码示例**：
```python
import ctypes
from ctypes import wintypes

# 定义钩子回调函数类型
HOOKPROC = ctypes.WINFUNCTYPE(
    wintypes.LPARAM,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM
)

class KeyboardHookManager:
    def __init__(self):
        self.hook_id = None
        self.hint_mode_active = False
        self.callback = HOOKPROC(self._hook_callback)

    def install_hook(self):
        """安装底层键盘钩子"""
        WH_KEYBOARD_LL = 13
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        hmod = kernel32.GetModuleHandleW(None)

        self.hook_id = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self.callback,
            hmod,
            0  # 0 = 全局钩子
        )

        if not self.hook_id:
            raise ctypes.WinError(ctypes.get_last_error())

    def uninstall_hook(self):
        """移除钩子"""
        if self.hook_id:
            ctypes.windll.user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None

    def _hook_callback(self, nCode, wParam, lParam):
        """钩子回调函数"""
        if nCode >= 0 and self.hint_mode_active:
            # 解析键盘事件
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101

            if wParam in (WM_KEYDOWN, WM_KEYUP):
                # 读取键盘事件结构体
                class KBDLLHOOKSTRUCT(ctypes.Structure):
                    _fields_ = [
                        ("vkCode", wintypes.DWORD),
                        ("scanCode", wintypes.DWORD),
                        ("flags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
                    ]

                kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk_code = kb_struct.vkCode

                # 处理标签输入（a-z、0-9）
                if self._is_label_key(vk_code):
                    if wParam == WM_KEYDOWN:
                        self._handle_label_input(vk_code)
                    return 1  # 阻止事件传播

                # 处理Esc、Space等控制键
                if vk_code in (0x1B, 0x20):  # ESC, SPACE
                    if wParam == WM_KEYDOWN:
                        self._handle_control_key(vk_code)
                    return 1  # 阻止事件传播

        # 调用下一个钩子
        return ctypes.windll.user32.CallNextHookEx(
            self.hook_id, nCode, wParam, lParam
        )

    def _is_label_key(self, vk_code):
        """检查是否为标签键（a-z）"""
        # VK_A = 0x41, VK_Z = 0x5A
        return 0x41 <= vk_code <= 0x5A

    def _handle_label_input(self, vk_code):
        """处理标签输入"""
        char = chr(vk_code).lower()
        print(f"Label key pressed: {char}")
        # TODO: 调用HEMouse的标签选择逻辑

    def _handle_control_key(self, vk_code):
        """处理控制键"""
        if vk_code == 0x1B:  # ESC
            print("Exiting hint mode")
            self.hint_mode_active = False
        elif vk_code == 0x20:  # SPACE
            print("Rotate overlapping labels")
            # TODO: 实现标签旋转逻辑

# 使用示例
hook_manager = KeyboardHookManager()
hook_manager.install_hook()

# 激活Hint模式
hook_manager.hint_mode_active = True

# ... 运行消息循环 ...

# 退出时清理
hook_manager.uninstall_hook()
```

**优点**：
- ✅ 可靠拦截所有键盘输入，下层应用不会收到事件
- ✅ 不改变焦点，下层应用不会收到失焦事件
- ✅ 可以处理全局快捷键

**缺点**：
- ❌ 实现较复杂，需要小心处理钩子回调
- ❌ 可能被安全软件（如杀毒软件）警告/拦截
- ❌ 钩子回调必须快速返回（<300ms），否则系统会移除钩子

**适用场景**：生产版本，需要可靠的键盘拦截

---

### 方案C：混合方案（推荐）

**原理**：结合方案A和方案B的优点
- **主路径**：焦点窗口方案（处理90%的正常场景）
- **安全网**：底层键盘钩子（处理边缘情况）

**实现策略**：
1. Hint模式激活时：
   - 创建TopMost遮罩窗口，但**不立即切换焦点**
   - 安装底层键盘钩子，开始拦截键盘输入
   - 用户首次按键时，再切换焦点到遮罩窗口（延迟焦点切换）

2. 键盘输入处理：
   - 钩子拦截并转发到遮罩窗口的消息循环
   - 遮罩窗口处理标签选择逻辑
   - 钩子返回1阻止传播

3. Hint模式退出时：
   - 先移除键盘钩子
   - 销毁遮罩窗口，恢复焦点

**代码示例**：
```python
class HybridInputManager:
    def __init__(self):
        self.overlay_window = OverlayWindow()
        self.keyboard_hook = KeyboardHookManager()
        self.hint_mode_active = False

    def activate_hint_mode(self):
        """激活Hint模式"""
        # 1. 创建遮罩窗口（但不切换焦点）
        self.overlay_window.create(focus=False)

        # 2. 安装键盘钩子
        self.keyboard_hook.install_hook()
        self.keyboard_hook.hint_mode_active = True

        # 3. 设置钩子回调转发到遮罩窗口
        self.keyboard_hook.on_key_press = self.overlay_window.handle_key_press

        self.hint_mode_active = True

    def deactivate_hint_mode(self):
        """退出Hint模式"""
        self.hint_mode_active = False

        # 1. 先移除钩子
        self.keyboard_hook.uninstall_hook()

        # 2. 再销毁遮罩窗口
        self.overlay_window.destroy()

class OverlayWindow:
    def handle_key_press(self, vk_code, is_keydown):
        """处理从钩子转发来的按键事件"""
        if not is_keydown:
            return

        char = chr(vk_code).lower()

        # 标签选择逻辑
        if self.is_valid_label_char(char):
            self.current_input += char
            matched_elements = self.find_matching_labels(self.current_input)

            if len(matched_elements) == 1:
                # 唯一匹配，执行点击
                self.click_element(matched_elements[0])
                self.exit_hint_mode()
            elif len(matched_elements) == 0:
                # 无匹配，重置输入
                self.current_input = ""
                self.show_error_feedback()
```

**优点**：
- ✅ 兼顾可靠性和简洁性
- ✅ 钩子提供安全网，确保100%拦截
- ✅ 延迟焦点切换减少对下层应用的干扰

**缺点**：
- ⚠️ 实现复杂度中等

---

## 4. 推荐实现方案

### 4.1 分阶段实施

**Phase 1: MVP（方案A - 焦点窗口）**
- 快速验证核心功能
- 代码量少，易于调试
- 适用于桌面办公场景（Chrome、VSCode、Office等）

**Phase 2: Production（方案C - 混合方案）**
- 引入底层键盘钩子
- 处理边缘情况（游戏、全屏应用）
- 生产级可靠性

### 4.2 完整实现代码（Python + pywin32）

```python
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import threading

class HEMouseInputManager:
    """HEMouse键盘输入隔离管理器"""

    def __init__(self):
        self.hint_mode_active = False
        self.overlay_hwnd = None
        self.hook_id = None
        self.previous_focus = None
        self.current_label_input = ""

        # 注册窗口类
        self._register_window_class()

    def _register_window_class(self):
        """注册遮罩窗口类"""
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "HEMouse_Overlay_Class"
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        win32gui.RegisterClass(wc)

    def activate_hint_mode(self):
        """激活Hint模式"""
        if self.hint_mode_active:
            return

        # 保存当前焦点
        self.previous_focus = win32gui.GetForegroundWindow()

        # 创建全屏遮罩窗口
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        self.overlay_hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW,
            "HEMouse_Overlay_Class",
            "HEMouse Hint Overlay",
            win32con.WS_POPUP,
            0, 0, screen_width, screen_height,
            0, 0, win32api.GetModuleHandle(None), None
        )

        # 设置透明度（90%透明）
        win32gui.SetLayeredWindowAttributes(
            self.overlay_hwnd,
            0,  # 颜色键
            int(255 * 0.1),  # 透明度
            win32con.LWA_ALPHA
        )

        # 显示窗口并设置焦点
        win32gui.ShowWindow(self.overlay_hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(self.overlay_hwnd)

        # 安装键盘钩子（作为安全网）
        self._install_keyboard_hook()

        self.hint_mode_active = True
        self.current_label_input = ""

    def deactivate_hint_mode(self):
        """退出Hint模式"""
        if not self.hint_mode_active:
            return

        self.hint_mode_active = False

        # 移除钩子
        self._uninstall_keyboard_hook()

        # 销毁窗口
        if self.overlay_hwnd:
            win32gui.DestroyWindow(self.overlay_hwnd)
            self.overlay_hwnd = None

        # 恢复焦点
        if self.previous_focus:
            try:
                win32gui.SetForegroundWindow(self.previous_focus)
            except:
                pass  # 原窗口可能已关闭

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """窗口消息处理"""
        if msg == win32con.WM_KEYDOWN:
            return self._handle_keydown(wparam)
        elif msg == win32con.WM_PAINT:
            self._handle_paint(hwnd)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _handle_keydown(self, vk_code):
        """处理按键事件"""
        # ESC - 退出
        if vk_code == win32con.VK_ESCAPE:
            self.deactivate_hint_mode()
            return 0

        # Space - 旋转重叠标签
        if vk_code == win32con.VK_SPACE:
            self._rotate_overlapping_labels()
            return 0

        # A-Z - 标签输入
        if 0x41 <= vk_code <= 0x5A:  # VK_A to VK_Z
            char = chr(vk_code).lower()
            self.current_label_input += char

            # 查找匹配的标签
            matched = self._find_matching_labels(self.current_label_input)

            if len(matched) == 1:
                # 唯一匹配，执行点击
                self._click_element(matched[0])
                self.deactivate_hint_mode()
            elif len(matched) == 0:
                # 无匹配，重置
                self.current_label_input = ""
                win32api.MessageBeep(win32con.MB_ICONHAND)  # 错误提示音

            return 0

        return 1  # 其他键不处理

    def _install_keyboard_hook(self):
        """安装底层键盘钩子（安全网）"""
        # TODO: 实现底层钩子（可选，用于处理边缘情况）
        pass

    def _uninstall_keyboard_hook(self):
        """移除键盘钩子"""
        # TODO: 实现钩子移除
        pass

    def _handle_paint(self, hwnd):
        """绘制提示标签"""
        hdc, ps = win32gui.BeginPaint(hwnd)

        # TODO: 绘制标签逻辑
        # 1. 获取UI元素列表
        # 2. 生成标签（使用Hint_Label_Design_Guide.md的算法）
        # 3. 绘制标签

        win32gui.EndPaint(hwnd, ps)

    def _find_matching_labels(self, input_str):
        """查找匹配的标签"""
        # TODO: 实现标签匹配逻辑
        return []

    def _click_element(self, element):
        """点击目标元素"""
        # TODO: 实现元素点击逻辑
        pass

    def _rotate_overlapping_labels(self):
        """旋转重叠标签"""
        # TODO: 实现标签旋转逻辑（参考Hint_Label_Design_Guide.md）
        pass

# 使用示例
if __name__ == "__main__":
    input_manager = HEMouseInputManager()

    # 激活Hint模式
    input_manager.activate_hint_mode()

    # 运行消息循环
    win32gui.PumpMessages()
```

---

## 5. 特殊情况处理

### 5.1 系统快捷键（不拦截）
以下按键应该让系统处理，不拦截：
- **Ctrl+Alt+Del**：安全注意序列
- **Win键**：开始菜单
- **Alt+Tab**：窗口切换
- **Win+L**：锁定屏幕

```python
def _should_bypass_system_key(self, vk_code, modifiers):
    """检查是否为系统快捷键"""
    # Ctrl+Alt+Del
    if vk_code == win32con.VK_DELETE and \
       modifiers['ctrl'] and modifiers['alt']:
        return True

    # Win键
    if vk_code in (win32con.VK_LWIN, win32con.VK_RWIN):
        return True

    # Alt+Tab
    if vk_code == win32con.VK_TAB and modifiers['alt']:
        return True

    return False
```

### 5.2 输入法（IME）处理
中文输入法可能干扰标签输入：

**解决方案**：
- Hint模式激活时，强制切换到英文模式
- 退出时恢复原输入法状态

```python
import win32api

def _disable_ime(self):
    """禁用输入法"""
    hwnd = self.overlay_hwnd
    himc = win32api.ImmGetContext(hwnd)
    win32api.ImmSetOpenStatus(himc, False)
    win32api.ImmReleaseContext(hwnd, himc)

def _restore_ime(self):
    """恢复输入法"""
    # TODO: 恢复之前的输入法状态
    pass
```

### 5.3 全屏游戏兼容性
某些全屏游戏使用独占模式（Exclusive Fullscreen），遮罩窗口可能无法覆盖：

**解决方案**：
- 检测全屏独占模式 → 提示用户切换到窗口化/无边框模式
- 或者使用更底层的方案（驱动级拦截，超出当前范围）

---

## 6. 测试方法

### 6.1 功能测试清单

| 测试场景 | 预期结果 | 测试方法 |
|---------|---------|---------|
| 文本编辑器（Notepad） | 标签输入不出现在文档中 | 打开Notepad，激活Hint，输入"aj" |
| 浏览器地址栏 | 标签输入不出现在地址栏 | Chrome地址栏获得焦点，激活Hint |
| 游戏（WASD控制） | 标签输入不触发游戏移动 | 运行游戏，激活Hint，输入"wasd" |
| 系统快捷键 | Alt+Tab仍然可用 | Hint模式下按Alt+Tab |
| 输入法 | 中文输入法被禁用 | 切换到中文输入法，激活Hint |
| ESC退出 | Hint模式正常退出，焦点恢复 | 激活Hint后按ESC |

### 6.2 边缘情况测试

```python
def test_keyboard_isolation():
    """自动化测试键盘隔离"""
    import pyautogui
    import time

    # 1. 打开Notepad
    os.system("notepad.exe &")
    time.sleep(1)

    # 2. 激活Hint模式
    input_manager.activate_hint_mode()
    time.sleep(0.5)

    # 3. 模拟输入
    pyautogui.press('a')
    pyautogui.press('j')
    time.sleep(0.5)

    # 4. 退出Hint模式
    input_manager.deactivate_hint_mode()

    # 5. 检查Notepad内容
    # 预期：Notepad为空（字符被拦截）
    # 如果Notepad显示"aj"，则测试失败
```

---

## 7. 性能优化

### 7.1 钩子性能
- 钩子回调必须<10ms返回（目标<5ms）
- 避免在回调中执行耗时操作（如文件I/O、网络请求）
- 使用线程池处理复杂逻辑

```python
import concurrent.futures

class OptimizedHookManager:
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def _hook_callback(self, nCode, wParam, lParam):
        """快速返回的钩子回调"""
        if nCode >= 0 and self.hint_mode_active:
            vk_code = self._extract_vk_code(lParam)

            # 快速检查是否为标签键
            if self._is_label_key(vk_code):
                # 异步处理复杂逻辑
                self.executor.submit(self._async_handle_input, vk_code)
                return 1  # 立即返回，阻止传播

        return ctypes.windll.user32.CallNextHookEx(...)
```

### 7.2 内存管理
- 遮罩窗口使用双缓冲绘制，避免闪烁
- 及时释放GDI资源（DC、Bitmap、Brush等）

---

## 8. 常见陷阱与注意事项

### ⚠️ 陷阱1：钩子死锁
**问题**：钩子回调中调用了`SendMessage`等同步API，导致消息循环阻塞

**解决**：
- 钩子回调中只做最小化处理
- 使用`PostMessage`异步发送消息
- 复杂逻辑放到独立线程

### ⚠️ 陷阱2：焦点丢失循环
**问题**：遮罩窗口尝试获取焦点 → 下层应用拒绝失焦 → 无限循环

**解决**：
- 设置焦点失败时，回退到纯钩子方案
- 添加超时保护（3秒无法获取焦点则放弃）

### ⚠️ 陷阱3：杀毒软件误报
**问题**：全局键盘钩子被杀毒软件标记为恶意行为

**解决**：
- 代码签名证书
- 向主流杀毒软件厂商提交白名单申请
- 在文档中说明合法用途

### ⚠️ 陷阱4：DPI缩放问题
**问题**：高DPI显示器上，遮罩窗口大小/位置不正确

**解决**：
```python
# 启用DPI感知
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
```

---

## 9. 总结与建议

### 9.1 推荐方案
**MVP阶段**：方案A（焦点窗口）
- 快速实现，验证核心功能
- 适用于90%的桌面办公场景

**生产阶段**：方案C（混合方案）
- 引入底层键盘钩子作为安全网
- 处理边缘情况和特殊应用

### 9.2 实施步骤
1. **Week 1-2**：实现焦点窗口方案，完成基础拦截
2. **Week 3**：集成到Hint模式，测试主流应用（Chrome、VSCode、Office）
3. **Week 4-5**：引入底层键盘钩子，处理边缘情况
4. **Week 6**：性能优化，减少延迟到<5ms
5. **Week 7-8**：兼容性测试（游戏、全屏应用、输入法）

### 9.3 关键指标
- **拦截成功率**：>99.9%（下层应用不收到Hint模式的输入）
- **延迟**：<5ms（从按键到拦截的延迟）
- **兼容性**：覆盖95%+的常用应用

---

## 10. 参考资料

### 技术文档
- [Windows Hooks Reference](https://docs.microsoft.com/en-us/windows/win32/winmsg/hooks)
- [Keyboard Input Reference](https://docs.microsoft.com/en-us/windows/win32/inputdev/keyboard-input)
- [SetWindowsHookEx Function](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowshookexw)

### 开源项目参考
- [AutoHotkey键盘钩子实现](https://github.com/AutoHotkey/AutoHotkey)
- [PowerToys Keyboard Manager](https://github.com/microsoft/PowerToys/tree/main/src/modules/keyboardmanager)

### HEMouse项目文档
- `Hint_Label_Design_Guide.md` - 提示标签设计指南
- `Mode_Transition_UX_Analysis.md` - 模式切换用户体验分析

---

**文档版本**：v1.0
**创建日期**：2025-09-30
**状态**：✅ Ready for Implementation