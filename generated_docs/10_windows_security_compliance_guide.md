# Windows安全合规指南

## Q4: 如何避免被Windows安全程序误判为恶意行为？

---

## 1. 问题分析

### 1.1 为什么HEMouse会被误判？

HEMouse的核心功能与恶意软件的典型行为高度重合：

| HEMouse功能 | 恶意软件相似行为 | 风险等级 |
|------------|----------------|---------|
| **全局键盘钩子** | 键盘记录器（Keylogger） | 🔴 HIGH |
| **键盘输入拦截** | 窃取密码、信用卡信息 | 🔴 HIGH |
| **遮罩层窗口** | 网络钓鱼（假冒登录界面） | 🟡 MEDIUM |
| **UI自动化（UIA）** | 点击劫持、自动化攻击 | 🟡 MEDIUM |
| **开机自启动** | 持久化驻留 | 🟡 MEDIUM |
| **DLL注入（如果使用）** | 进程劫持、代码注入 | 🔴 HIGH |

### 1.2 典型误报场景

**场景1：Windows Defender误报**
```
威胁名称: Trojan:Win32/Wacatac.B!ml
检测到的文件: hemouse.exe
风险: 高
行为: 全局键盘钩子 + 键盘输入拦截
```

**场景2：第三方杀毒软件（如卡巴斯基、诺顿）**
```
威胁类型: Potentially Unwanted Program (PUP)
原因: 未签名的可执行文件使用敏感API
建议: 隔离或删除
```

**场景3：企业防护软件（如CrowdStrike、Carbon Black）**
```
行为检测: 异常进程行为
- 全局钩子安装
- 键盘输入监控
- 跨进程窗口操作
动作: 阻止执行 + 上报安全团队
```

### 1.3 影响范围

- **用户体验**：安装失败、程序无法启动
- **信任度**：用户怀疑软件安全性
- **市场推广**：下载量降低、负面评价
- **企业部署**：IT部门拒绝批准安装

---

## 2. 安全合规策略矩阵

### 2.1 合规层级（4层防御）

```
┌─────────────────────────────────────────────────────────┐
│ Layer 4: 行为透明化（运行时信任）                        │
│ - 用户授权提示                                           │
│ - 实时行为日志                                           │
│ - 隐私声明                                               │
└─────────────────────────────────────────────────────────┘
             ↑
┌─────────────────────────────────────────────────────────┐
│ Layer 3: 安全厂商白名单（第三方认证）                    │
│ - 向杀毒软件厂商申请白名单                               │
│ - 提交VirusTotal扫描报告                                │
│ - Microsoft SmartScreen信誉累积                         │
└─────────────────────────────────────────────────────────┘
             ↑
┌─────────────────────────────────────────────────────────┐
│ Layer 2: 代码签名（身份认证）                            │
│ - EV代码签名证书                                         │
│ - 时间戳签名                                             │
│ - 签名验证自动化                                         │
└─────────────────────────────────────────────────────────┘
             ↑
┌─────────────────────────────────────────────────────────┐
│ Layer 1: 代码实现安全（技术基础）                        │
│ - 最小权限原则                                           │
│ - 安全API选择                                            │
│ - 沙箱隔离                                               │
│ - 开源透明                                               │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1: 代码实现安全

### 3.1 最小权限原则

**原则**：只请求必要的权限，避免过度权限

#### 权限需求分析

| 功能 | 需要权限 | 风险评估 | 替代方案 |
|-----|---------|---------|---------|
| 键盘钩子 | 用户级钩子 | 中 | ✅ 使用`WH_KEYBOARD_LL`（用户级）<br>❌ 避免内核驱动 |
| UI元素检测 | UIA访问权限 | 低 | ✅ 使用Windows UIA API<br>❌ 避免进程注入 |
| 遮罩窗口 | 无特殊权限 | 低 | ✅ 标准窗口API |
| 开机自启动 | 注册表写入 | 中 | ✅ 用户批准后写入<br>❌ 避免服务安装 |

#### 不需要管理员权限

```python
# ✅ 好的实践：用户级钩子，不需要管理员权限
def install_user_level_hook():
    """用户级键盘钩子"""
    hook_handle = ctypes.windll.user32.SetWindowsHookExW(
        13,  # WH_KEYBOARD_LL（用户级）
        callback,
        None,
        0
    )
    return hook_handle

# ❌ 坏的实践：要求管理员权限
def install_kernel_driver():
    """内核驱动（需要管理员权限）"""
    # 这会触发UAC提示，且被杀毒软件高度警惕
    service_handle = win32service.CreateService(...)
```

### 3.2 安全API选择

#### 键盘钩子：选择用户级而非内核级

```cpp
// ✅ 推荐：用户级底层钩子（WH_KEYBOARD_LL）
HHOOK hook = SetWindowsHookEx(
    WH_KEYBOARD_LL,  // 用户模式，低风险
    KeyboardProc,
    hInstance,
    0  // 全局钩子，但仍在用户空间
);

// ❌ 避免：内核驱动过滤
// 需要签名、管理员权限、极高风险
NTSTATUS status = IoCreateDevice(...);
```

#### UI自动化：使用官方UIA而非注入

```python
# ✅ 推荐：Windows UIA API（官方支持）
from pywinauto import Desktop
desktop = Desktop(backend="uia")
elements = desktop.windows()

# ❌ 避免：DLL注入
# 极高风险，杀毒软件必定拦截
def inject_dll(target_pid, dll_path):
    # 不要使用这种方法！
    pass
```

### 3.3 数据隐私保护

#### 不存储敏感数据

```python
class KeyboardInputHandler:
    def __init__(self):
        # ❌ 避免：记录所有键盘输入
        self.input_history = []

    def on_key_press(self, key):
        # ✅ 推荐：只处理标签键，立即丢弃
        if self.is_label_key(key):
            self.handle_label_selection(key)
            # 不记录到日志或文件
        else:
            # 忽略非标签键
            pass

    # ❌ 避免：持久化键盘输入
    def save_logs(self):
        with open("keylog.txt", "w") as f:
            f.write(str(self.input_history))
```

#### 网络通信透明化

```python
# ✅ 推荐：无网络通信（除非必要）
# HEMouse不需要联网，避免任何网络请求

# 如果必须联网（如更新检查）：
def check_for_updates():
    """透明的更新检查"""
    # 1. 提前告知用户
    if not user_consent_for_update_check():
        return

    # 2. 使用HTTPS
    response = requests.get(
        "https://hemouse.example.com/version.json",
        timeout=5
    )

    # 3. 记录日志
    logger.info(f"Update check: {response.status_code}")

    # 4. 不发送任何用户数据
    # ❌ 避免：发送用户ID、系统信息、使用统计
```

### 3.4 代码混淆 vs 开源透明

**选择：开源透明（推荐）**

| 策略 | 优点 | 缺点 | 推荐度 |
|-----|------|------|-------|
| **开源（GitHub公开）** | - 可审计性<br>- 社区信任<br>- 杀毒软件易验证 | - 无商业秘密保护 | ⭐⭐⭐⭐⭐ |
| **代码混淆** | - 保护知识产权 | - 增加可疑度<br>- 杀毒软件误报率↑ | ⭐⭐ |
| **闭源二进制** | - 完全保密 | - 信任度↓<br>- 误报率最高 | ⭐ |

**开源策略**：
```yaml
仓库结构:
  hemouse/
    src/              # 完整源代码
    docs/             # 文档
    tests/            # 单元测试
    SECURITY.md       # 安全声明
    PRIVACY.md        # 隐私政策
    CODE_OF_CONDUCT.md

许可证: MIT或Apache 2.0（宽松开源）

安全声明示例:
  - 不收集用户数据
  - 不联网（除更新检查）
  - 键盘输入仅本地处理
  - 可审计的代码
```

---

## 4. Layer 2: 代码签名（身份认证）

### 4.1 为什么需要代码签名？

**Windows SmartScreen机制**：
```
未签名程序 → "Windows已保护你的电脑"警告 → 用户放弃安装（70%+）
已签名程序 → 验证发布者身份 → 降低拦截率（减少90%+误报）
```

### 4.2 EV代码签名证书（强烈推荐）

#### 证书类型对比

| 证书类型 | 验证级别 | 信誉累积 | SmartScreen效果 | 价格 | 推荐度 |
|---------|---------|---------|----------------|------|-------|
| **EV代码签名** | 企业身份验证 | 立即信誉 | 无警告 | $300-500/年 | ⭐⭐⭐⭐⭐ |
| **标准代码签名** | 基础身份验证 | 需累积 | 初期有警告 | $100-200/年 | ⭐⭐⭐ |
| **自签名证书** | 无验证 | 无信誉 | 严重警告 | 免费 | ⭐ |

#### EV证书优势

**立即信誉**：
- 首次发布即可绕过SmartScreen警告
- 显示完整企业名称（如"Manshall Technology Co."）
- 杀毒软件白名单申请更易通过

**硬件保护**：
- 私钥存储在USB硬件令牌中，无法被盗
- 防止证书滥用和吊销风险

### 4.3 获取EV证书步骤

#### 推荐供应商

| 供应商 | 价格 | 验证周期 | 支持 |
|-------|------|---------|------|
| **DigiCert** | $474/年 | 3-5工作日 | ⭐⭐⭐⭐⭐ |
| **Sectigo (Comodo)** | $299/年 | 5-7工作日 | ⭐⭐⭐⭐ |
| **GlobalSign** | $399/年 | 3-5工作日 | ⭐⭐⭐⭐ |

#### 申请流程

**1. 企业身份准备**（1-2天）
```yaml
必需材料:
  - 营业执照副本
  - 企业银行账户证明
  - 法人身份证
  - 企业邮箱（@company.com）
  - 企业电话（可验证）

注意:
  - 个人开发者需注册个体工商户或公司
  - 地址必须与工商注册地址一致
```

**2. 在线申请**（1天）
```
1. 访问DigiCert官网 → Code Signing → EV Code Signing Certificate
2. 填写企业信息（英文）
3. 上传企业文件
4. 支付$474（支持信用卡/PayPal）
```

**3. 身份验证**（3-5天）
```
DigiCert会通过以下方式验证：
- 邓白氏编码（DUNS）查询（自动）
- 电话回访（验证企业存在）
- 企业邮箱确认（验证员工身份）
- 银行账户验证（可选）
```

**4. 收到USB令牌**（5-7天物流）
```
DigiCert寄送SafeNet USB令牌：
- 包含私钥的硬件设备
- 需要设置PIN码
- 插入电脑后才能签名
```

### 4.4 签名实践

#### Windows可执行文件签名

```bash
# 使用signtool（Windows SDK自带）
signtool sign ^
  /f "certificate.pfx" ^            # 证书文件（如果使用软件证书）
  /p "password" ^                    # 证书密码
  /fd SHA256 ^                       # 使用SHA256哈希
  /tr http://timestamp.digicert.com ^  # 时间戳服务器
  /td SHA256 ^                       # 时间戳哈希算法
  /v ^                               # 详细输出
  hemouse.exe

# 如果使用EV证书的USB令牌：
signtool sign ^
  /n "Your Company Name" ^           # 证书主题名称
  /fd SHA256 ^
  /tr http://timestamp.digicert.com ^
  /td SHA256 ^
  /v ^
  hemouse.exe
```

#### Python打包签名（PyInstaller）

```python
# build_and_sign.py
import subprocess
import os

def build_executable():
    """使用PyInstaller打包"""
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=hemouse.ico",
        "--name=HEMouse",
        "main.py"
    ], check=True)

def sign_executable(exe_path):
    """签名可执行文件"""
    subprocess.run([
        "signtool", "sign",
        "/n", "Manshall Technology Co.",  # 你的公司名
        "/fd", "SHA256",
        "/tr", "http://timestamp.digicert.com",
        "/td", "SHA256",
        "/v",
        exe_path
    ], check=True)

if __name__ == "__main__":
    build_executable()
    sign_executable("dist/HEMouse.exe")
    print("✅ Build and sign completed")
```

#### DLL签名（C++核心模块）

```bash
# 签名hemouse_core.dll
signtool sign ^
  /n "Your Company Name" ^
  /fd SHA256 ^
  /tr http://timestamp.digicert.com ^
  /td SHA256 ^
  hemouse_core.dll

# 验证签名
signtool verify /pa hemouse_core.dll
```

### 4.5 时间戳重要性

**没有时间戳的后果**：
- 证书过期后，签名失效
- 用户下载旧版本时会报错

**使用时间戳**：
- 证明"签名时证书有效"
- 证书过期后，旧版本仍可信任

```bash
# ✅ 好的实践：添加时间戳
signtool sign /tr http://timestamp.digicert.com /td SHA256 hemouse.exe

# ❌ 坏的实践：不添加时间戳
signtool sign hemouse.exe  # 证书过期后签名失效
```

---

## 5. Layer 3: 安全厂商白名单

### 5.1 Microsoft Defender提交

#### 误报申诉流程

**1. 提交到Microsoft Security Intelligence**
```
网址: https://www.microsoft.com/wdsi/filesubmission

步骤:
1. 选择"Software developer" → "Submit suspected false positive"
2. 上传hemouse.exe
3. 填写表单:
   - File name: HEMouse.exe
   - SHA256: [计算文件哈希]
   - Software name: HEMouse
   - Contact email: your@email.com
4. 详细说明:
   "HEMouse is a legitimate accessibility tool that uses keyboard hooks
    for hands-free mouse control. It does not collect user data or
    connect to the internet. Source code available at github.com/..."
```

**2. 等待人工审核**（1-3个工作日）
```
审核结果:
- ✅ 通过: 文件从威胁定义中移除，全球生效
- ❌ 拒绝: 需要修改代码或提供更多证明
```

#### 预防性提交（推荐）

```
在发布前提交:
- 避免用户遇到误报
- 累积SmartScreen信誉
- 建立与Microsoft的信任关系

提交时机:
- 每个新版本发布前7天提交
- 主版本更新必须提交
- 代码签名证书更换后重新提交
```

### 5.2 第三方杀毒软件白名单

#### 主流杀毒软件申诉渠道

| 杀毒软件 | 误报申诉网址 | 审核周期 | 备注 |
|---------|------------|---------|------|
| **Kaspersky** | https://opentip.kaspersky.com/ | 1-2天 | 需要俄语或英语 |
| **Norton (Symantec)** | https://submit.norton.com/ | 2-3天 | 详细说明必需 |
| **McAfee** | https://www.mcafee.com/enterprise/en-us/threat-center/submit-sample.html | 3-5天 | 企业用户优先 |
| **Avast/AVG** | https://www.avast.com/false-positive-file-form.php | 1-2天 | 需要上传样本 |
| **Bitdefender** | https://www.bitdefender.com/submit/ | 2-4天 | 提供源代码链接有助于审核 |
| **趋势科技** | https://www.trendmicro.com/en_us/about/legal/detection-reevaluation.html | 3-5天 | 日本公司，支持中文 |

#### 申诉模板

```
Subject: False Positive Report - HEMouse Accessibility Software

Dear [Antivirus Vendor] Security Team,

I am writing to report a false positive detection of our software HEMouse.

**Product Information:**
- Name: HEMouse
- Version: 1.0.0
- File: hemouse.exe
- SHA256: [hash]
- Developer: Manshall Technology Co.
- Website: https://hemouse.example.com
- Source Code: https://github.com/manshall/hemouse

**Purpose:**
HEMouse is a legitimate accessibility tool that enables hands-free mouse
control using head movements and keyboard shortcuts. It is designed to
help users with RSI (Repetitive Strain Injury) and improve ergonomics.

**Why it uses sensitive APIs:**
- Keyboard hooks (SetWindowsHookEx): To provide keyboard-based mouse control
- UI Automation (UIA): To detect clickable elements on screen
- Overlay windows: To display hint labels for element selection

**Privacy & Security:**
- Does NOT collect or transmit user data
- Does NOT log keystrokes
- All processing is local
- Open source for transparency
- Code signed with EV certificate (DigiCert)

**Evidence:**
- GitHub repository: [link]
- Code signing certificate: Verified by DigiCert
- Privacy policy: [link]
- Microsoft false positive cleared: [if applicable]

We would greatly appreciate if you could review and whitelist our software.
Please let me know if you need any additional information.

Best regards,
[Your Name]
[Your Title]
[Contact Information]
```

### 5.3 VirusTotal扫描与信誉

#### VirusTotal提交策略

**公开提交 vs 私密提交**

| 方式 | 优点 | 缺点 | 适用场景 |
|-----|------|------|---------|
| **公开提交** | - 免费<br>- 70+引擎扫描<br>- 社区评论 | - 文件公开（竞争对手可下载） | 开源项目 |
| **私密提交** | - 文件不公开<br>- API访问 | - 需付费($200+/月) | 商业软件 |

**使用VirusTotal**：
```bash
# 1. 上传文件到VirusTotal
# 网址: https://www.virustotal.com/gui/home/upload

# 2. 查看扫描结果
# 目标: 0/70+ 检出率

# 3. 如果有误报，点击"Request reanalysis"
# 或联系对应杀毒软件厂商

# 4. 在官网展示扫描结果
# 示例: "VirusTotal: 0/72 detections ✅"
```

**API自动化扫描**（持续集成）
```python
# virustotal_check.py
import requests
import time

def scan_file(file_path, api_key):
    """提交文件到VirusTotal扫描"""
    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": api_key}

    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        scan_id = response.json()["data"]["id"]
        print(f"Scan submitted: {scan_id}")
        return scan_id
    else:
        raise Exception(f"Upload failed: {response.text}")

def get_scan_result(scan_id, api_key):
    """获取扫描结果"""
    url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
    headers = {"x-apikey": api_key}

    # 等待扫描完成
    while True:
        response = requests.get(url, headers=headers)
        result = response.json()

        status = result["data"]["attributes"]["status"]
        if status == "completed":
            stats = result["data"]["attributes"]["stats"]
            print(f"Scan completed: {stats}")
            return stats
        else:
            print(f"Status: {status}, waiting...")
            time.sleep(30)

# 使用
api_key = "YOUR_API_KEY"
scan_id = scan_file("dist/HEMouse.exe", api_key)
stats = get_scan_result(scan_id, api_key)

# 检查结果
if stats["malicious"] > 0:
    print("❌ Detected as malicious by some engines")
    exit(1)
else:
    print("✅ Clean scan, 0 detections")
```

### 5.4 SmartScreen信誉累积

#### SmartScreen工作原理

```
新文件发布 → SmartScreen无信誉 → "未知发布者"警告
             ↓
         用户下载
             ↓
         签名验证 → EV证书 → 立即信誉 ✅
         或         标准证书 → 需累积信誉
             ↓
         下载量 > 阈值（~1000）→ 信誉建立 → 无警告
```

#### 加速信誉累积策略

**1. 使用EV证书**（最有效）
- 首次发布即绕过警告
- 投入：$300-500/年

**2. 增加下载量**
- GitHub发布：吸引开发者
- 技术博客：分享使用案例
- 社交媒体：Reddit、HackerNews推广
- 目标：前1000次下载容忍警告

**3. 多渠道分发**
```
官方网站下载
  ↓
GitHub Releases
  ↓
Microsoft Store（如果可行）
  ↓
Chocolatey/Scoop（包管理器）
```

---

## 6. Layer 4: 行为透明化

### 6.1 首次运行授权提示

#### 权限申请界面设计

```python
# permission_dialog.py
import tkinter as tk
from tkinter import messagebox

class PermissionDialog:
    def show_permission_request(self):
        """显示权限申请对话框"""
        root = tk.Tk()
        root.withdraw()

        message = """
HEMouse需要以下权限才能正常工作：

✅ 键盘输入监控
   用途：检测CapsLock和标签键（a-z）
   范围：仅在Hint模式激活时
   保证：不记录或上传键盘输入

✅ UI元素访问
   用途：检测屏幕上的可点击元素
   范围：仅当前用户的窗口
   保证：不访问敏感信息（密码框除外）

✅ 创建遮罩窗口
   用途：显示提示标签
   范围：临时全屏透明窗口
   保证：不拦截鼠标点击（可穿透）

是否授予权限？

隐私声明: https://hemouse.example.com/privacy
开源代码: https://github.com/manshall/hemouse
        """

        result = messagebox.askokcancel(
            "HEMouse权限申请",
            message,
            icon="info"
        )

        root.destroy()
        return result

# 使用
if not PermissionDialog().show_permission_request():
    print("用户拒绝权限，退出程序")
    exit(0)
```

### 6.2 隐私政策（PRIVACY.md）

```markdown
# HEMouse隐私政策

最后更新：2025-09-30

## 数据收集

**HEMouse不收集任何用户数据**，包括但不限于：
- ❌ 键盘输入记录
- ❌ 鼠标轨迹
- ❌ 访问的网站或应用程序
- ❌ 个人身份信息
- ❌ 系统信息或设备标识

## 数据处理

HEMouse的所有处理都在**本地设备**上进行：
- ✅ 键盘输入仅用于检测标签键（a-z），立即处理后丢弃
- ✅ UI元素检测仅在内存中进行，不持久化
- ✅ 配置文件仅存储用户偏好设置（如快捷键绑定）

## 网络通信

HEMouse默认**不连接互联网**，除非：
- 检查更新（可选，用户可禁用）
- 访问GitHub仓库（仅下载更新时）

更新检查仅发送：
- 当前版本号
- 操作系统类型（Windows 10/11）

**不发送**：用户ID、使用统计、个人信息

## 第三方服务

HEMouse不使用任何第三方分析或广告服务。

## 开源审计

HEMouse是开源软件，任何人都可以审计代码：
https://github.com/manshall/hemouse

## 联系我们

如有隐私问题，请联系：privacy@hemouse.example.com
```

### 6.3 实时行为日志（可选）

```python
# behavior_logger.py
import logging
from datetime import datetime

class TransparentLogger:
    def __init__(self, log_dir="logs"):
        self.logger = logging.getLogger("HEMouse")
        self.logger.setLevel(logging.INFO)

        # 文件日志（仅本地，不上传）
        handler = logging.FileHandler(f"{log_dir}/hemouse.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_mode_change(self, from_mode, to_mode):
        """记录模式切换（不敏感）"""
        self.logger.info(f"Mode changed: {from_mode} → {to_mode}")

    def log_hook_install(self):
        """记录钩子安装"""
        self.logger.info("Keyboard hook installed")

    def log_hook_uninstall(self):
        """记录钩子卸载"""
        self.logger.info("Keyboard hook uninstalled")

    def log_element_click(self, element_type):
        """记录元素点击（不记录具体内容）"""
        # ✅ 记录类型：Button, Link, TextBox
        self.logger.info(f"Element clicked: {element_type}")

        # ❌ 不记录：具体文本、URL、输入内容

# 用户可查看日志
# 提供"打开日志文件夹"按钮
```

### 6.4 托盘图标状态指示

```python
# tray_icon.py
import pystray
from PIL import Image, ImageDraw

class HEMouseTrayIcon:
    def create_icon(self, status="idle"):
        """创建状态图标"""
        # 不同状态用不同颜色
        colors = {
            "idle": "gray",      # 空闲：灰色
            "hint": "green",     # Hint模式：绿色
            "grid": "blue",      # Grid模式：蓝色
            "normal": "orange"   # Normal模式：橙色
        }

        color = colors.get(status, "gray")
        image = self._draw_icon(color)
        return image

    def _draw_icon(self, color):
        """绘制图标"""
        img = Image.new('RGB', (64, 64), color="white")
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 8, 56, 56], fill=color)
        return img

    def show_tray_icon(self):
        """显示托盘图标"""
        icon = pystray.Icon(
            "HEMouse",
            self.create_icon("idle"),
            "HEMouse - Idle",
            menu=pystray.Menu(
                pystray.MenuItem("打开设置", self.open_settings),
                pystray.MenuItem("查看日志", self.open_logs),
                pystray.MenuItem("隐私政策", self.open_privacy_policy),
                pystray.MenuItem("退出", self.quit)
            )
        )
        icon.run()

# 透明化：用户随时知道HEMouse的状态
```

---

## 7. 企业环境部署策略

### 7.1 企业IT部门的顾虑

**典型拒绝理由**：
1. 未知发布者，无代码签名
2. 使用敏感API（键盘钩子）
3. 缺乏安全审计报告
4. 不符合企业安全策略

### 7.2 企业部署包（MSI）

```bash
# 使用WiX Toolset创建MSI安装包

# 1. 定义产品（Product.wxs）
<?xml version="1.0"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*"
           Name="HEMouse"
           Version="1.0.0"
           Manufacturer="Manshall Technology Co."
           Language="1033"
           UpgradeCode="YOUR-GUID">

    <Package InstallerVersion="200"
             Compressed="yes"
             InstallScope="perUser" />  <!-- 用户级安装，不需要管理员权限 -->

    <Media Id="1" Cabinet="hemouse.cab" EmbedCab="yes" />

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="LocalAppDataFolder">
        <Directory Id="INSTALLFOLDER" Name="HEMouse">
          <Component Id="MainExecutable" Guid="YOUR-GUID">
            <File Id="HEMouseExe"
                  Source="hemouse.exe"
                  KeyPath="yes" />
          </Component>
        </Directory>
      </Directory>
    </Directory>

    <Feature Id="Complete" Level="1">
      <ComponentRef Id="MainExecutable" />
    </Feature>

    <!-- 数字签名 -->
    <SignTool Id="signtool"
              Name="signtool.exe"
              Arguments="/n 'Manshall Technology Co.' /fd SHA256 /tr http://timestamp.digicert.com /td SHA256" />

  </Product>
</Wix>

# 2. 编译MSI
candle Product.wxs
light Product.wixobj -out HEMouse-1.0.0.msi

# 3. 签名MSI
signtool sign /n "Manshall Technology Co." /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 HEMouse-1.0.0.msi
```

### 7.3 安全白皮书（for IT决策者）

```markdown
# HEMouse安全白皮书

**版本**: 1.0.0
**发布日期**: 2025-09-30
**目标读者**: 企业IT管理员、安全团队

## 执行摘要

HEMouse是一款开源的无障碍辅助工具，使用键盘和头部动作替代鼠标操作。
本文档详细说明HEMouse的安全架构、隐私保护措施和企业部署建议。

## 技术架构

### 权限需求
- ✅ 用户级键盘钩子（WH_KEYBOARD_LL）
- ✅ Windows UIA API访问
- ❌ 不需要管理员权限
- ❌ 不需要内核驱动

### 数据处理
- 所有处理在本地进行
- 不持久化敏感数据
- 不连接外部服务器（除更新检查）

## 安全措施

### 代码签名
- EV代码签名证书（DigiCert）
- SHA256哈希算法
- 时间戳签名（证书过期后仍可验证）

### 开源审计
- GitHub公开源代码
- 社区审计和贡献
- 透明的开发流程

### 隐私保护
- 遵守GDPR和CCPA
- 不收集用户数据
- 详细隐私政策

## 企业部署

### 部署方式
1. MSI安装包（Group Policy推送）
2. 用户级安装（不需要管理员权限）
3. 静默安装支持：`msiexec /i HEMouse.msi /quiet`

### 配置管理
- 注册表配置：`HKCU\Software\HEMouse`
- 可通过GPO统一配置
- 支持企业默认设置

### 监控和日志
- 本地日志文件（可配置路径）
- 支持集中日志收集（Syslog）
- 无远程遥测

## 合规性

### 标准符合
- ✅ WCAG 2.1无障碍标准
- ✅ Windows应用认证要求
- ✅ GDPR数据保护要求

### 安全认证
- Microsoft Defender白名单
- VirusTotal扫描报告（0检出）
- 第三方杀毒软件兼容性测试

## 支持和维护

### 更新机制
- 自动更新检查（可禁用）
- 手动下载安装包
- 企业内网镜像支持

### 技术支持
- 企业支持：enterprise@hemouse.example.com
- 响应时间：24小时内响应，72小时内解决
- 专业服务：安全审计、定制开发

## 风险评估

### 低风险
- 用户级权限，攻击面小
- 开源透明，可审计
- 活跃维护，快速修复漏洞

### 缓解措施
- 定期安全审计
- 漏洞披露计划
- 快速补丁发布流程

## 推荐部署策略

1. **试点部署**（1-2周）
   - IT部门内部测试
   - 10-20名用户试用
   - 收集反馈和监控日志

2. **小规模推广**（1个月）
   - 特定部门部署（如开发团队）
   - 验证兼容性和稳定性

3. **全面推广**
   - 通过Group Policy推送
   - 提供培训和文档
   - 建立支持渠道

## 联系信息

- 安全问题：security@hemouse.example.com
- 企业咨询：enterprise@hemouse.example.com
- GitHub Issues：https://github.com/manshall/hemouse/issues
```

---

## 8. 持续监控与响应

### 8.1 监控策略

```python
# security_monitor.py
import requests
import time
from datetime import datetime

class SecurityMonitor:
    def __init__(self):
        self.virustotal_api_key = "YOUR_API_KEY"
        self.notification_email = "security@hemouse.example.com"

    def daily_virustotal_check(self, file_hash):
        """每日检查VirusTotal状态"""
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {"x-apikey": self.virustotal_api_key}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            stats = response.json()["data"]["attributes"]["last_analysis_stats"]

            if stats["malicious"] > 0:
                self._alert(f"⚠️ New detection: {stats['malicious']} engines")

    def monitor_smartscreen_reputation(self):
        """监控SmartScreen信誉"""
        # 通过下载统计、用户反馈等间接监控
        pass

    def _alert(self, message):
        """发送警报"""
        print(f"[{datetime.now()}] {message}")
        # 发送邮件或Slack通知

# 部署到CI/CD
monitor = SecurityMonitor()
monitor.daily_virustotal_check("YOUR_FILE_SHA256")
```

### 8.2 漏洞响应流程

```yaml
漏洞发现:
  - 用户报告
  - 安全研究员披露
  - 自动扫描检测

响应流程:
  1. 确认漏洞（24小时内）
  2. 评估风险等级
  3. 开发补丁（Critical: 48h, High: 7d, Medium: 30d）
  4. 内部测试
  5. 发布安全更新
  6. 公开披露（修复后）

通知渠道:
  - GitHub Security Advisory
  - 官网公告
  - 邮件通知（企业用户）
  - 社交媒体
```

---

## 9. 最佳实践检查清单

### 9.1 发布前检查清单

```markdown
## 代码层面
- [ ] 使用最小权限API（用户级钩子）
- [ ] 不存储敏感数据
- [ ] 代码开源（GitHub公开）
- [ ] 通过静态代码分析（无高危漏洞）
- [ ] 移除调试代码和后门

## 签名与认证
- [ ] EV代码签名证书
- [ ] 签名所有可执行文件（.exe, .dll, .msi）
- [ ] 添加时间戳签名
- [ ] 验证签名有效性

## 安全扫描
- [ ] VirusTotal扫描（0检出）
- [ ] 提交Microsoft Defender（无误报）
- [ ] 主流杀毒软件测试（Kaspersky, Norton, etc.）

## 文档与透明化
- [ ] 隐私政策（PRIVACY.md）
- [ ] 安全声明（SECURITY.md）
- [ ] 首次运行权限提示
- [ ] 企业安全白皮书

## 部署
- [ ] MSI安装包（签名）
- [ ] 自动更新机制（可禁用）
- [ ] 日志和监控

## 持续监控
- [ ] 每日VirusTotal检查
- [ ] SmartScreen信誉监控
- [ ] 用户反馈收集
```

### 9.2 常见错误与避免

| 错误 | 后果 | 正确做法 |
|-----|------|---------|
| **不签名** | SmartScreen警告，70%用户流失 | 购买EV证书 |
| **代码混淆** | 增加可疑度，误报率↑ | 开源透明 |
| **使用内核驱动** | 极高风险，杀毒软件必拦 | 用户级钩子 |
| **存储键盘记录** | 被定性为恶意软件 | 立即处理后丢弃 |
| **无隐私政策** | 信任度低，企业拒绝 | 详细隐私声明 |
| **不响应误报** | 持续被拦截 | 主动申诉白名单 |

---

## 10. 总结与建议

### 10.1 关键措施优先级

| 优先级 | 措施 | 成本 | 效果 | 实施难度 |
|-------|------|------|------|---------|
| 🔴 P0 | EV代码签名证书 | $300-500/年 | 极高 | 低 |
| 🔴 P0 | 开源代码（GitHub） | 免费 | 高 | 低 |
| 🟡 P1 | Microsoft Defender申诉 | 免费 | 高 | 中 |
| 🟡 P1 | 隐私政策+安全文档 | 免费 | 中 | 低 |
| 🟢 P2 | 第三方杀毒软件申诉 | 免费 | 中 | 中 |
| 🟢 P2 | VirusTotal持续监控 | $0-200/月 | 中 | 低 |

### 10.2 实施路线图

**Phase 1: MVP（1-2周）**
- ✅ 代码开源（GitHub）
- ✅ 基础安全实现（用户级API）
- ✅ 隐私政策文档

**Phase 2: 正式发布（4-6周）**
- 📦 购买EV证书
- 🔏 签名所有文件
- 📝 提交Microsoft Defender
- 📊 VirusTotal扫描

**Phase 3: 生态建设（3-6个月）**
- 🏢 企业安全白皮书
- 🛡️ 第三方杀毒软件白名单
- 📈 SmartScreen信誉累积
- 🔄 持续监控与响应

### 10.3 预期效果

**实施完整方案后**：
- ✅ 误报率降低至<5%
- ✅ SmartScreen无警告（EV证书）
- ✅ 主流杀毒软件兼容
- ✅ 企业IT部门接受度↑
- ✅ 用户信任度↑，下载完成率>90%

---

**文档版本**：v1.0
**创建日期**：2025-09-30
**状态**：✅ Ready for Implementation

**下一步行动**：
1. 开始申请EV代码签名证书（DigiCert推荐）
2. 完善GitHub仓库（添加SECURITY.md, PRIVACY.md）
3. 准备Microsoft Defender提交材料