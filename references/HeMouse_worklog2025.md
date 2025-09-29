2025年5月10日

- 目前看，对控件级别进行区分，点击即可；在文本区内不做精准控制。因为后者难度较大，且有对应的 vim 等支持
- 大笑+头动：大笑做个 启动终止控制量，类似vim的escape
	- 大笑开始：上下左右摆头，分别对应上下左右4个区域
	- 大笑停止：对应区域上视觉元素被字幕数字标识：
	
## 2024年11月30日
```
as an expert on CV(computer vision) and HMI (human-machine interaction) expert , and also a tech guru on windows with comprehensive experience on LLM with vision, pls give me an practicable and workable solution , to satisify my requirement:
1. i have 2 monitors side by side (left to right), pls detect the layout of the monitor, they may be both horizontal placement; and the  laptop which one monitor  belongs to , has a builtin medium-quality webcamera
2. when i turn my head to  the left monitor, the window shown on it is activated after reasonable time staring on it, so do the right monitor (to simplified: there's 1 window shown on each monitor)
3. the program needs to have a startup calibration procedure, to better know the exact behavior above mentioned, since each user-to-monitor distance+angle can be different each time i use them

pls think slowly and provide an insightful solution which is fully considering the limited resource in the windows laptop, attached notepad contains information on CPU and GPU for your reference

CPU

	11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz

	基准速度:	2.80 GHz
	插槽:	1
	内核:	4
	逻辑处理器:	8
	虚拟化:	已启用
	L1 缓存:	320 KB
	L2 缓存:	5.0 MB
	L3 缓存:	12.0 MB

	利用率	7%
	速度	1.32 GHz
	正常运行时间	0:00:38:59
	进程	285
	线程	3431
	句柄	123264

GPU 0

	Intel(R) Iris(R) Xe Graphics

	驱动程序版本:	31.0.101.4255
	驱动程序日期:	2023/3/16
	DirectX 版本:	12 (FL 12.1)
	物理位置：	PCI 总线 0、设备 2、功能 0

	利用率	1%
	专用 GPU 内存	
	共享 GPU 内存	0.6/15.8 GB
	GPU 内存	0.6/15.8 GB

GPU 1

	NVIDIA GeForce MX450

	驱动程序版本:	31.0.15.2908
	驱动程序日期:	2023/5/30
	DirectX 版本:	12 (FL 12.1)
	物理位置：	PCI 总线 1、设备 0、功能 0

	利用率	0%
	专用 GPU 内存	0.0/2.0 GB
	共享 GPU 内存	0.0/15.8 GB
	GPU 内存	0.0/17.8 GB

```


## 2024年11月29日

 #q In Cursor/IntelliJ IDEA's editor area (vim insert or normal mode), a normal click will put the cursor at desired location , while, also do an extra action: select adjacement word 。。as compared, sublime(vim insert or normal mode) has no problem, so do notepad, 
 	- tried around 10 times, no success, abandon tentatively
 		- since its a minor extra action, the main action works as desired


 #q you are LibreOffice Calc developer and expert in windows system developping focus on keyboard and mouse, windows message, can you help diagnose the problem:   with this program , double-click for a target character in a cell of Calc cannot make the caret before the character , that is mouse double-clicking did;  Insteadly,  the below cell is actively selected 


 - debug-log: add grid-level ; double-click events recored in log

 2024年11月29日 16:23:42
 immediate #done： branch manage and follow feature、buffix naming for every new feature，bugfix， which is a MUST and essential for HECE develop


2024年11月29日 19:05:29
above shows: double-typing enter wont work within cells in LibreOffice calc, we found its due to Enter Key, so we tried to use capLock to replace

- caplsLock refactor:
	- capsLock+space: launch grid at current monitor
	= capsLock+ arrowKey: launch grid at respective monitor， formmer is: L/R key ...
	- cpasLock once: single-click
	- capsLock double-typing: double-click
	- capsLock+shift: right-click

	Q: Why kb first? 
	A: 1. for easy and simplicity to test and use; 2. KB can improve productivety, which indirect improve health.

	Q: why using as much KB as possible?
	A: since user can meet some bad CV condiation, such as no web-camera, bad lighting condition,etc

---
git branch -m keyboardReplaceMouse_36cells HECE_main, we make this branch as baseline from now on.
relationship: 
- keyboardReplaceMouse forked out: keyboardReplaceMouse_36CELLS,
- moreMonitorsRelevance forked out: keyboardReplaceMouse
- HEMouse forked out: moreMonitorsRelevance

---


Ah, you raise a good point! Yes, using a single CapsLock press for clicking could conflict with other CapsLock combinations. Let's modify the code to avoid this conflict:

```python:productivity/utils/UIautomation.py
def handle_caps_press_down(self, event):
    """Handle caps lock press down"""
    current_time = time.time()
    
    # Track the press time for potential click action
    if self.movement_mode and self.current_position:
        self.caps_press_start = current_time
    
    self.caps_lock_pressed = True
    self.last_caps_press = current_time
    return False

def handle_caps_release(self, event):
    """Handle caps lock release"""
    if self.movement_mode and self.current_position:
        release_time = time.time()
        # Only perform click if it was a quick press (less than 200ms)
        # and no other keys were pressed during this time
        if hasattr(self, 'caps_press_start') and \
           (release_time - self.caps_press_start) < 0.2 and \
           not (keyboard.is_pressed('shift') or 
                keyboard.is_pressed('ctrl') or 
                keyboard.is_pressed('space')):
            self.logger.debug("Quick CapsLock press in movement mode - performing click")
            self.perform_click(self.current_position[0], self.current_position[1])
    
    self.caps_lock_pressed = False
    if hasattr(self, 'caps_press_start'):
        del self.caps_press_start
    return False
```

The changes:
1. Added timing check for CapsLock press duration
2. Only performs click if:
   - CapsLock was pressed quickly (less than 200ms)
   - No modifier keys were pressed during the CapsLock press
   - We're in movement mode（"Movement mode" is the state after you've selected a cell in the grid but before clicking. It's when you can use arrow keys to fine-tune the cursor position）
3. Maintains all other CapsLock combination functionality

This way:
1. Quick tap of CapsLock = click (in movement mode)
2. CapsLock + Arrow = show grid on monitor
3. CapsLock + Space = show grid at current monitor
4. CapsLock + Esc = exit application

Let me know if this better handles the potential conflicts!

---
BugFix: in LibreOffice Calc,  double-typing capLock now can insert caret or select the word containing the target char, which is same as physical mouse do, verified as:
1. if caret is in the cell, double-click certain char will select the word containing the char
2.If there is no caret in the cell, double-click will insert a caret before the char



## 2024年11月28日
Q： by now, cursor position works, but when do a click, caret not appear in the position expected
AI: The caret positioning issue in text editors occurs because different text editors handle mouse clicks and input focus differently

```
as an computer vision and human machine interaction expert, do help provide me a productive and robust solution to replace mouse with facial action with or without keyboard on existing code, which did a good job on 2 action with only keyboard:
- move cursor 
-  click  and place caret 

so my requirement is:
1.  following the easist and convenient first pricinple, most reliable and distinct, thats: robust facial action for most common opertions , 
2. support following operations at stage 1, this is the stage we're now
- click 
- double click
- right click 
3.  support following operations at stage 2, this is the next stage ,
- mouse scroll
-  select text
4.  (optional) consider advanced mouse-drag-drop ,final stage and optional one

```


 #done add configuration: use caret-based or cursor-based way to detect which monitor user prefer, now its cursor-based
```
This improved version:
First tries to detect the monitor based on the active window location:
Gets the currently focused window
Uses the window's center point to determine which monitor it's on
This helps when you're typing in a window on a different monitor
2. Falls back to cursor position if:
No focused window is found
The focused window isn't on any monitor
Uses primary monitor as final fallback
4. Adds detailed logging to track the decision process
This makes the behavior more intuitive because:
The grid appears on the monitor where you're actively working
Works better with text editors and other applications
Still maintains the cursor-based fallback for other scenarios
Let me know if you'd like any adjustments to this behavior!

```

## 2024年11月27日
- 2个 36cell的grid显示，第二级36显示会有点小；15.6寸屏幕默认显示
	- 

tried to implement the following, but failed after several tries
"
add arrow-key movement fearture on the cell within each level grid, note for the movement step-size should depend on 
1.  no more than 2 pressing to reach its farest end
2.  movement should not be limited in the cell
"
	

	```
	as an computer vision and human machine interaction expert, do help provide me a productive and robust solution to replace mouse with keyboard+ facial action on existing code
1.  following the easist and convenient first pricinple for common opertions ( in a usage-frequence sequence, from more to less) as below
- right click
- 
	
	```


## 2024年11月25日
benefits on using vim-like solution on replace mouse-click
- compared to head-move-to-switch-monitor: more monitors works similiar with one monitor
- compared to head-move-to-switch-monitor: dont need care more windows in the screen
- avoid the mistakes that using head to move mouse, which may be casued by wrong detect/recognization with openCV or relevant AI, CV technology

 #commercial: FYR: https://buy.stripe.com/dR65lv0no97Dds428h

 

**attention**:  although most text in editor can be reached, there're some text unreachable with latest commit #todo

## 2024年11月24日
im really excited to say:
1. With cursor-AI help tonight, i did make vim-like mouse movement workable; and the workload including learning is very efficient, 2 hours work with cursor-AI can overpass 2 months traditional learning and implementing.


## 2024年9月15日
Q： tabs 和 focusable什么关系？
\
A: 
> From AI: 4. **Control**: Developers can control which elements are focusable and the order in which they receive focus by using the `tabindex` attribute. For example, setting `tabindex="-1"` makes an element focusable programmatically but not via the tab key.

> In summary, the tab key is a means of navigating through focusable elements in a user interface. Understanding the relationship between tab and focusable elements is crucial for creating accessible and user-friendly web applications. Proper management of focusable elements ensures that all users can navigate and interact with the application effectively.

> **Tab stops** from [Accessibility Insights Tab stops](https://accessibilityinsights.io/docs/windows/reference/tabstops/)
> Why it matters
> Users must be able to interact with a software application using only a keyboard.

> Using a mouse is impossible for people who can't see the pointer.
> Some people don't have the physical capability to control a pointing device.
> Many people without disabilities prefer to use a keyboard.
> Good tab stop design allows keyboard users to:

> Access all of the application's interactive elements in a predictable order.
> Identify which element currently has the input focus.
> Poorly-designed tab stops create high-impact accessibility problems.


## 2024年9月8日
又一个场景：eudic欧陆词典，划词搜索后弹出 eusoft_eudic_en_win32为标题的窗口， 必须要用鼠标点击该窗口外的焦点，才能关闭该窗口。
~~#todo 想个解决太多快捷键容易冲突的问题~~ (done)，AHK 能解决这类问题，esc to quit eudic look-up words window这个提交的代码有参考意义：
> HotIfWinExist("eusoft_eudic_en_win32")
> Hotkey("Esc",closeEuDicWindow)

- [win-vind](HEMouse-references.md)中的 edit mode-visual模式似乎不错，但不适合普通用户，所以对普通用户来说，还是给它在当前文本情况下 提示用 shift,ctrl,alt+上下左右按钮来移动鼠标选择文本吧

## 2024年8月26日
重要决定:要做两个版本，一个开源，一个闭源，分别提供不同的功能和收费模式，这样有几点好处
1. 可以避免人的猜忌说你这个代码里面是不是会涉及人的隐私
2. 可以让更多的开发人员参与进来做协作进而交更多朋友，吸引更多人才
3. 也让自己有点开源精神可以回报社区

## 2024年8月25日
计划：完成随头部移动切换不同显示器的当前显示窗口，游标/光标落在当前显示窗口原有位置
拆解：
1. 实现用hotkey
2. 实现头部切换

## 2024年8月15日
鼠标移动范围，可以由3种来控制（1、3要有针对用户个人的训练）
1. 微笑、中笑、大笑：分别对应：当前鼠标所在位置的小、中、大九宫格
2. ctrl、shift、capslock（完成最终点击动作后，应补充1个capslock以恢复其原有状态）：同上
3. 头部移动鼠标到对应


## 2024年6月14日
- 改为lessMouse.ai可能更合适点，因为有些操作不好实现
- 实现方式也可能要改为：少量头（眼）控+ 唇语控
- 不适合抠图等鼠标为主的工作者，适合键盘为主、鼠标为辅的工作，比如编辑+软件开发
- 
## 2024年5月23日


## 2024年5月10日
- visual-speech-recognize，据介绍计算intensive，对速度慢电脑不合用
- pyautogui 不支持副屏

本想用pynput.keyboard代替 keyboard，因后者的key会被某些application给吞没、且suppress/blocking key传递给其它application，但看pynput文档才知：它也一样
> on windows, Furthermore, sending key press events will properly propagate to the rest of the system

之后又搜索了其它2个类似项目，也都没看到可满足需求
综上，在mask层（mouse-free项目中的identity-window）输入key，会传递给其它程序。。 I tested on chrome address bar,  And  confirmed:  when I press number zero on  Right hand pane when  So identify window is on,  And I saw  zero. Also show in the address bar

再加上上述两个库都不能直接支持双击capsLock, 不需要另外设置阈值和写程序,
确定一个结论吧:，不用键盘操作做控制性命令... #todo  use lip reading
- 开关

## 2024年5月4日
计划：
- 实现基本功能


## 2024年4月28日
计划：
- 确定昨天结论中的左右上下摆动，适合用头眼。。
- 
实际：
- 想到了一个办法可以规避问题尽量还是用头眼来控制鼠标
- 按ctrl做头控启动
- caps-lock双击：显示/隐藏 遮罩层
- 粘滞键windows自己设定是5次点按shift，intelliJ取巧：2次shift。。
- 其它2次的： 2次alt不能用，会启动文件菜单；2次ctrl会启动  1个国产启动软件
- 搜索"长按control键"，没有结果证明这个键可以被我们使用

## 2024年4月27日
看mouseFree的快捷键设置，联系这些年看到的快捷键，发现在已有这么多的软件、这么多年的进化后，想设置个好的、没有冲突的快捷键，实在很难，所以还是应该从 嘴部的Audio+Video角度来提供这类辅助
- 头、眼动来控制鼠标，优劣都明显：
	-  优点：
		- 左右摆动来控制：直观、对受众来说自然
		- 助人健康
		- 
	- 缺点：
		- 容易判断错误：到底是自然摆头（眼）还是控制鼠标用的？ 虽然可以加多前置或中置的判断因素，比如张嘴、闭嘴来启动、停止鼠标移动指令
		- 摆动后一般还要返回中位
		- 苹果VisionPro的做法是：用多个红外光源+红外传感器来做
- 可以采用的是：
	- 模仿单击、双击：可以用头、眼
	- 模仿右键：右眼眨动
- 不合适的是：
	- 上下、左右摆动来定位鼠标
	- 上下、左右拖放文件
	- 上下、左右拖动滚动条

## 2024年4月25日
今日PLAN:  改造mouse-free, 使得
- 双击caps lock：显示9宫格
- 双击alt ：在当前鼠标附近显示待点击-不支持alt，因为单击alt会高亮file菜单

- escape键给mouseFree全局占用了，bug

```
saleo: whats  Common use case of the ` Suppress` =true  In the below function

GitHub Copilot: The `suppress` parameter in the `add_hotkey` function is used to control whether successful triggers of the hotkey should block the keys from being sent to other programs. When `suppress` is set to `True`, it means that the keys will be suppressed and not sent to other programs when the hotkey is successfully triggered.

This can be useful in scenarios where you want to prevent the default behavior of certain key combinations or prevent other programs from receiving the key events when the hotkey is pressed. For example, if you have a hotkey that is used to perform a specific action within your application, you may want to suppress the key events from being sent to other programs to avoid unintended behavior.

Here's an example of using the `suppress` parameter:

```python
def my_callback():
    print("Hotkey triggered!")

# Add a hotkey that triggers the callback and suppresses the key events
add_hotkey('ctrl+shift+a', my_callback, suppress=True)
```

In this example, when the user presses the "ctrl+shift+a" key combination, the `my_callback` function will be invoked, and the key events will be suppressed, preventing other programs from receiving them.

It's important to note that the behavior of suppressing key events may vary depending on the operating system and the context in which the code is running.

saleo:  Can use explain the last sentense you said in details

GitHub Copilot: Certainly! In the code excerpt you provided, there is a comment that mentions the file "__init__.py". This comment is referring to the current file that contains the code snippet you shared. The "__init__.py" file is a special file in Python that is used to mark a directory as a Python package. It can contain initialization code and define the behavior of the package when it is imported.

In this case, the code snippet is part of the "__init__.py" file, which means it is defining the behavior of the package or module that this file belongs to. The code defines a function called "add_hotkey" that allows you to register a hotkey combination and a callback function. When the registered hotkey combination is pressed, the callback function will be invoked.

The last sentence I mentioned refers to the fact that the "add_hotkey" function returns an event handler function. This event handler function can be used to remove the registered hotkey later on if needed. To remove a hotkey, you can call the event handler function returned by the "add_hotkey" function, or you can use the hotkey itself as a parameter to the "remove_hotkey" function.

In summary, the code you provided is part of the "__init__.py" file and defines a function called "add_hotkey" that allows you to register hotkeys and their corresponding callback functions. The function returns an event handler function that can be used to remove the registered hotkey later on.

saleo: /explain more on this sentense "it's important to note that the behavior of suppressing key events may vary depending on the operating system and the context in which the code is running."

GitHub Copilot: In the provided code, there is a parameter called `suppress` in the `add_hotkey` function. This parameter determines whether successful triggers of the hotkey should block the keys from being sent to other programs.

However, it's important to note that the behavior of suppressing key events may vary depending on the operating system and the context in which the code is running. Different operating systems handle key events differently, and the behavior can also be influenced by the specific application or environment in which the code is executed.

For example, on some operating systems, suppressing key events may prevent other programs from receiving those key events, effectively blocking them from performing their intended actions. This can be useful in scenarios where you want to ensure that the hotkey triggers only the desired functionality and doesn't interfere with other applications.

However, in other contexts or operating systems, suppressing key events may not have the same effect. It's possible that the key events may still be received by other programs, regardless of the `suppress` parameter. This means that the hotkey functionality may not be isolated and could potentially interfere with other applications or system-wide shortcuts.

Therefore, when using the `suppress` parameter, it's important to consider the specific operating system and context in which the code will be executed. It's recommended to test the behavior on the target platform to ensure that the key event suppression works as expected.

saleo: is there a way to ensure the hotkey be suppressed/blocked ,and would not be sent to other programs

GitHub Copilot: To ensure that the hotkey is suppressed and not sent to other programs, you can modify the `add_hotkey` function by setting the `suppress` parameter to `True` when calling `_add_hotkey_step` function. 


## 2024年4月16日
考虑到用头来控制无论是用传统的程序加坐标变换、位置计算来做还是机器学习来做，都有一定的难度，所以考虑用口型来控制：
- 实际只用一个字就能控制：因为正常情况头部的水平位置都是居中的，所以只要用一个字来控制垂直运动就可以了
- 而但凡口型一个字的控制，那么它自然就有起始的时间；也就是说不会存在用头控制、需要增加开关量，来确定准确意图的问题：头往左上走，之后回头到原来中位，这个究竟他是往左上走还是往右下走不好确定，需要增加嘴巴做开关量：张开嘴巴是其实关闭嘴巴是终止通过终止位置和起始位置的坐标差值来判断他的意向是什么


## 2024年4月13日
- 《降伏其心》：专注时要头、眼僵硬。。如此不是跟HEMouse倡导的微动相反了？ 实际还好，因为鼠标用户就是不用HEMouse，也不会一直僵硬在那里的，因为鼠标是需要适当分心的。
- 下午看资料，晚上准备好 mouth-shape-classification的环境，运行后提示没有数据。看代码需要，而文档没有。

## 2024年4月7日
- 头部和眼部最需要关注健康但眼部运动有时个人并不完全能做到，比如左眼动和右眼动，单左眼眨眼或者单右眼眨眼，同时眼如果扎的话，稍微影响速度，毕竟正常来说眼睛要持续看屏幕的
- 而头部也不能大动，否则影响旁边人
- 耳朵不能被操控
- 鼻子不容易被操控，即使操控这种挺丑的
- 所以目前最合适的可能就是嘴了，嘴部的动作可以有大笑
参考：  [[嘴部动作lipAction]] #todo/question " suck in air or to blow out air" can be done via HCI?




## 2024年3月29日
- 深刻感受到 做好的利益： 使用欧路词典，它的大窗口都没有快捷键，使用起来挺不方便的，各地都找了，还是没有找到，也许他们有隐藏起来的吧。。。而如果HEMouse做好，就不考虑那么多快捷键

鉴于之前deepgaze虽然有自己所需功能，但因为文档缺失，所以找准确版本的包是困难的。
所以还是找最新的 head_pose_estimate repo
## 2024年3月28日
- 调研软件发明专利：
	- 以mouse 头控相关的很多，多到自己找不过来
	- 国内、外简单看了，少数开放查询，多数收费； 不好用
	- 
	- 自忖：最大目的是利益众生，其次是赚钱，而软件发明专利主要是为赚钱，跟自己初心不一致，且申请也有相当难度和门槛、周期


## 2024年3月22日
- 原来自己所设想的，如果你点击在左上位置，那么要回到中上的话会用其他方式来跳，但目前看统一回到正中位统一操作会更好一些，原因有几个：第1：人的习惯，头伸到某个位置只是鼠标移动后肯定还会回来的，不可能一直停在那个位置; 第2：方便统一操作
- 也不是，因为要用个 开关量来确定合适开始、何时终止移动；如此就不用限制人家必须回到中位；同时只要计算相对位移即可，所以即使做的没那么正中，也可以
- **需要整体看HEMouse：支持所有鼠标操作，而不只是移动光标；否则还是要用鼠标了**
	- 上下页面滚动，尤其那种不支持键盘操作的
	- 拖拽文件
	- 选中文字

## 2024年3月19日
多日不做HEMouse，发觉即使看到有文档，也没能马上提起精神


## 2024年3月12,3日
build successfully mediapipe (latest version) on windows11,都忘记到底为什么要build这个了。大概是因为找不到这个package。

- 注意自己机器上用的是Python，3.12.2, 官方显示的是3.8~3.11。
[mediaPipe for python setup guide] (https://developers.google.com/mediapipe/solutions/setup_python)

- 开始用 #gaze track来确定鼠标动向，之后不妥：1.可能gaze动而头不动，不符合自己头替鼠标利健康的核心理念之一；不过可以做个替补，毕竟眼控也有利于健康。
- 对用户来说，头动更容易、自然，眼珠运动需要训练；

#注意 垂直低头时，嘴巴看不到，所以微笑不易被监控到；
如果才算抬头：track开始时的y < 结束时的y，

## 2024年3月11日
如果需要眼睛控制，precisionGazeMouse还是要用 Tobii的硬件的；这个跟该作者后来用的 #Talon 所要求的一样

#kw
gaze  NOT gazebo language:Python 
awesome gaze

hemouse类 vim，但用数字代替字母来表示位置。避免快捷键冲突

## 2024年3月6日
在anxin755上，按EVC install要求安装了 windows SDK for windows7 and .net Framework 4.7.1...果不其然， 是2个sdk，如下图：
![本机安装的sdk](assets/Worklog_HEMouse/image.png)

## 2024年3月4日
#english 
- convex hull(凸包)，convex凸、hull船体、花萼
- contour 轮廓

#todo 手势开关屏幕、关机
.#shortcut #HEMouse体会  用control加数字键盘上的数字做快捷键有个好处是可以让胳膊稍微多动一些，虽然没有。存在键盘主区上操作快

## 2024年3月1日
EVC-enableViaCam要依赖多个大东西来build，使用流量较多；暂时切换研究ComputerCursorControlledByFacialExpre...

#体悟 #shortcut 容易记比容易按更重要，因为不好按时，你会低头看，这样可以活动肩颈；当然这样的代价是多花些时间了，但比不容易记、容易按到这种方式好，因为后者所花时间更长。



手机热点流量：半小时237MB

QA：能否把主机显示不全的给扩展到副屏（辅助屏幕上）？NO，win不支持

## 2024年2月29日
需要确定是主观要用头部控制鼠标时才动； 屏蔽无意为之的（用EVC的亲身经历）
- 左手挠痒，水平动；
- 低头写字，水平动
- 伸懒腰，。。
#HEMouse体会

#inputDirector 不能wrapMouse



## 2024年2月27日
searched: mouse-emulation

```
in mouse-without-border, 
 Easy Mouse means you can just move your mouse cursor to the other computers freely.

If you disable it, you will have to press the Control key when you want to move the mouse cursor to other computers.
```
## 2024年2月26日
需解决eViaCam在2台主机情况下，必须大幅扭头才能转移cursor，因它的中心是在A主机中心，更好识别当前工作屏
#english pupilla瞳孔复数，pupil瞳孔单数

解决方案：
- 计算CEA或CPA，来判断是否在当前屏前看，这个需要有个基准：每次坐下后确立基准（每个会话期内的固定位置，以座位为基准，而不是脑袋；包含人机距，眼距等）
  - 不够灵活，必须要做初始化
- 神经网络
  - [AI回答](AI模型相关.md)
## 2024年2月24日
eViaCam很不错，
- 鼠标也不抖动
- 鼠标随头移动速度合适
- 2台电脑安装Mouse_without_border，1台电脑安装EVIACAM后，可随着视线转移到对应电脑的显示屏上，很好

todo：
- 增加鼠标动作功能
  - 左键、双击、右键
  - 滚动？中间滚轮
  - 拖动
- 更合理的快捷键。
  - 极小化窗口
  - 切换启用状态



## 2024年2月23日
#todo/low 找talon中常用的动作来定义 常用，适用于电脑工作者各领域

## 2024年2月23日 之前
用笔记本电脑摄像头是：1280*720p，16:9，30fps

![自用L15摄像头设置](assets/HEMouse/image.png)
![自用笔记本摄像头照片设置](assets/HEMouse/image-1.png)

用webcamTESTS.com检测结果：
```

Webcam Name:	Integrated Camera
Quality Rating:	407
Built-in Microphone:	None
Built-in Speaker:	None
Frame rate:	30 FPS
Stream Type:	video
Image Mode:	rgb
Webcam MegaPixels:	0.92 MP
Webcam Resolution:	1280×720
Video Standard:	HD
Aspect Ratio:	1.78
PNG File Size:	1.17 MB
JPEG File Size:	589.32 kB
Bitrate:	17.37 MB/s
Number of Colors:	133379
Average RGB Color:	
 
Lightness:	70.39%
Luminosity:	69.88%
Brightness:	70.59%
Hue:	288°
Saturation:	3.31%
```

用https://www.onlinemictest.com/webcam-test/检测结果：

```json
{"Webcam Name:":"Integrated Camera (13d3:56fb)","Frame rate:":"30 FPS","Webcam Resolution:":"1280x720","Aspect Ratio:":"1.78","Webcam MegaPixels:":"0.92 MP","Camera Facing:":"environment","Built-in Microphone:":"None","Built-in Speaker:":"None","PNG File Size:":"253.84 kB","JPEG File Size:":"34.26 kB","Number of Colors:":"55979","Brightness:":"48.17 %","Hue:":"49.88 %","Saturation:":"58 °","—":"—"}
```


