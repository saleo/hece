# 🚀 快速开始指南

**5分钟开始使用目光追踪MVP**

---

## ⚡ 极速启动（3步）

### 1️⃣ 安装依赖（1分钟）

```bash
# Windows PowerShell
cd gaze_tracking_mvp
pip install -r requirements.txt
```

### 2️⃣ 校准屏幕（2分钟）

```bash
python gaze_tracker_standalone.py --calibrate
```

**操作说明**：
1. 看向**主屏幕中心**，按Enter，保持5秒
2. 看向**副屏中心**，按Enter，保持5秒
3. 完成！

### 3️⃣ 开始使用（立即）

```bash
python gaze_tracker_standalone.py --run
```

转动头部看向不同屏幕，窗口会自动激活！

---

## 📝 完整流程

### 步骤1：环境检查

**检查Python版本**：
```bash
python --version  # 应该 >= 3.8
```

**检查摄像头**：
- 打开相机应用验证摄像头工作
- 确保没有其他程序占用摄像头

**检查屏幕配置**：
- 确认主屏和副屏已正确配置
- Windows设置 → 系统 → 显示 → 多显示器

### 步骤2：安装

**方法A：使用虚拟环境（推荐）**
```bash
# 创建虚拟环境
python -m venv venv_gaze

# 激活虚拟环境
venv_gaze\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

**方法B：全局安装**
```bash
pip install -r requirements.txt
```

**验证安装**：
```bash
python -c "import cv2, mediapipe, numpy; print('✅ All modules imported successfully')"
```

### 步骤3：初次测试（可选但推荐）

**测试摄像头和姿态检测**：
```bash
python gaze_tracker_standalone.py --test
```

这会打开一个窗口显示：
- 你的视频画面
- 实时Yaw角度
- 方向指示

转动头部观察角度变化。按 **'q'** 退出。

### 步骤4：校准

**启动校准**：
```bash
python gaze_tracker_standalone.py --calibrate
```

**校准主屏**：
```
📍 Calibrating PRIMARY...
   Please look at the primary screen
   Keep your head still and look at the center
   Calibration will last 5 seconds

   Collecting samples..........  Done!

✅ PRIMARY calibrated successfully!
   Yaw range: -8.5° ~ 7.2°
   Yaw mean: -0.3° (±3.1°)
   Samples: 52
```

**校准副屏**：
- 转动头部看向副屏
- 按Enter开始
- 保持5秒

**校准技巧**：
- ✅ 保持头部稳定，看屏幕中心
- ✅ 光线充足，正对摄像头
- ✅ 距离摄像头30-80cm
- ❌ 不要频繁转动头部
- ❌ 不要遮挡面部

### 步骤5：查看配置

```bash
python gaze_tracker_standalone.py --info
```

输出示例：
```
📺 Screen Layout
==================================================

🖥️  Primary Screen:
   Position: (0, 0)
   Size: 1920x1080

🖥️  Secondary Screen 0:
   Position: (1920, 0)
   Size: 1920x1080
   Relative: Right of primary

Total: 2 screen(s)
==================================================

🎯 Calibration Info
==================================================

📍 PRIMARY:
   Yaw range: -8.5° ~ 7.2°
   Yaw mean: -0.3° (±3.1°)
   Threshold: -15.3° ~ 14.7°
   Samples: 52

📍 SECONDARY_0:
   Yaw range: 32.1° ~ 48.7°
   Yaw mean: 40.2° (±3.5°)
   Threshold: 25.2° ~ 55.2°
   Samples: 48
==================================================
```

### 步骤6：运行追踪

```bash
python gaze_tracker_standalone.py --run
```

**使用说明**：
- 🎯 转头看向不同屏幕
- 🪟 对应屏幕窗口自动激活
- ⏸️ Ctrl+C 停止

**运行示例**：
```
🚀 Run Mode - Gaze Tracking Active
==================================================
✅ Tracking Active
==================================================

📖 Instructions:
   - Move your head to look at different screens
   - Windows on the target screen will be auto-activated
   - Press Ctrl+C to stop

🎯 Switched to PRIMARY
🎯 Switched to SECONDARY_0
🎯 Switched to PRIMARY

📊 Stats: 542 frames, 3 switches, 23.8 FPS
...
```

**停止后统计**：
```
📊 Gaze Tracker Statistics
==================================================
Tracking Status: 🔴 Stopped
Duration: 45.2s
Frames processed: 1076
Processing FPS: 23.8
Screen switches: 8

📷 Camera:
   Captured: 1125
   Dropped: 49 (4.4%)

🎯 Pose Estimation:
   Total: 1076
   Detected: 1038
   Detection rate: 96.5%

🪟 Window Activation:
   Attempts: 8
   Successful: 8
   Failed: 0
   Success rate: 100.0%
==================================================
```

---

## 🎯 使用场景示例

### 场景1：编程 + 文档

```
主屏：VSCode编辑器
副屏：浏览器文档

操作：
1. 看主屏写代码 → VSCode自动激活
2. 看副屏查文档 → 浏览器自动激活
3. 无需手动切换！
```

### 场景2：数据分析

```
主屏：Excel数据表
副屏：PowerBI报表

操作：
转头切换，鼠标和键盘立即可用
```

### 场景3：多任务工作

```
主屏：主要工作窗口
副屏：通讯工具（微信/钉钉）

快速看一眼副屏回复消息，立即切回主屏
```

---

## ⚠️ 常见问题速查

### Q1: 摄像头打不开？
```bash
# 检查摄像头是否被占用
# 关闭所有可能使用摄像头的程序（Teams、Zoom等）

# 尝试不同的摄像头ID
# 修改 camera_manager.py 中的 camera_id=0 改为 1 或 2
```

### Q2: 检测不到面部？
- ✅ 增加光线
- ✅ 调整摄像头角度
- ✅ 距离30-80cm
- ✅ 避免背光

### Q3: 窗口激活失败？
```bash
# 大部分情况Alt键workaround会成功
# 如果持续失败，以管理员权限运行：
# 右键 PowerShell → 以管理员身份运行
python gaze_tracker_standalone.py --run
```

### Q4: 频繁误切换？
```bash
# 重新校准，提高质量：
python gaze_tracker_standalone.py --calibrate

# 或调整防抖动参数（高级）
# 编辑 modules/gaze_tracker.py
# 修改 self.buffer_size = 5  改为  7 或 10
```

### Q5: 准确率不理想？
**检查清单**：
- [ ] 校准时保持头部稳定
- [ ] 光线充足
- [ ] 摄像头清晰可见面部
- [ ] 屏幕位置相对固定
- [ ] 重新校准尝试

---

## 📊 性能调优

### 降低CPU占用

编辑 `modules/camera_manager.py`:
```python
# 原始：
self.camera = CameraManager(resolution=(320, 240), fps=30)

# 优化：
self.camera = CameraManager(resolution=(320, 240), fps=20)  # 降低帧率
```

### 提高准确率

编辑 `modules/gaze_tracker.py`:
```python
# 原始：
self.buffer_size = 5  # 5帧一致才切换

# 更严格（减少误判，但延迟增加）：
self.buffer_size = 7  # 7帧一致才切换
```

### 调整灵敏度

编辑 `modules/screen_calibrator.py`:
```python
# 原始：
buffer = 15  # 度数缓冲区

# 更宽松（更容易触发切换）：
buffer = 10

# 更严格（减少误判）：
buffer = 20
```

---

## 🧪 测试建议

### 基础功能测试（10分钟）

1. **摄像头测试**（2分钟）
   ```bash
   python modules/camera_manager.py
   # 应该看到视频窗口，按'q'退出
   ```

2. **姿态检测测试**（3分钟）
   ```bash
   python modules/pose_estimator.py
   # 转动头部，观察Yaw角度变化
   ```

3. **窗口激活测试**（2分钟）
   ```bash
   python modules/window_activator.py
   # 测试Alt键workaround
   ```

4. **完整流程测试**（3分钟）
   - 校准
   - 测试模式验证
   - 运行模式测试

### 准确率测试（15分钟）

执行20次切换，记录：
```
主屏 → 副屏: __/10 成功
副屏 → 主屏: __/10 成功
总准确率: ___%
```

**目标**：≥85%

### 长时间稳定性测试（30分钟）

连续运行30分钟，记录：
- 总切换次数
- 成功切换
- 失败切换
- 误切换
- 是否崩溃

---

## 📝 反馈模板

完成测试后，请记录：

```
【环境信息】
- Windows版本: ___
- Python版本: ___
- 摄像头: ___
- 屏幕配置: ___

【性能数据】
- 准确率: ___%
- 平均延迟: ___ ms
- CPU占用: ___%
- 检测率: ___%

【使用体验】
最满意: ___
最不满意: ___
遇到的问题: ___
改进建议: ___

【继续集成？】
□ 是，值得集成到HEMouse
□ 否，需要改进
□ 保持独立工具
```

---

## 🎓 进阶使用

### 多屏支持（3+屏幕）

如果有3个或更多屏幕：
```bash
# 校准时会提示校准 secondary_0, secondary_1, secondary_2...
python gaze_tracker_standalone.py --calibrate
```

### 重新校准单个屏幕

删除配置文件重新开始：
```bash
# 删除校准数据
del config\gaze_config.json

# 重新校准
python gaze_tracker_standalone.py --calibrate
```

### 调试模式

在测试模式下可以看到详细信息：
```bash
python gaze_tracker_standalone.py --test
```

---

## ✅ 下一步

完成Phase 1测试后：

**如果成功（准确率≥85%）**：
- 📝 填写反馈模板
- 📊 整理测试数据
- 💬 讨论Phase 2集成方案

**如果需要改进**：
- 🔧 调优参数
- 📸 改善校准流程
- 💡 考虑其他方案

---

**祝使用愉快！**🎉
