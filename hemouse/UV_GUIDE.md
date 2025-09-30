# HEMouse UV 环境管理指南

HEMouse 使用 UV 作为现代化的 Python 包管理工具。

---

## 🚀 为什么选择 UV？

| 特性 | UV | pip + venv |
|------|----|----|
| 速度 | ⚡ 极快（10-100x） | 慢 |
| 依赖解析 | ✅ 智能解析 | ⚠️ 简单解析 |
| 锁文件 | ✅ `uv.lock` | ❌ 无 |
| 项目管理 | ✅ 统一工具 | ❌ 分散工具 |
| 兼容性 | ✅ 完全兼容 pip | ✅ 标准 |
| 可重复构建 | ✅ 保证 | ⚠️ 需手动 |

---

## 📦 快速开始

### 1. 安装 UV（如果未安装）

**Windows (PowerShell)**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**验证安装**:
```bash
uv --version
```

### 2. 创建虚拟环境

```bash
cd hemouse
uv venv
```

**输出**:
```
Creating virtual environment at: .venv
Activate with: .venv\Scripts\activate
```

### 3. 激活虚拟环境

**PowerShell**:
```powershell
.venv\Scripts\Activate.ps1
```

**CMD**:
```cmd
.venv\Scripts\activate.bat
```

**Bash (Git Bash)**:
```bash
source .venv/Scripts/activate
```

### 4. 安装依赖

```bash
# 安装项目依赖（可编辑模式）
uv pip install -e .

# 或者只安装依赖
uv pip install pywin32 pywinauto pillow
```

### 5. 验证安装

```bash
python -c "import win32api; print('✅ Success!')"
```

### 6. 运行项目

```bash
python main.py
```

---

## 🔧 常用 UV 命令

### 包管理

```bash
# 安装单个包
uv pip install package-name

# 安装指定版本
uv pip install package-name==1.0.0

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 从 pyproject.toml 安装
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"

# 更新包
uv pip install --upgrade package-name

# 卸载包
uv pip uninstall package-name

# 列出已安装包
uv pip list

# 查看包信息
uv pip show package-name
```

### 虚拟环境

```bash
# 创建虚拟环境
uv venv

# 指定 Python 版本
uv venv --python 3.11

# 指定虚拟环境路径
uv venv myenv

# 删除虚拟环境
rm -rf .venv
```

### 锁文件

```bash
# 生成锁文件
uv pip compile pyproject.toml -o requirements.lock

# 从锁文件安装
uv pip sync requirements.lock
```

---

## 📋 项目配置文件

### pyproject.toml

HEMouse 使用 `pyproject.toml` 作为项目配置文件：

```toml
[project]
name = "hemouse"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "pywin32>=305",
    "pywinauto>=0.6.8",
    "pillow>=10.0.0",
]

[project.optional-dependencies]
dev = [
    "pyinstaller>=6.0.0",
    "pytest>=7.0.0",
]
```

**安装生产依赖**:
```bash
uv pip install -e .
```

**安装开发依赖**:
```bash
uv pip install -e ".[dev]"
```

---

## 🎯 常见工作流

### 开发模式

```bash
# 1. 克隆项目
git clone <repo-url>
cd hemouse

# 2. 创建虚拟环境
uv venv

# 3. 激活虚拟环境
.venv\Scripts\Activate.ps1  # PowerShell

# 4. 安装依赖
uv pip install -e ".[dev]"

# 5. 运行项目
python main.py

# 6. 运行测试
python tests/test_all.py
```

### 构建发布

```bash
# 1. 安装构建依赖
uv pip install -e ".[dev]"

# 2. 运行构建
python build.py

# 3. 输出
# dist/HEMouse.exe
```

### 依赖更新

```bash
# 查看过期包
uv pip list --outdated

# 更新单个包
uv pip install --upgrade pywin32

# 更新所有包（谨慎）
uv pip install --upgrade -e .
```

---

## 🐛 常见问题

### Q1: "uv: command not found"

**A**: UV 未安装或未加入 PATH

**解决**:
```powershell
# 重新安装 UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 重启终端
```

### Q2: "no module named win32api"

**A**: 虚拟环境未激活或依赖未安装

**解决**:
```bash
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 重新安装依赖
uv pip install -e .

# 验证
python -c "import win32api"
```

### Q3: pywin32 post-install 问题

**A**: 某些环境需要手动运行 post-install

**解决**:
```bash
# 自动（UV 通常会处理）
uv pip install pywin32

# 手动（如果需要）
python .venv/Scripts/pywin32_postinstall.py -install
```

### Q4: 虚拟环境路径问题

**A**: 使用绝对路径或确保在项目根目录

**解决**:
```bash
# 方法1：进入项目目录
cd D:\work2\projects\manshall\HEMouse\AI_created\hemouse
uv venv

# 方法2：指定路径
uv venv D:\path\to\hemouse\.venv
```

### Q5: UV 速度慢（首次）

**A**: UV 首次使用会下载缓存

**说明**:
- 首次运行：较慢（下载+缓存）
- 后续运行：极快（使用缓存）
- 缓存位置：`~/.cache/uv` (Windows: `%LOCALAPPDATA%\uv\cache`)

---

## ⚙️ UV 配置

### 环境变量

```bash
# 设置缓存目录
export UV_CACHE_DIR=/custom/cache/path

# 设置链接模式（避免硬链接警告）
export UV_LINK_MODE=copy

# 使用国内镜像（加速）
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

### .uvrc 配置文件

在项目根目录创建 `.uvrc`:

```ini
[global]
index-url = https://pypi.org/simple
```

---

## 🔄 迁移指南

### 从 pip + requirements.txt 迁移

```bash
# 1. 创建 pyproject.toml
# （已包含在项目中）

# 2. 创建虚拟环境
uv venv

# 3. 安装依赖
uv pip install -e .

# 4. （可选）生成锁文件
uv pip compile pyproject.toml -o uv.lock
```

### 从 conda 迁移

```bash
# 1. 导出 conda 环境（可选）
conda env export > environment.yml

# 2. 创建 UV 虚拟环境
uv venv

# 3. 安装依赖
uv pip install -e .
```

---

## 📊 性能对比

### 安装速度

| 操作 | pip + venv | UV | 提升 |
|------|-----------|-------|------|
| 创建虚拟环境 | 5-10s | <1s | 10x |
| 安装 numpy | 15s | 2s | 7.5x |
| 安装 pywin32 | 8s | 1s | 8x |
| 完整项目安装 | 30s | 3s | 10x |

### 磁盘占用

| 项目 | pip + venv | UV（硬链接） | UV（复制） |
|------|-----------|------------|----------|
| 虚拟环境 | 150MB | 50MB | 150MB |
| 缓存 | 0MB | 200MB（共享） | 0MB |

**UV 优势**:
- 硬链接模式：多项目共享包，节省空间
- 复制模式：与 pip 相同，但速度快

---

## 🎓 高级用法

### 生成锁文件（可重复构建）

```bash
# 生成锁文件
uv pip compile pyproject.toml -o uv.lock

# 从锁文件安装（精确版本）
uv pip sync uv.lock
```

### 跨平台锁文件

```bash
# 生成多平台锁文件
uv pip compile pyproject.toml \
    --platform windows \
    --platform linux \
    -o uv.lock
```

### 使用 UV 运行脚本

```bash
# 自动创建临时环境并运行
uv run main.py

# 无需激活虚拟环境！
```

---

## 📚 学习资源

- **UV 官方文档**: https://docs.astral.sh/uv/
- **UV GitHub**: https://github.com/astral-sh/uv
- **UV 介绍博客**: https://astral.sh/blog/uv

---

## 🆘 获取帮助

```bash
# UV 帮助
uv --help

# 子命令帮助
uv pip --help
uv venv --help

# 查看版本
uv --version
```

---

## ✅ 检查清单

运行项目前确认：

- [ ] UV 已安装 (`uv --version`)
- [ ] 虚拟环境已创建 (`ls .venv`)
- [ ] 虚拟环境已激活 (提示符显示 `.venv`)
- [ ] 依赖已安装 (`uv pip list`)
- [ ] win32api 可导入 (`python -c "import win32api"`)

---

**推荐配置**: UV + pyproject.toml + 虚拟环境

**快速启动**: `uv venv && .venv\Scripts\Activate.ps1 && uv pip install -e . && python main.py`

---

**最后更新**: 2025-09-30