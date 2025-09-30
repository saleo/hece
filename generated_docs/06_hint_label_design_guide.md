# Hint模式标签设计指南
**解决高密度UI下的标签可读性与选择性问题**

---

## 🎯 核心挑战

在Hint模式下，如何在**密集UI**中生成清晰、易选、不重叠的标签？

**关键问题**:
1. 标签太小 → 看不清
2. 标签太密 → 互相遮挡
3. 标签太多 → 选择困难
4. 标签生成算法 → 前缀冲突

---

## 📚 业界调研发现

### **Vimium的做法与问题**

#### **标签生成算法**
```
单字母: a-z (26个元素)
双字母: aa, ab, ac, ..., zz (676个元素)
三字母: aaa, aab, ... (17576个元素)
```

#### **已知问题**

**1. 前缀冲突问题** (Kitty终端bug)
```
错误示例:
标签: j, ja, jb, jc
问题: 输入'j'时系统等待判断是'j'还是'ja/jb/jc'
结果: 'j'标签无法选择
```

**2. 重叠处理** (手动而非自动)
```
Vimium策略: 按Space键旋转堆叠顺序
缺点:
- 需要额外操作
- 认知负担增加
- 不够智能
```

**3. Z-index问题**
```
Vimium不保证标签总在最上层
解决: Popover元素(新浏览器支持)
```

---

### **Vimium-C的优化**

#### **交替手指优化**
```
灵感来自luakit:
- 奇数位: 左手字母 (asdf)
- 偶数位: 右手字母 (jkl;)
- 目的: 提高输入速度

示例:
aj, ak, al  (左-右交替)
而非: aa, ab, ac (单手连续)
```

#### **Filtered Hints模式**
```
标签: 数字 (1-9, 10, 11, ...)
输入: 可以输入数字，也可以输入链接文本本身
优点: 提前知道要输入什么
缺点: 数字标签不如字母直观
```

---

### **Mousio Hint的做法**

#### **核心特点**
```
目标: 与Mousio无缝集成
功能: 在UI元素旁显示键盘快捷键提示
限制: 需要访问UI元素位置(沙盒环境不可用)
```

#### **关键洞察**
- 需要系统级UI元素访问权限
- Windows UIA API是关键依赖

---

### **可访问性标准** (WCAG)

#### **焦点指示器要求**
```yaml
WCAG 2.4.11 - Focus Appearance:
  outline_thickness: ≥2 CSS pixels
  offset: ≥2 CSS pixels
  contrast_ratio: ≥3:1 (vs background)

最佳实践:
  - 高可见性
  - 充足对比度
  - 背景色支持
  - 悬停效果 = 焦点效果
```

---

## 🛠️ HEMouse Hint标签系统设计

### **设计原则**

1. **可读性优先**: 标签要大、清晰、高对比
2. **智能避让**: 自动检测并避免重叠
3. **上下文感知**: 根据UI密度调整策略
4. **无前缀冲突**: 算法保证不会有歧义
5. **快速输入**: 优化字符选择提高效率

---

### **核心技术方案**

#### **1. 标签生成算法**

##### **无前缀冲突算法**

```python
class HintLabelGenerator:
    """无前缀冲突的标签生成器"""

    def __init__(self, charset='asdfghjkl'):
        """
        使用home row字符作为基础
        asdfghjkl: 9个字符，左右手平衡
        """
        self.charset = charset
        self.charset_size = len(charset)

    def generate_labels(self, count):
        """
        生成count个无冲突标签
        策略: 先用完所有单字母，再用双字母
        """
        labels = []

        if count <= self.charset_size:
            # 单字母足够
            labels = [self.charset[i] for i in range(count)]
        else:
            # 需要双字母
            # 先生成所有双字母
            for c1 in self.charset:
                for c2 in self.charset:
                    labels.append(c1 + c2)
                    if len(labels) >= count:
                        return labels[:count]

        return labels

    def generate_labels_optimized(self, count):
        """
        优化版本: 交替左右手
        左手: asdf (4个)
        右手: jkl (3个) - 简化为3个，去掉分号
        """
        left_hand = 'asdf'
        right_hand = 'jkl'

        labels = []

        # 单字母: 先左右交替
        if count <= 7:
            for i in range(count):
                if i % 2 == 0:
                    labels.append(left_hand[i // 2])
                else:
                    labels.append(right_hand[i // 2])
            return labels

        # 双字母: 保持左右交替
        # 格式: 左右, 左右, ...
        for l in left_hand:
            for r in right_hand:
                labels.append(l + r)
                if len(labels) >= count:
                    return labels[:count]

        # 如果还不够，使用右左组合
        for r in right_hand:
            for l in left_hand:
                labels.append(r + l)
                if len(labels) >= count:
                    return labels[:count]

        return labels

    def generate_labels_numeric(self, count):
        """
        数字模式: 避免与Vimium等快捷键冲突
        使用数字0-9作为基础
        """
        labels = []

        if count <= 10:
            # 单数字: 0-9
            labels = [str(i) for i in range(count)]
        else:
            # 双数字: 00-99
            for i in range(100):
                labels.append(str(i).zfill(2))  # 补零: 00, 01, 02
                if len(labels) >= count:
                    return labels[:count]

        return labels
```

##### **算法对比**

| 算法 | 容量 | 输入效率 | 冲突避免 | 记忆负担 |
|------|------|----------|----------|----------|
| **单字母** | 9 | ⭐⭐⭐⭐⭐ | ✅ 无冲突 | ⭐⭐⭐⭐⭐ |
| **交替双字母** | 81 | ⭐⭐⭐⭐ | ✅ 无冲突 | ⭐⭐⭐⭐ |
| **数字模式** | 100 | ⭐⭐⭐ | ✅ 无冲突 | ⭐⭐⭐ |
| **Vimium原版** | 702 | ⭐⭐⭐ | ❌ 有冲突 | ⭐⭐ |

**推荐**: 交替双字母算法，平衡效率与容量

---

#### **2. 智能定位与避让**

##### **标签放置策略**

```python
class HintLabelPositioner:
    """智能标签定位系统"""

    def __init__(self):
        self.label_positions = []
        self.collision_detector = CollisionDetector()

    def calculate_optimal_position(self, element, label_size):
        """
        计算最佳标签位置
        优先级:
        1. 元素左上角
        2. 元素右上角
        3. 元素左下角
        4. 元素右下角
        5. 元素内部中心
        """
        element_rect = element.getBoundingClientRect()

        # 候选位置列表 (优先级排序)
        candidates = [
            # 左上角 (最常用)
            {
                'x': element_rect.left - label_size.width - 5,
                'y': element_rect.top,
                'priority': 1
            },
            # 右上角
            {
                'x': element_rect.right + 5,
                'y': element_rect.top,
                'priority': 2
            },
            # 左下角
            {
                'x': element_rect.left - label_size.width - 5,
                'y': element_rect.bottom - label_size.height,
                'priority': 3
            },
            # 右下角
            {
                'x': element_rect.right + 5,
                'y': element_rect.bottom - label_size.height,
                'priority': 4
            },
            # 元素内部 (最后选择)
            {
                'x': element_rect.left + 5,
                'y': element_rect.top + 5,
                'priority': 5
            }
        ]

        # 检测碰撞，选择无冲突的最高优先级位置
        for candidate in candidates:
            label_rect = {
                'left': candidate['x'],
                'top': candidate['y'],
                'right': candidate['x'] + label_size.width,
                'bottom': candidate['y'] + label_size.height
            }

            # 检查与其他标签的碰撞
            if not self.collision_detector.has_collision(label_rect, self.label_positions):
                # 检查是否在屏幕内
                if self.is_within_viewport(label_rect):
                    self.label_positions.append(label_rect)
                    return candidate

        # 如果所有位置都冲突，返回最高优先级位置(可能重叠)
        return candidates[0]

    def is_within_viewport(self, rect):
        """检查矩形是否在视口内"""
        viewport_width = window.innerWidth
        viewport_height = window.innerHeight

        return (
            rect['left'] >= 0 and
            rect['top'] >= 0 and
            rect['right'] <= viewport_width and
            rect['bottom'] <= viewport_height
        )


class CollisionDetector:
    """碰撞检测器"""

    def has_collision(self, rect1, existing_rects):
        """检测矩形是否与已有矩形重叠"""
        for rect2 in existing_rects:
            if self.rectangles_overlap(rect1, rect2):
                return True
        return False

    def rectangles_overlap(self, rect1, rect2):
        """判断两个矩形是否重叠"""
        return not (
            rect1['right'] < rect2['left'] or
            rect1['left'] > rect2['right'] or
            rect1['bottom'] < rect2['top'] or
            rect1['top'] > rect2['bottom']
        )
```

##### **碰撞处理流程**

```
步骤1: 获取元素边界框
步骤2: 计算5个候选位置 (按优先级)
步骤3: 遍历候选位置
  3.1 检测与已有标签的碰撞
  3.2 检测是否超出屏幕
  3.3 选择第一个无冲突位置
步骤4: 如果全部冲突
  4.1 使用最高优先级位置
  4.2 添加半透明背景增强可读性
```

---

#### **3. 自适应标签大小**

##### **密度感知系统**

```python
class AdaptiveLabelSizer:
    """自适应标签大小调整器"""

    def __init__(self):
        self.density_thresholds = {
            'sparse': 20,      # 少于20个元素
            'moderate': 50,    # 20-50个元素
            'dense': 100,      # 50-100个元素
            'very_dense': 200  # 超过100个元素
        }

    def calculate_label_size(self, element_count, viewport_area):
        """
        根据元素数量和视口大小计算标签尺寸
        """
        density = element_count / viewport_area * 1000000  # 每百万像素的元素数

        if element_count < self.density_thresholds['sparse']:
            # 稀疏: 大标签
            return {
                'font_size': '16px',
                'padding': '6px 10px',
                'min_width': '32px',
                'min_height': '28px'
            }
        elif element_count < self.density_thresholds['moderate']:
            # 中等: 标准标签
            return {
                'font_size': '14px',
                'padding': '4px 8px',
                'min_width': '28px',
                'min_height': '24px'
            }
        elif element_count < self.density_thresholds['dense']:
            # 密集: 小标签
            return {
                'font_size': '12px',
                'padding': '3px 6px',
                'min_width': '24px',
                'min_height': '20px'
            }
        else:
            # 超密集: 最小标签
            return {
                'font_size': '10px',
                'padding': '2px 4px',
                'min_width': '20px',
                'min_height': '16px'
            }

    def get_density_level(self, element_count):
        """获取密度等级"""
        if element_count < self.density_thresholds['sparse']:
            return 'sparse'
        elif element_count < self.density_thresholds['moderate']:
            return 'moderate'
        elif element_count < self.density_thresholds['dense']:
            return 'dense'
        else:
            return 'very_dense'
```

##### **视觉样式设计**

```css
/* Hint标签基础样式 */
.hemouse-hint-label {
    position: absolute;
    z-index: 999999;

    /* 基础外观 */
    font-family: 'Arial', 'Segoe UI', sans-serif;
    font-weight: bold;
    text-align: center;
    line-height: 1;

    /* 圆角和阴影 */
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);

    /* 动画过渡 */
    transition: all 0.15s ease-in-out;

    /* 防止选择和交互 */
    user-select: none;
    pointer-events: none;
}

/* 稀疏模式 (大标签) */
.hemouse-hint-label.sparse {
    font-size: 16px;
    padding: 6px 10px;
    min-width: 32px;
    min-height: 28px;

    /* 高对比度配色 */
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #000000;
    border: 2px solid #FF8C00;
}

/* 中等密度 (标准标签) */
.hemouse-hint-label.moderate {
    font-size: 14px;
    padding: 4px 8px;
    min-width: 28px;
    min-height: 24px;

    background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
    color: #FFFFFF;
    border: 2px solid #2E7D32;
}

/* 密集模式 (小标签) */
.hemouse-hint-label.dense {
    font-size: 12px;
    padding: 3px 6px;
    min-width: 24px;
    min-height: 20px;

    background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
    color: #FFFFFF;
    border: 1px solid #0D47A1;
}

/* 超密集 (最小标签) */
.hemouse-hint-label.very-dense {
    font-size: 10px;
    padding: 2px 4px;
    min-width: 20px;
    min-height: 16px;

    background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
    color: #FFFFFF;
    border: 1px solid #4A148C;
}

/* 激活状态 (用户输入匹配) */
.hemouse-hint-label.active {
    transform: scale(1.15);
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.6);
    filter: brightness(1.2);
}

/* 半透明背景增强 (碰撞时) */
.hemouse-hint-label.overlapping {
    background: rgba(0, 0, 0, 0.85);
    color: #FFFF00;
    border: 2px solid #FFFF00;
}
```

---

#### **4. 高密度UI特殊处理**

##### **问题场景**
```
示例: IDE工具栏
- 30+个小图标按钮
- 每个按钮20x20px
- 间距仅2-3px
- 标签放置极度困难
```

##### **解决方案: 分区分组**

```python
class DenseUIHandler:
    """高密度UI处理器"""

    def __init__(self):
        self.grid_size = 100  # 网格单元大小 (px)

    def partition_elements(self, elements):
        """
        将元素按空间位置分区
        """
        grid = {}

        for element in elements:
            rect = element.getBoundingClientRect()
            center_x = (rect.left + rect.right) / 2
            center_y = (rect.top + rect.bottom) / 2

            # 计算网格坐标
            grid_x = int(center_x / self.grid_size)
            grid_y = int(center_y / self.grid_size)
            grid_key = f"{grid_x},{grid_y}"

            if grid_key not in grid:
                grid[grid_key] = []

            grid[grid_key].append(element)

        return grid

    def generate_hints_for_dense_region(self, elements):
        """
        为密集区域生成Hint
        策略: 两阶段选择
        """
        if len(elements) <= 9:
            # 直接标注所有元素
            return self.generate_direct_hints(elements)
        else:
            # 第一阶段: 选择区域
            # 第二阶段: 选择具体元素
            return self.generate_two_stage_hints(elements)

    def generate_two_stage_hints(self, elements):
        """
        两阶段Hint生成
        """
        # 第一阶段: 分组
        groups = self.partition_into_groups(elements, group_size=9)

        stage1_hints = []
        for i, group in enumerate(groups):
            # 计算组的中心位置
            group_center = self.calculate_group_center(group)

            stage1_hints.append({
                'label': str(i + 1),
                'position': group_center,
                'elements': group,
                'stage': 1
            })

        return stage1_hints

    def partition_into_groups(self, elements, group_size=9):
        """将元素分成组"""
        groups = []
        for i in range(0, len(elements), group_size):
            groups.append(elements[i:i+group_size])
        return groups

    def calculate_group_center(self, group):
        """计算组的中心位置"""
        total_x = 0
        total_y = 0

        for element in group:
            rect = element.getBoundingClientRect()
            total_x += (rect.left + rect.right) / 2
            total_y += (rect.top + rect.bottom) / 2

        count = len(group)
        return {
            'x': total_x / count,
            'y': total_y / count
        }
```

##### **两阶段选择示例**

```
场景: 50个密集按钮

第一阶段:
  显示: 6个数字标签 (1-6)
  每个标签代表一组8-9个按钮
  用户输入: 3

第二阶段:
  显示: 第3组的9个按钮标签 (a-i)
  用户输入: f
  结果: 定位到第3组的第6个按钮
```

---

#### **5. 智能过滤不可见元素**

```python
class VisibilityChecker:
    """可见性检查器"""

    def is_element_visible(self, element):
        """
        综合判断元素是否真正可见
        """
        # 检查1: 元素尺寸
        rect = element.getBoundingClientRect()
        if rect.width === 0 or rect.height === 0:
            return False

        # 检查2: 在视口内
        if not self.is_in_viewport(rect):
            return False

        # 检查3: CSS可见性
        style = window.getComputedStyle(element)
        if (style.display === 'none' or
            style.visibility === 'hidden' or
            style.opacity === '0'):
            return False

        # 检查4: 被遮挡
        if self.is_obscured(element):
            return False

        return True

    def is_in_viewport(self, rect):
        """检查元素是否在视口内"""
        return (
            rect.top < window.innerHeight and
            rect.bottom > 0 and
            rect.left < window.innerWidth and
            rect.right > 0
        )

    def is_obscured(self, element):
        """检查元素是否被其他元素完全遮挡"""
        rect = element.getBoundingClientRect()
        center_x = (rect.left + rect.right) / 2
        center_y = (rect.top + rect.bottom) / 2

        # 获取中心点的最顶层元素
        top_element = document.elementFromPoint(center_x, center_y)

        # 检查是否是目标元素或其子元素
        return not (top_element === element or element.contains(top_element))
```

---

## 🎨 视觉设计最佳实践

### **配色方案**

#### **高对比度主题**
```css
/* 亮色主题 */
.hemouse-hint-light {
    background: #FFD700;  /* 金黄色 */
    color: #000000;       /* 黑色文字 */
    border: 2px solid #FF8C00;
}

/* 暗色主题 */
.hemouse-hint-dark {
    background: #000000;  /* 黑色 */
    color: #00FF00;       /* 绿色文字 */
    border: 2px solid #00FF00;
}

/* 自适应主题 (根据页面背景) */
.hemouse-hint-adaptive {
    background: var(--adaptive-bg);
    color: var(--adaptive-fg);
    border: 2px solid var(--adaptive-border);
}
```

#### **对比度算法**

```python
class ContrastCalculator:
    """对比度计算器"""

    def calculate_contrast_ratio(self, color1, color2):
        """
        计算两个颜色的对比度
        WCAG标准: 至少3:1
        """
        l1 = self.get_relative_luminance(color1)
        l2 = self.get_relative_luminance(color2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def get_relative_luminance(self, rgb):
        """计算相对亮度"""
        r, g, b = rgb
        r = self.adjust_channel(r / 255)
        g = self.adjust_channel(g / 255)
        b = self.adjust_channel(b / 255)

        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def adjust_channel(self, channel):
        """调整通道值"""
        if channel <= 0.03928:
            return channel / 12.92
        else:
            return ((channel + 0.055) / 1.055) ** 2.4

    def get_optimal_label_color(self, background_color):
        """
        根据背景色选择最佳标签颜色
        """
        bg_luminance = self.get_relative_luminance(background_color)

        # 如果背景亮，使用深色文字
        if bg_luminance > 0.5:
            return {
                'background': '#FFD700',  # 金黄色
                'foreground': '#000000',  # 黑色
                'border': '#FF8C00'
            }
        else:
            # 如果背景暗，使用亮色文字
            return {
                'background': '#000000',  # 黑色
                'foreground': '#00FF00',  # 绿色
                'border': '#00FF00'
            }
```

---

### **动画与反馈**

```css
/* 出现动画 */
@keyframes hint-appear {
    0% {
        opacity: 0;
        transform: scale(0.5);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

.hemouse-hint-label {
    animation: hint-appear 0.15s ease-out;
}

/* 输入匹配高亮 */
@keyframes hint-pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.15);
    }
}

.hemouse-hint-label.matching {
    animation: hint-pulse 0.3s ease-in-out;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.8);
}

/* 选中动画 */
@keyframes hint-select {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.3);
        opacity: 0.8;
    }
    100% {
        transform: scale(0);
        opacity: 0;
    }
}

.hemouse-hint-label.selected {
    animation: hint-select 0.2s ease-out forwards;
}
```

---

## 📋 实施建议

### **阶段1: MVP (Week 1-2)**

```yaml
目标: 基础Hint系统
实现:
  - 无前缀冲突标签生成 (单/双字母)
  - 基础定位算法 (5个候选位置)
  - 简单碰撞检测
  - 固定大小标签 (14px)
  - 高对比度配色

验证:
  - 少于50个元素的页面正常工作
  - 标签清晰可读
  - 无明显重叠
```

### **阶段2: 优化 (Week 3-4)**

```yaml
目标: 自适应与智能
实现:
  - 密度感知标签大小
  - 智能碰撞避让
  - 可见性过滤
  - 自适应配色
  - 两阶段选择 (密集UI)

验证:
  - 支持100+元素的密集UI
  - 标签大小合理调整
  - 碰撞率<5%
```

### **阶段3: 打磨 (Week 5-6)**

```yaml
目标: 用户体验提升
实现:
  - 流畅动画
  - 键盘反馈
  - 用户配置
  - 性能优化
  - A/B测试

验证:
  - 动画流畅(60fps)
  - 延迟<100ms
  - 用户满意度>85%
```

---

## 🎯 性能优化

### **关键指标**

```yaml
目标性能:
  hint_generation: <50ms
  collision_detection: <30ms
  rendering: <20ms
  total_latency: <100ms

优化策略:
  - 使用Web Workers处理计算
  - Canvas预渲染标签
  - 虚拟DOM diff减少重绘
  - 区域缓存避免重复计算
```

### **性能监控**

```javascript
class PerformanceMonitor {
    measureHintGeneration() {
        const start = performance.now();

        // Hint生成逻辑
        const hints = this.generateHints();

        const end = performance.now();
        const duration = end - start;

        // 记录性能数据
        this.logPerformance('hint_generation', duration);

        // 如果超过阈值，触发警告
        if (duration > 50) {
            console.warn(`Hint generation slow: ${duration}ms`);
        }

        return hints;
    }
}
```

---

## ✅ 最终推荐方案

### **核心配置**

```json
{
  "hint_labels": {
    "charset": "asdfghjkl",
    "algorithm": "alternating_hands",
    "max_single_char": 9,
    "max_hints": 81
  },

  "positioning": {
    "strategy": "smart_avoid",
    "candidates": ["top-left", "top-right", "bottom-left", "bottom-right", "center"],
    "collision_padding": 5
  },

  "sizing": {
    "adaptive": true,
    "thresholds": {
      "sparse": 20,
      "moderate": 50,
      "dense": 100
    }
  },

  "visual": {
    "theme": "adaptive",
    "animation": true,
    "animation_duration": 150
  },

  "performance": {
    "max_latency": 100,
    "lazy_render": true,
    "viewport_only": true
  }
}
```

---

**文档版本**: v1.0
**创建日期**: 2025-09-28
**状态**: 设计完成，待实施