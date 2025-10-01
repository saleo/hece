# 🎯 Gaze Tracking MVP - Phase 1

**双屏目光追踪窗口自动激活 - 独立测试程序**

## 📋 项目概述

这是HEMouse目光追踪功能的**阶段1独立MVP**，用于验证核心技术可行性。

### 核心功能

- ✅ **头部姿态检测** - 使用MediaPipe实时检测头部方向
- ✅ **屏幕校准** - 为每个屏幕校准Yaw角度范围
- ✅ **窗口自动激活** - 根据目光方向自动激活对应屏幕的窗口
- ✅ **防抖动机制** - 避免频繁误切换
- ✅ **实时可视化** - 测试模式显示实时Yaw角度

### 技术栈

- **MediaPipe Face Mesh** - 面部特征点检测
- **OpenCV** - 图像处理和姿态计算
- **PyWin32** - Windows API窗口控制
- **Pynput** - 键盘模拟（Alt键workaround）
- **screeninfo** - 屏幕信息检测

---

## 🚀 快速开始

### 1. 环境准备

**前提条件**:
- Python 3.8+
- Windows 10/11
- 内置摄像头或USB摄像头
- 至少2个显示器（推荐）

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv_gaze
venv_gaze\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**依赖库**:
- opencv-python==4.8.1
- mediapipe==0.10.9
- numpy==1.24.3
- screeninfo==0.8.1
- pynput==1.7.6
- pywin32>=305

### 3. 校准屏幕

**首次使用必须先校准！**

```bash
python gaze_tracker_standalone.py --calibrate
```

**校准流程**:
1. 看向主屏幕，保持5秒
2. 看向副屏，保持5秒
3. 校准数据自动保存到 `config/gaze_config.json`

**校准提示**:
- 📌 保持头部相对稳定，主要转动头部而非眼球
- 📌 看向屏幕中心位置
- 📌 确保摄像头能清晰看到您的面部
- 📌 光线充足，避免背光

### 4. 测试模式（推荐）

在实际使用前，先用测试模式验证：

```bash
python gaze_tracker_standalone.py --test
```

这会打开一个窗口显示：
- 实时Yaw角度（Raw和Smoothed）
- 校准阈值范围
- 当前目标屏幕
- 方向指示（LEFT/CENTER/RIGHT）

按 **'q'** 退出测试窗口。

### 5. 运行追踪

```bash
python gaze_tracker_standalone.py --run
```

**使用说明**:
- 🎯 转动头部看向不同屏幕
- 🪟 对应屏幕的顶层窗口会自动激活
- ⏸️ 按 **Ctrl+C** 停止追踪
- 📊 停止后会显示统计信息

---

## 📖 使用指南

### 命令参数

| 命令 | 说明 |
|------|------|
| `--calibrate` | 校准模式 - 为屏幕校准Yaw角度范围 |
| `--run` | 运行模式 - 启动目光追踪和窗口激活 |
| `--test` | 测试模式 - 可视化显示Yaw角度（不激活窗口） |
| `--info` | 信息模式 - 显示屏幕布局和校准状态 |
| `--config PATH` | 指定配置文件路径（默认: config/gaze_config.json） |

### 工作原理

```
摄像头帧 → 面部检测 → 姿态估计 → Yaw角度
                                    ↓
                              屏幕判断 → 防抖动 → 窗口激活
                                    ↑
                              校准数据
```

**关键技术点**:

1. **MediaPipe姿态检测**
   - 提取6个面部关键点
   - 使用solvePnP计算3D姿态
   - 得到Yaw/Pitch/Roll角度

2. **Kalman滤波平滑**
   - 平滑Yaw角度，减少抖动
   - 预测和校正机制

3. **防抖动缓冲**
   - 需要连续5帧一致才切换屏幕
   - 约200ms延迟，避免误判

4. **Alt键Workaround**
   - 绕过Windows前台窗口激活限制
   - 模拟Alt键按下/释放

---

## 🔧 模块说明

### 项目结构

```
gaze_tracking_mvp/
├── modules/
│   ├── camera_manager.py      # 摄像头管理（后台线程）
│   ├── pose_estimator.py       # 姿态检测（MediaPipe）
│   ├── screen_calibrator.py    # 屏幕校准和配置
│   ├── window_activator.py     # 窗口激活（Alt workaround）
│   └── gaze_tracker.py         # 主控制器
├── config/
│   └── gaze_config.json        # 校准数据（自动生成）
├── requirements.txt            # 依赖列表
├── gaze_tracker_standalone.py  # 主程序
└── README.md                   # 本文档
```

### 核心模块

#### CameraManager
- 后台线程采集摄像头帧
- 非阻塞队列（容量1，自动丢弃旧帧）
- 可配置分辨率和帧率
- 统计信息（采集帧数、丢帧率）

#### PoseEstimator
- MediaPipe Face Mesh面部检测
- OpenCV solvePnP姿态计算
- Kalman滤波平滑Yaw角度
- 检测率统计

#### ScreenCalibrator
- 自动检测屏幕布局
- 校准Yaw角度范围
- 目标屏幕判断逻辑
- JSON配置持久化

#### WindowActivator
- 枚举屏幕窗口
- Alt键workaround激活
- 防重复激活
- 成功率统计

#### GazeTracker
- 整合所有模块
- 后台追踪线程
- 防抖动缓冲
- 完整统计信息

---

## 📊 性能指标

### 预期性能

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **延迟** | 50-80ms | 检测到窗口激活的总延迟 |
| **帧率** | 15-25 FPS | 姿态检测处理频率 |
| **CPU占用** | 5-10% | 单核CPU占用率 |
| **内存占用** | ~200 MB | 包含所有依赖库 |
| **准确率** | 85-90% | 校准后的屏幕判断准确率 |

### 实际测试

运行测试后查看统计信息：

```bash
python gaze_tracker_standalone.py --run
# ... 使用一段时间后按 Ctrl+C

# 输出示例：
📊 Gaze Tracker Statistics
==================================================
Tracking Status: 🔴 Stopped
Duration: 120.5s
Frames processed: 2890
Processing FPS: 24.0
Screen switches: 15

📷 Camera:
   Captured: 3125
   Dropped: 235 (7.5%)

🎯 Pose Estimation:
   Total: 2890
   Detected: 2758
   Detection rate: 95.4%

🪟 Window Activation:
   Attempts: 15
   Successful: 14
   Failed: 1
   Success rate: 93.3%
==================================================
```

---

## 🐛 故障排除

### 常见问题

#### 1. 摄像头无法打开
```
❌ Failed to open camera 0
```

**解决方案**:
- 检查摄像头是否被其他程序占用
- 尝试不同的camera_id（如果有多个摄像头）
- 检查摄像头权限设置

#### 2. 未检测到面部
```
No face detected
```

**解决方案**:
- 确保光线充足
- 调整摄像头角度
- 距离摄像头保持30-80cm
- 避免强烈背光

#### 3. 窗口激活失败
```
⚠️ Failed to activate: ...
```

**解决方案**:
- 大部分情况下Alt键workaround会成功
- 如果持续失败，尝试以管理员权限运行
- 某些全屏应用可能无法激活

#### 4. 频繁误切换

**解决方案**:
- 重新校准屏幕（提高样本质量）
- 增加防抖动缓冲大小（修改gaze_tracker.py中的buffer_size）
- 调整校准时的头部稳定性

#### 5. MediaPipe导入错误
```
ImportError: No module named 'mediapipe'
```

**解决方案**:
```bash
pip install --upgrade mediapipe
# 如果失败，尝试指定版本
pip install mediapipe==0.10.9
```

---

## 🧪 测试检查清单

### 阶段1评估标准

运行完整测试并记录以下数据：

- [ ] **安装成功** - 所有依赖安装无错误
- [ ] **摄像头工作** - 能正常采集视频帧
- [ ] **姿态检测工作** - 能显示Yaw角度
- [ ] **校准完成** - 主屏和副屏都成功校准
- [ ] **窗口激活成功** - Alt键workaround能激活窗口
- [ ] **准确率测试** - 记录误判次数和准确率
- [ ] **延迟测试** - 感受切换延迟是否可接受
- [ ] **CPU占用** - 查看任务管理器CPU占用率
- [ ] **使用体验** - 实际使用场景下的体验评分

### 性能测试

**准确率测试**（20次切换）:
```
主屏 → 副屏: __/10 成功
副屏 → 主屏: __/10 成功
准确率: ___%
```

**延迟测试**:
```
头部转向到窗口激活：约 ___ 毫秒
主观感受：□ 流畅  □ 可接受  □ 明显延迟
```

**稳定性测试**（30分钟连续使用）:
```
总切换次数: ___
成功切换: ___
失败切换: ___
误切换: ___
崩溃次数: ___
```

---

## 📝 数据收集

### 请记录以下信息

**环境信息**:
- 系统: Windows __
- Python版本: __
- 摄像头型号: __
- 屏幕配置: 主屏__寸 + 副屏__寸
- 屏幕相对位置: □ 水平 □ 垂直 □ 其他

**校准数据**:
```
主屏 Yaw范围: __ ~ __ 度
副屏 Yaw范围: __ ~ __ 度
```

**使用反馈**:
1. 最满意的地方: ________________
2. 最不满意的地方: ________________
3. 遇到的问题: ________________
4. 改进建议: ________________
5. 是否值得继续集成到HEMouse: □ 是 □ 否

---

## 🎯 下一步

### 如果阶段1成功（准确率≥85%）

继续 **阶段2: 模块化集成**
- 集成到HEMouse主程序
- 添加GAZE_TRACKING模式
- 热键切换支持
- 托盘图标控制

### 如果阶段1不理想（准确率<85%）

**调优方向**:
1. 增加校准样本数量
2. 调整防抖动参数
3. 优化Kalman滤波参数
4. 考虑添加眼球追踪辅助

**或考虑**:
- 保持为独立工具（不集成）
- 重新评估技术方案

---

## 📚 参考资源

**技术文档**:
- [MediaPipe Face Mesh](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)
- [OpenCV solvePnP](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga549c2075fac14829ff4a58bc931c033d)
- [Windows SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)

**相关论文**:
- "Combining head pose and eye location for gaze estimation" (2011)
- "Webcam-based gaze estimation for computer screen interaction" (2024)

---

## 📄 许可证

本项目是HEMouse的一部分，遵循HEMouse项目的许可证。

---

## 🙋 反馈

如有问题或建议，请：
1. 记录在测试检查清单中
2. 与HEMouse项目维护者讨论
3. 决定是否继续阶段2集成

---

**版本**: MVP Phase 1
**日期**: 2025-10-01
**状态**: 实验性测试版本
