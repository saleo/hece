# why
1. I need control mouse without hands,since as a develop and heavy computer use. Sometimes I need to work Without desktop.
2. 头眼控制鼠标，减少我缩回的动作，进而提升输入速度
3. 如果头和眼能控制的话，那么还能对健康有利，因为这样子在操作电脑过程中可以动脖子动眼,避免长时间僵持在那里。除此之外：
  - 撅嘴吹口哨让人轻松
  - 嘴部吸气动作，提醒并做深呼吸
4. 桌面整洁
5. （高级）解决双屏幕或两电脑鼠标共享时头转动，而鼠标没有跟随头部移动、导致另外还要每次去滑鼠标再移动到对应屏幕问题。
6. 快捷键虽好，但也有不足
  - 有些操作没有快捷键、或者比较难定义，比如VScode启动后某些扩展的提示
  - 快捷键太多，记不住
  - some applications works with most shortcuts,but not all: 
	- dida qingda, cannot focus on edit after task-creation ,even with tab key
    - vscode github copilot, mouse can scroll history,while no shortcut for keyboard
    - 那些浮窗：词典的查词小窗、讯飞输入法
  - 企业微信中的tapd
10. 类似 https://docs.cursor.com/chat/overview 这个网页，vimium支持不好：要反复来回用gf切换当前frame
11. when we cannot pgup/pgdown and other ways to scroll webpage with vimium, click a mouse will help to get it done, since the `gf` key cannot work as expected.


总结（按重要性优先级）
  - 利健康
  - 便操作（游学、直播）
  - 提效率（提速、好心情。。）

## 潜在客户调研
### 唱歌直播的人
不方便操作鼠标和键盘，eg彭老师
### 知识工作者（键盘使用频率高于鼠标）
如鼠标使用频率高于键盘，如抠图设计人，则不合适

# what
- 如果不做到更稳、准、快，否则无人用
- （optional）AI观察到健康问题，主动或被动提出解决方案、提醒
-  Ai观察到问题去提醒：坐正、去休息。。


## 同类产品调研
### mouse-free
- gdeveloping / mouse-free: 。在电脑屏幕上布上一层幕布，在整个屏幕上切分区域，每个区域用两个字母来表示，输入这两个字母就可以把光标移动到对应的位置
  - 主打用键盘替代鼠标，避免切换影响速度和准确性。功能看起来不错，只是没有健康方面的功能
- 默认不显示， c-a=space 满屏显示，整桌快捷键
- 如有2显示器，而不是2主机，会同样铺满另个显示器
- 下载、build的exe，总被报警并删除by Windows defender
- 会记录上次软件状态、位置，标识鼠标附近位置

### PGM-precisionGazeMouse
- use eViaCam as its headTracking.
- 用头微调在1~4厘米半径以内，而眼睛大调在4厘米半径以外

### openTrack
options: relative Translation(平移)
调整NaturalMovement的： filter只有rotation有用， 无论是Responsiveness还是drift speed
scoll/click都做不到。
Filter:  Takes your raw data and smoothens a bit, so that you don't get any annoying jittery one looking around, I use standard accela settings, any smoothing will introduce a slightly delay if set low enough. Let's say. 2 milliseconds. You won't wait. The delay really

- tracker:  FaceTracker, Aruco(more reliable),point(most reliable, needs external devices),eyeTracker
#### OT-neutralNet-tracker-train code
#### AITracker
 Facial recognition models ., landmark recognization ....With an AI track. There are several neutral networks trained to recognize 68 landmarks to estimate users head position. models


### cameraMouse
#### 优点
- 。速度切换移动多快，文档菜单功能好

#### 缺点
单击、右击是另外按 dwell click.不能保存上次设置
用dwell click控制不好，因为不动也会click
以他为代表的软件是以残障人士为目标。。,不是，以效率和保健人群为目标

### https://smylemouse.com/
虽然接近自己需求。特点是用微笑来click。劣势是下载太慢，下载链接是邮件发送的
。并且比较贵，完全买断要400多美元，月费是29美元。

### eyeMouse
- 低头写字慢速摇头可能是例外。
确定没有人做过这个: 用笔记本自身所带镜头就足够的eyeMouse

### mouse-control-AHK
- 键盘操作鼠标：慢、快选择。
- 与现有程序快捷键冲突 

自用必要性不强，字作为
- 多显示器时的切换
- 不常用软件的鼠标操作
- 常用软件、但忘记快捷键

- 用纯键盘操作鼠标的方法。还有个问题就是在某些只用单字母，而不是用修饰符加字母来控制做快捷键的界面程序，比如。Chrome vimium下会冲突。所以还要设置一个白名单，在这些程序下不使用该快捷键。


- （增强？难点？）鼠标拖动垂直或水平滚动条：物理鼠标做法是：保持按着左键、上下移动鼠标：~~自己可以左手按脸、上下移动头或眼睛~~ 这个体验不好
- (增强？难点？)鼠标滚轮效果
- AI-Agent:
  - 快捷键多了容易冲突、忘记，AI可协助