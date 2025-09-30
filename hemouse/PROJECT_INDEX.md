# HEMouse 项目索引

快速导航到项目的各个部分。

---

## 📂 核心文件

### 入口点

- **`main.py`** - 应用程序主入口，包含HEMouseApp类
  - 启动命令: `python main.py`
  - 功能: 初始化组件、注册热键、主事件循环

### 构建与配置

- **`build.py`** - PyInstaller构建脚本
  - 使用: `python build.py`
  - 输出: `dist/HEMouse.exe`

- **`requirements.txt`** - Python依赖列表
  - 安装: `pip install -r requirements.txt`

- **`.gitignore`** - Git忽略规则

---

## 📚 文档

### 用户文档

- **`README.md`** - 项目概述和快速开始
- **`QUICKSTART.md`** - 5分钟快速上手指南
- **`docs/USER_GUIDE.md`** - 完整用户手册（15页）
  - Hint模式详解
  - Grid模式详解
  - 常见问题解答

### 技术文档

- **`docs/ARCHITECTURE.md`** - 系统架构文档（20页）
  - 组件设计
  - 数据流
  - 性能分析

- **`docs/DEVELOPMENT.md`** - 开发者指南（15页）
  - 开发环境设置
  - 代码规范
  - 贡献指南

### 项目报告

- **`generated_docs/12_mvp_completion_report.md`** - MVP完成报告
  - 功能清单
  - 测试报告
  - 路线图

---

## 💻 源代码

### 核心模块 (`src/core/`)

| 文件 | 功能 | 关键类/方法 |
|------|------|-----------|
| `hotkey_manager.py` | CapsLock检测 | `HotkeyManager` |
| `element_detector.py` | UI元素检测 | `ElementDetector.get_clickable_elements()` |
| `label_generator.py` | 标签生成 | `LabelGenerator.generate_labels()` |

**快速定位**:
```python
# 修改CapsLock检测频率
src/core/hotkey_manager.py:17  # self.poll_interval

# 修改元素检测深度
src/core/element_detector.py:20  # max_depth=10

# 修改标签字符集
src/core/label_generator.py:12  # charset="asdfghjkl"
```

### 模式管理 (`src/modes/`)

| 文件 | 功能 | 关键类/方法 |
|------|------|-----------|
| `mode_manager.py` | 模式状态管理 | `ModeManager.switch_mode()` |
| `hint_mode.py` | Hint模式控制器 | `HintMode.activate()` |
| `grid_mode.py` | Grid模式控制器 | `GridMode._select_grid()` |

**快速定位**:
```python
# 添加新模式
src/modes/mode_manager.py:9  # class Mode(Enum)

# 修改Hint模式逻辑
src/modes/hint_mode.py:30  # def activate()

# 修改Grid大小
src/modes/grid_mode.py:13  # grid_size=3
```

### UI组件 (`src/ui/`)

| 文件 | 功能 | 关键类/方法 |
|------|------|-----------|
| `overlay_window.py` | 透明遮罩窗口 | `OverlayWindow.draw_labels()` |

**快速定位**:
```python
# 修改透明度
src/ui/overlay_window.py:28  # attributes('-alpha', 0.3)

# 修改标签颜色
src/ui/overlay_window.py:55  # fill='yellow'
```

### 工具模块 (`src/utils/`)

| 文件 | 功能 | 关键类/方法 |
|------|------|-----------|
| `logger.py` | 日志工具 | `HEMouseLogger` |

---

## 🧪 测试

### 测试文件 (`tests/`)

- **`test_all.py`** - 完整测试套件
  - 运行: `python tests/test_all.py`
  - 包含: 标签生成、模式管理、热键检测、元素检测

**测试覆盖**:
```
✅ 自动化测试:
   - LabelGenerator (单元测试)
   - ModeManager (单元测试)

⚠️ 手动测试:
   - HotkeyManager (需用户按CapsLock)
   - ElementDetector (需活动窗口)
```

---

## 🔍 快速查找

### 常见任务

| 任务 | 文件位置 | 行号 |
|------|---------|------|
| 修改CapsLock热键 | `main.py` | 89-90 |
| 添加新的可点击类型 | `src/core/element_detector.py` | 54-58 |
| 修改标签字符集 | `src/core/label_generator.py` | 12 |
| 调整遮罩透明度 | `src/ui/overlay_window.py` | 28 |
| 修改Grid尺寸 | `src/modes/grid_mode.py` | 13 |

### 关键算法

| 算法 | 文件 | 方法 |
|------|------|------|
| 无前缀冲突标签生成 | `src/core/label_generator.py` | `generate_labels()` |
| UI树递归遍历 | `src/core/element_detector.py` | `_traverse_elements()` |
| 标签输入匹配 | `src/modes/hint_mode.py` | `_on_key_press()` |
| Grid递归细化 | `src/modes/grid_mode.py` | `_select_grid()` |

### 关键数据结构

```python
# Element字典
{
    'element': UIAWrapper对象,
    'rect': Rectangle对象,
    'type': 'Button' | 'Hyperlink' | ...,
    'name': 字符串
}

# Mode枚举
Mode.IDLE    # 空闲模式
Mode.HINT    # Hint模式
Mode.GRID    # Grid模式
```

---

## 🎓 学习路径

### 新手上路

1. 阅读 `README.md` - 了解项目概述
2. 阅读 `QUICKSTART.md` - 5分钟快速体验
3. 运行 `python main.py` - 实际操作
4. 阅读 `docs/USER_GUIDE.md` - 深入了解功能

### 开发者入门

1. 阅读 `docs/ARCHITECTURE.md` - 理解系统架构
2. 阅读 `docs/DEVELOPMENT.md` - 了解开发规范
3. 运行 `python tests/test_all.py` - 验证环境
4. 修改源码 → 测试 → 提交PR

### 高级定制

1. 研究 `src/core/label_generator.py` - 自定义标签算法
2. 研究 `src/ui/overlay_window.py` - 自定义UI样式
3. 添加新模式到 `src/modes/` - 扩展功能
4. 优化 `src/core/element_detector.py` - 提升性能

---

## 📊 项目统计

```
代码行数:
  Python源文件: ~2500行
  文档文件: ~3000行
  测试文件: ~300行

文件数量:
  源码文件: 13个
  文档文件: 8个
  测试文件: 1个

依赖项:
  核心依赖: 3个 (pywin32, pywinauto, Pillow)
  构建依赖: 1个 (PyInstaller)
```

---

## 🔗 外部资源

### 官方文档

- **pywin32**: https://github.com/mhammond/pywin32
- **pywinauto**: https://pywinauto.readthedocs.io/
- **Windows UIA**: https://docs.microsoft.com/en-us/windows/win32/winauto/

### 灵感来源

- **Vimium**: https://github.com/philc/vimium
- **Homerow**: https://www.homerow.app/
- **Talon**: https://talonvoice.com/

---

## 🗺️ 项目目录树

```
hemouse/
├── 📄 README.md                    # 项目概述
├── 📄 QUICKSTART.md                # 快速启动
├── 📄 PROJECT_INDEX.md             # 本文件
├── 📄 main.py                      # 入口点
├── 📄 build.py                     # 构建脚本
├── 📄 requirements.txt             # 依赖列表
├── 📄 .gitignore                   # Git配置
│
├── 📁 src/                         # 源代码
│   ├── 📁 core/                    # 核心模块
│   │   ├── hotkey_manager.py
│   │   ├── element_detector.py
│   │   └── label_generator.py
│   ├── 📁 modes/                   # 模式管理
│   │   ├── mode_manager.py
│   │   ├── hint_mode.py
│   │   └── grid_mode.py
│   ├── 📁 ui/                      # UI组件
│   │   └── overlay_window.py
│   └── 📁 utils/                   # 工具
│       └── logger.py
│
├── 📁 tests/                       # 测试
│   └── test_all.py
│
├── 📁 docs/                        # 文档
│   ├── USER_GUIDE.md               # 用户手册
│   ├── ARCHITECTURE.md             # 架构文档
│   └── DEVELOPMENT.md              # 开发指南
│
├── 📁 assets/                      # 资源文件
├── 📁 logs/                        # 日志目录
└── 📁 dist/                        # 构建输出
    └── HEMouse.exe
```

---

## 🎯 快速跳转

- **想要快速体验**: → `QUICKSTART.md`
- **想要深入了解**: → `docs/USER_GUIDE.md`
- **想要修改代码**: → `docs/DEVELOPMENT.md`
- **想要理解架构**: → `docs/ARCHITECTURE.md`
- **遇到问题**: → `docs/USER_GUIDE.md` FAQ章节
- **想要贡献**: → `docs/DEVELOPMENT.md` 贡献章节

---

**最后更新**: 2025-09-30
**版本**: 1.0