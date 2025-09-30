# HEMouse 快速启动指南

## 🚀 5分钟上手

### 步骤1: 安装依赖

```bash
cd hemouse
pip install -r requirements.txt
```

**必需依赖**:
- pywin32 (Windows API)
- pywinauto (UI自动化)
- Pillow (图像处理)

### 步骤2: 运行程序

```bash
python main.py
```

**预期输出**:
```
============================================================
HEMouse - Hands-Free Mouse Control
============================================================
🔧 Initializing components...
✅ Components initialized

🚀 Starting HEMouse...
🟢 Hotkey monitoring started

============================================================
✅ HEMouse is ready!
============================================================

📖 Quick Start Guide:
   1. Press CapsLock to activate Hint mode
   2. Type labels (a-z) to select elements
   3. Press Space to switch to Grid mode
   4. Press ESC to exit current mode
   5. Press Ctrl+C to exit HEMouse

⌛ Waiting for CapsLock...
```

### 步骤3: 测试Hint模式

1. **打开Chrome浏览器**（或任意应用）
2. **按下CapsLock键**
   - 屏幕变暗
   - 黄色标签出现在可点击元素旁边
3. **输入标签字母**
   - 例如: 按 `a` 点击标签为'A'的元素
   - 例如: 按 `sj` 点击标签为'SJ'的元素
4. **按ESC退出**

### 步骤4: 测试Grid模式

1. **按CapsLock激活Hint模式**
2. **按Space键切换到Grid模式**
   - 屏幕显示3x3网格，数字1-9
3. **按数字键选择网格**
   - 例如: 按 `5` 移动鼠标到中心
   - 例如: 按 `9` 移动鼠标到右下角
4. **按ESC退出**

---

## 🧪 运行测试

```bash
python tests/test_all.py
```

**测试内容**:
- ✅ 标签生成算法
- ✅ 模式管理器
- ⚠️ 热键检测（需手动测试）
- ⚠️ 元素检测（需活动窗口）

---

## 📦 构建可执行文件

```bash
python build.py
```

**输出**: `dist/HEMouse.exe`

---

## ⚙️ 配置（可选）

### 修改标签字符集

编辑 `src/core/label_generator.py`:

```python
def __init__(self, charset="asdfghjkl"):  # 默认字符集
    # 修改为: charset="asdfghjkl;"  # 添加更多字符
```

### 修改轮询间隔

编辑 `src/core/hotkey_manager.py`:

```python
self.poll_interval = 0.05  # 50ms
# 修改为: self.poll_interval = 0.03  # 30ms (更快响应)
```

---

## 🐛 常见问题

### Q: "ModuleNotFoundError: No module named 'win32api'"

**A**: 安装pywin32
```bash
pip install pywin32
```

### Q: "No clickable elements found"

**A**:
1. 确保窗口处于前台（点击窗口激活）
2. 尝试使用Grid模式（按Space）
3. 部分应用可能不支持UI自动化

### Q: 标签重叠看不清

**A**:
1. 放大应用界面
2. 使用Grid模式作为备用
3. 等待v1.1版本的碰撞避免功能

### Q: CapsLock不响应

**A**:
1. 等待0.5秒（轮询延迟）
2. 检查CapsLock LED是否变化
3. 关闭其他键盘监听软件

---

## 📚 进一步学习

- **用户手册**: `docs/USER_GUIDE.md`
- **架构文档**: `docs/ARCHITECTURE.md`
- **开发指南**: `docs/DEVELOPMENT.md`

---

## 🆘 获取帮助

- **GitHub Issues**: 报告bug
- **Email**: support@hemouse.dev
- **文档**: `docs/` 目录

---

**祝使用愉快！🎉**