---
name: browser-agent
description: 拟人化浏览器代理。让 AI 像真人一样操作浏览器，绕过网站风控检测。核心方式：截图 → 模型看图 → click_text.py 点击。
---

# Browser Agent

让 AI 像真人一样操作浏览器，完全拟人化，绕过网站风控。

## 核心原则

### 一、Browser 工具使用规范

- **❌ 禁止自动化**：`browser(act=click/fill/type/hover/press)` 等直接 DOM 操作
- **✅ 允许只读**：`browser(snapshot/tabs/status/screenshot)` 等只读查询
- **✅ 允许框架控制**：`browser(open/close/start/stop/focus/navigate)` 管理浏览器生命周期
- **✅ 允许 act=evaluate**：仅用于只读查询（禁止写入 DOM 或触发事件）
- **✅ 操作层必须模拟**：所有页面内点击/输入使用 `click.py`, `type_text.py` 等脚本

**重要边界**：
- `browser(snapshot)` 返回元素**结构**（ref, role, name），**不含坐标**
- 坐标必须通过**视觉识别**或**UIA 框架控件**获取
- 禁止将 `browser` 作为自动化引擎（那不是拟人化）

### 二、混合模式定义

```
只读数据获取（browser） + 视觉定位/坐标 + 模拟操作（scripts）
```

**允许的组合**：
1. `snapshot` → 了解页面有哪些元素（语义信息）
2. `screenshot` → 截图 + Kimi → 视觉识别坐标（通用 fallback）
3. `click.py` / `type_text.py` → 模拟鼠标键盘（最终操作层）

**禁止的组合**：
1. `browser(act=click)` → 自动化点击
2. `browser(act=fill)` → 自动化填充
3. `evaluate` 写入 `value` → 绕过模拟层

---

## 必读注意事项

## 必读注意事项

⚠️ **按顺序执行**：截图 → 识别 → 操作 → 验证 → 重复

⚠️ **窗口必须聚焦**：执行任何操作前，确保浏览器窗口是最前台活动窗口。使用 `focus_window.py` 确保聚焦。

⚠️ **浏览器必须最大化**：打开浏览器后立即最大化，避免内容显示不全导致坐标偏差。

**标准流程**：
```bash
# 1. 打开浏览器
browser(action="open", targetUrl="https://...")

# 2. 最大化窗口（必需！）
py scripts/maximize_window.py "Chrome"

# 3. 等待页面加载
Start-Sleep -Milliseconds 1000

# 4. 截图识别
py scripts/screenshot.py
```

**已配置自动最大化**：`openclaw.json` 中已添加 `--start-maximized` 参数，新打开的 Chrome 窗口会自动最大化。但建议仍手动调用一次确保。

⚠️ **屏幕分辨率**：脚本使用绝对坐标。确保浏览器窗口最大化，且分辨率稳定（推荐 1920x1080 或 2560x1440）。

⚠️ **中文输入处理**：用户默认输入法为中文双拼（自然码）。执行英文输入前，必须先切换到英文输入法；需要输入中文时，切换到中文输入法。

**最佳实践工作流**：
```bash
# 输入英文（确保是英文输入法）
py scripts/key_press.py "shift"   # 切换到英文（如果当前是中文）
py scripts/type_text.py "AI"

# 输入中文（确保是中文输入法）
py scripts/input_method.py "zh"   # 切换到中文
py scripts/type_text.py "人工智能"

# 或使用 toggle 切换
py scripts/input_method.py "toggle"
```

> ⚠️ 注意：`type_text.py` 只是模拟键盘输入，**不会自动处理输入法状态**。你必须确保在执行前手动切换到正确的输入法。

⚠️ **截图权限**：`screenshot.py` 需要系统屏幕捕获权限。首次运行可能需要：
- 以管理员身份运行 OpenClaw
- 或在 Windows 设置 → 隐私 → 屏幕截图中授权 Python
- 替代方案：使用 `read_window.py` 代替（速度快，仅限 Windows UI）

⚠️ **页面加载等待**：网络延迟可能造成页面未完全加载。建议在操作后加入等待：
```bash
py scripts/wait_for_text.py "预期内容"
```

---

## 📚 Browser 工具使用规范（详细版）

### ✅ 允许使用的动作（只读 + 框架控制）

| 动作 | 用途 | 示例 | 是否允许 |
|------|------|------|----------|
| **`open`** | 打开新标签页 | `browser(action="open", targetUrl="https://...")` | ✅ |
| **`close`** | 关闭浏览器会话 | `browser(action="close")` | ✅ |
| **`start`** | 启动浏览器 | `browser(action="start", profile="chrome")` | ✅ |
| **`stop`** | 停止浏览器 | `browser(action="stop")` | ✅ |
| **`focus`** | 聚焦浏览器窗口 | `browser(action="focus", targetId="...")` | ✅ |
| **`navigate`** | 导航到 URL | `browser(action="navigate", targetUrl="...")` | ✅ |
| **`status`** | 获取浏览器状态 | `browser(action="status", profile="chrome")` | ✅ |
| **`tabs`** | 列出所有标签页 | `browser(action="tabs", profile="chrome")` | ✅ |
| **`snapshot`** | 获取页面 DOM 结构 | `browser(action="snapshot", refs="role")` | ✅ |
| **`screenshot`** | 截图 | `browser(action="screenshot")` | ✅ |
| **`pdf`** | 生成 PDF | `browser(action="pdf")` | ✅ |
| **`act` (evaluate only)** | 执行 JS 只读查询 | `browser(action="act", request={"kind":"evaluate", "fn":"() => document.title"})` | ⚠️ 仅限只读 |

### ❌ 禁止使用的动作（自动化页面内容）

| 动作 | 用途 | 为何禁止 |
|------|------|----------|
| **`act` (click/fill/type/press/hover/drag/select/resize)** | 直接操作页面元素 | 这是自动化，违反规则 |
| **`upload`** | 文件上传 | 自动化 |
| **`dialog`** | 处理对话框 | 自动化 |
| **`act` (evaluate 写入)** | 修改 DOM 或页面状态 | 绕过模拟层，禁止 |

---

## 🔧 Browser 工具参数速查

### 通用参数（所有 action）

| 参数 | 类型 | 说明 | 是否常用 |
|------|------|------|----------|
| `profile` | `string` | 配置文件："chrome"（Relay）、"openclaw"（独立） | ⭐⭐⭐ |
| `target` | `"sandbox" \| "node" \| "host"` | 执行位置 | 可选 |
| `targetId` | `string` | 标签页 ID（从 `tabs` 获取） | ⭐⭐ |
| `node` | `string` | 节点标识（node-hosted） | 罕见 |

---

### `snapshot` 专属参数

| 参数 | 类型 | 默认 | 说明 | 推荐值 |
|------|------|------|------|--------|
| `refs` | `"role" \| "aria"` | `"role"` | 引用格式 | `"aria"`（更稳定） |
| `compact` | `boolean` | `false` | 紧凑输出 | `false` |
| `depth` | `number` | `null` | 递归深度 | 默认（完整） |
| `interactive` | `boolean` | `false` | 仅可交互元素 | `false` |
| `fullPage` | `boolean` | `false` | 包含视窗外 | `false` |

**示例**：
```python
browser(action="snapshot", refs="aria", interactive=True)
# 返回可交互元素列表，使用 aria-ref（稳定）
```

---

### `act` 的 `request` 结构（仅 evaluate 允许）

```json
{
  "kind": "evaluate",
  "fn": "() => { return document.title; }"
}
```

**禁止**：
```json
{
  "kind": "evaluate",
  "fn": "() => { document.querySelector('#kw').value = 'AI'; }"  // ❌ 写入
}
```

---

## 📊 `snapshot` 返回结构

```json
{
  "refs": [
    {
      "ref": "e1",
      "role": "link",
      "name": "百度首页",
      "children": []
    },
    {
      "ref": "e6",
      "role": "textbox",
      "name": ""
    },
    {
      "ref": "e7",
      "role": "button",
      "name": "百度一下"
    }
  ]
}
```

**重要**：
- ❌ **没有** `x, y, width, height` 坐标
- ✅ 有 `ref` 可用于 `act`（但那是自动化，禁止）
- ✅ 有 `name` 可用于语义定位（知道哪个是搜索框）

---

## 🎯 坐标获取的正确方式（核心难点）

### 问题
`snapshot` 不提供坐标，`evaluate` 的 `getBoundingClientRect()` 在某些网站（如百度）返回 `{0,0}`。

### 解决方案：视觉识别定位法（通用 fallback）

**三步流程**：
1. **截图** → `py scripts/screenshot.py > screenshot.png`
2. **视觉识别** → 用 Kimi `image` 工具分析截图，返回控件中心坐标
   ```json
   {
     "element": "搜索框",
     "center": [x, y],
     "bbox": [left, top, width, height],
     "confidence": 0.95
   }
   ```
3. **模拟点击** → `py scripts/click.py <x> <y>`

**为什么通用**：
- ✅ 不依赖 DOM API（解决几何返回零的问题）
- ✅ 不依赖 UIA（解决看不到网页内元素的问题）
- ✅ 像人一样"看"屏幕找控件
- ✅ 适用于任何网站、任何控件

**Prompt 示例**：
```text
请分析这张截图，找出百度首页的搜索输入框。
返回纯 JSON：
{
  "search_box": {
    "center": [x, y],
    "bbox": [left, top, width, height]
  }
}
```

---

## 必读注意事项

## 模拟操作脚本来源

本 skill 使用的脚本是**模拟真人操作**的鼠标键盘脚本，复制自 windows-control skill 但独立管理。

脚本位于：`~/.openclaw/workspace/skills/browser-agent/scripts/`

> 注意：这些脚本是本 skill 的一部分，不是调用 windows-control skill。两个 skill 隔离管理。

## Core Workflow（核心工作流）

```
1. 截图：使用 screenshot.py 截取屏幕
2. 识别：image 工具分析截图（模型直接看图）
3. 操作：使用 click_text.py / type_text.py / scroll.py 等脚本
4. 验证：截图确认结果
5. 重复直到完成
```

**关键原则**：
- 每一步都要截图让模型看图
- 使用本 skill 的 scripts/ 文件夹中的脚本
- 禁止用 browser snapshot/tabs/relay 等任何自动化接口
- 用 click_text.py 通过文字点击（像人找按钮）

## 脚本调用方式

所有脚本位于 `~/.openclaw/workspace/skills/browser-agent/scripts/`

### 📸 增强功能：自动截图与元数据

**所有操作脚本都支持**：
- ✅ **操作前后自动截图**（before/after 对比）
- ✅ **元数据 JSON 记录**（参数、时间戳、截图路径）
- ✅ **自定义输出目录**（`--output-dir PATH`）
- ✅ **会话追踪**（session_id 分组）

**输出目录结构**：
```
tmp/_artifacts/screenshots/
├── click_before_20260227_122040_315.png    # 操作前截图
├── click_after_20260227_122040_511.png     # 操作后截图
├── click_20260227_122040.json              # 元数据（含参数和截图路径）
└── ...
```

**元数据 JSON 示例**：
```json
{
  "operation": "click",
  "params": {"x": 500, "y": 300, "button": "left", "clicks": 1},
  "timestamp": "2026-02-27T12:20:40",
  "before_screenshot": {"path": "...", "filename": "..."},
  "after_screenshot": {"path": "...", "filename": "..."}
}
```

---

### 截图操作

| 命令 | 用途 |
|------|------|
| `py scripts/screenshot.py` | 截取当前屏幕（返回 base64 + 保存文件） |
| `py scripts/screenshot.py --output-dir "PATH"` | 指定输出目录 |
| `py scripts/screenshot.py --filename "name.png"` | 指定文件名 |

### 点击操作

| 命令 | 用途 |
|------|------|
| `py scripts/click.py 500 300` | 点击坐标 (500, 300)，自动截图 |
| `py scripts/click.py 500 300 right` | 右键点击 |
| `py scripts/click.py 500 300 left 2` | 双击 |
| `py scripts/click.py 500 300 --output-dir "PATH"` | 指定截图输出目录 |
| `py scripts/click_text.py "按钮文字"` | 通过文字点击（全局） |
| `py scripts/click_text.py "确定" "Chrome"` | 在指定窗口点击 |
| `py scripts/click_element.py --list` | 列出所有可点击元素 |
| `py scripts/click_element.py "保存"` | 按名称点击元素 |

### 输入操作

| 命令 | 用途 |
|------|------|
| `py scripts/type_text.py "内容"` | 输入文字，自动截图 |
| `py scripts/type_text.py "AI" --output-dir "PATH"` | 指定截图输出目录 |
| 先点击输入框后再输入 | 点击输入框 → 输入文字 |

**注意**：用户默认输入法为中文双拼（自然码）。执行英文输入前，应先切换到英文输入法。

### 按键操作

| 命令 | 用途 |
|------|------|
| `py scripts/key_press.py "enter"` | 按回车键，自动截图 |
| `py scripts/key_press.py "tab"` | 按 Tab 键 |
| `py scripts/key_press.py "ctrl+s"` | 组合键（Ctrl+S） |
| `py scripts/key_press.py "esc"` | 按 Esc 键 |
| `py scripts/key_press.py "enter" --output-dir "PATH"` | 指定截图输出目录 |

### 滚动操作

| 命令 | 用途 |
|------|------|
| `py scripts/scroll.py down 3` | 向下滚动 3 格 |
| `py scripts/scroll.py up 5` | 向上滚动 5 格 |
| `py scripts/scroll.py bottom` | 滚动到底部 |
| `py scripts/scroll.py top` | 滚动到顶部 |

### 窗口管理

| 命令 | 用途 |
|------|------|
| `py scripts/focus_window.py "Chrome"` | 聚焦浏览器窗口 |
| `py scripts/close_window.py "标题"` | 关闭窗口 |
| `py scripts/maximize_window.py` | 最大化窗口 |
| `py scripts/minimize_window.py` | 最小化窗口 |
| `py scripts/list_windows.py` | 列出所有窗口 |
| `py scripts/get_active_window.py` | 获取当前活动窗口 |

### 读取内容

| 命令 | 用途 |
|------|------|
| `py scripts/find_text.py "文字"` | 找文字坐标 |
| `py scripts/read_window.py "Chrome"` | 读取窗口内容（Windows UI 自动化） |
| `py scripts/read_webpage.py "Chrome"` | 读取网页内容（含按钮/链接坐标） |
| `py scripts/read_ui_elements.py "Chrome"` | 读取 UI 元素（按钮/链接等） |
| `py scripts/read_region.py x y w h` | 读取指定区域（需 Tesseract） |

### 对话框处理

| 命令 | 用途 |
|------|------|
| `py scripts/handle_dialog.py list` | 列出所有对话框 |
| `py scripts/handle_dialog.py read` | 读取对话框内容 |
| `py scripts/handle_dialog.py click "确定"` | 点击对话框按钮 |
| `py scripts/handle_dialog.py type "内容"` | 输入到对话框 |
| `py scripts/handle_dialog.py dismiss` | 关闭对话框 |

### 鼠标与键盘

| 命令 | 用途 |
|------|------|
| `py scripts/mouse_move.py 500 300` | 移动鼠标到坐标 |
| `py scripts/key_press.py "enter"` | 按键 |
| `py scripts/key_press.py "ctrl+s"` | 组合键 |
| `py scripts/drag.py x1 y1 x2 y2` | 拖拽 |

### 等待操作

| 命令 | 用途 |
|------|------|
| `py scripts/wait_for_text.py "文字"` | 等待文字出现 |
| `py scripts/wait_for_window.py "标题"` | 等待窗口出现 |

---

## 🐍 Python 模块用法（高级）

在自定义脚本中使用 `AutoScreenshotter` 模块：

```python
from auto_screenshot import AutoScreenshotter

# 初始化（自动创建默认输出目录）
shot = AutoScreenshotter(output_dir="C:/path/to/output")

# 方法 1: 自动序列（推荐）
result = shot.capture_sequence(
    operation_type="click",
    params={"x": 500, "y": 300},
    execute_fn=lambda: pyautogui.click(500, 300)
)

print(f"Success: {result['success']}")
print(f"Before: {result['before']['path']}")
print(f"After: {result['after']['path']}")
print(f"Metadata: {result['metadata']}")

# 方法 2: 手动控制
before = shot.capture("before")
# ... 执行操作 ...
after = shot.capture("after")
shot.save_metadata("custom_op", {"note": "test"}, before, after)
```

详细文档见：`scripts/README.md`

---

## 🔄 混合模式：通过 Browser Relay 获取元素坐标

### 何时使用此模式

- ✅ 需要操作**网页内部元素**（搜索框、链接、按钮）
- ✅ 已安装 Browser Relay 扩展
- ✅ 可以手动或自动激活 Relay
- ✅ 遵守"只读数据 + 模拟操作"原则

### 核心工作流

```
1. 激活 Browser Relay（扩展按钮）
2. 使用 browser 工具 snapshot 获取 DOM 元素列表（含坐标）
3. 解析坐标，转换到屏幕坐标系
4. 使用 click.py 按坐标模拟点击
5. 截图或 read_window 验证结果
```

### 步骤详解

#### Step 1：激活 Browser Relay

**方式 A - 手动激活（推荐）**
用户点击 Chrome 工具栏上的 "OpenClaw Browser Relay" 按钮一次，之后保持激活状态。

**方式 B - 自动激活（UIA）**
```bash
py scripts/click_element.py "OpenClaw Browser Relay"
```
等待用户确认授权弹窗。

#### Step 2：获取页面元素

通过 `browser` 工具（OpenClaw 内置）获取元素：

```python
# 使用 snapshot 动作
browser(
    action="snapshot",
    profile="openclaw",     # 必须使用 openclaw 配置文件
    target="host",
    refs="role",            # 或 "aria"
    interactive=True
)
```

返回结构（简化）：
```json
{
  "refs": [
    {"ref": "button1", "role": "button", "name": "百度一下", "x": 100, "y": 200},
    {"ref": "input1", "role": "textbox", "name": "搜索框", "x": 50, "y": 150}
  ]
}
```

#### Step 3：坐标转换

`browser` snapshot 返回的是**相对视口的坐标**。需要转换为**屏幕绝对坐标**：

```
绝对坐标 = (元素.x + 浏览器窗口左上角.x, 元素.y + 浏览器窗口左上角.y)
```

获取浏览器窗口位置：
```bash
py scripts/get_active_window.py  # 输出窗口标题和位置
# 或使用 UIA 读取 Chrome 窗口的 rectangle
```

#### Step 4：模拟点击

```bash
# 计算出的绝对坐标
py scripts/click.py <screen_x> <screen_y>
```

#### Step 5：验证

```bash
py scripts/screenshot.py  # 保存截图对比
py scripts/read_window.py "Chrome"  # 读取 URL 或内容
```

### 完整示例：百度搜索（混合模式）

```bash
# 1. 聚焦 Chrome
py scripts/focus_window.py "Chrome"

# 2. 等待页面加载
py scripts/wait_for_text.py "百度一下" 10

# 3. 通过 browser 工具获取元素（此处以伪代码表示，实际需调用 OpenClaw API）
# 假设我们得到了：
#   input_search: { x: 100, y: 150 }   # 搜索框（视口坐标）
#   button_baidu: { x: 300, y: 150 }  # 百度一下按钮

# 4. 获取 Chrome 窗口位置（假设为 0,0 简化）
# 实际应通过 UIA 获取：read_ui_elements.py 或 get_active_window.py

# 5. 点击搜索框（绝对坐标）
py scripts/click.py 100 150

# 6. 输入法切换 + 输入
py scripts/input_method.py "en"
py scripts/type_text.py "AI"

# 7. 点击搜索按钮
py scripts/click.py 300 150

# 8. 验证
py scripts/wait_for_text.py "相关" 10
```

### 参考系校准（避免坐标偏移）

由于 `browser snapshot` 的坐标可能因设备、窗口位置、缩放比例而有偏差，**必须进行参考校准**：

```bash
# 算法：找一个已知位置的元素（如"百度一下"按钮），点击后验证是否触发了搜索
# 如果未触发，在 ±20px 范围内微调重新点击，直到成功，记录偏移量 (dx, dy)
# 后续所有坐标应用此偏移量
```

---

## 🖼️ 视觉识别定位法（通用 fallback）

### 适用场景

当标准几何 API（`getBoundingClientRect`, `elementFromPoint`）无法返回有效坐标时（如百度首页搜索框），使用视觉识别。

### 核心原理

1. 用 `screenshot.py` 截取当前屏幕
2. 用 Kimi 图像识别模型分析截图，找出目标控件
3. 要求 Kimi 返回控件的**中心坐标**（与图片 1:1 对应）
4. 用 `click.py` 点击该坐标（模拟鼠标）

### 步骤

```bash
# 1. 截图
py scripts/screenshot.py > screenshot.png.base64
# （或直接保存为 PNG 文件）

# 2. 调用 Kimi 识别（示例代码，需在 agent 脚本中实现）
image(
    image="screenshot.png",
    prompt="""
请分析这张截图，找出 [目标控件]（例如：搜索框、按钮）。
返回纯 JSON，格式：
{
  "element": "搜索框",
  "center": [x, y],
  "bbox": [left, top, width, height],
  "confidence": 0.9
}
"""
)

# 3. 解析 Kimi 返回的 JSON，提取 center 坐标 (x, y)
# 4. 点击坐标
py scripts/click.py <x> <y>
```

### 坐标转换

截图是**全屏截图**，坐标直接对应屏幕像素，无需转换。
- `x` 为从屏幕左侧开始的列数
- `y` 为从屏幕顶部开始的行数

### 示例：百度搜索框定位

```python
# 截图
screenshot = screenshot.py()  # base64

# 识别
result = image(
    image=screenshot,
    prompt="""
在截图中找到百度首页的搜索输入框。
返回 JSON：
{
  "search_box": {
    "center": [x, y],
    "bbox": [left, top, width, height]
  }
}
""",
    model="kimi-coding/k2p5"  # 使用支持图像的 Kimi
)

# 解析
coord = result['search_box']['center']
click.py(coord[0], coord[1])
```

### 注意事项

⚠️ **Kimi 必须可用**：确保 `image` 工具已配置支持图像的模型（如 Kimi）
⚠️ **截图清晰**：屏幕分辨率稳定，避免模糊
⚠️ **置信度检查**：如果 `confidence < 0.8`，重新截图或人工介入
⚠️ **坐标校准**：首次使用可能需要手动验证坐标准确性

### 优势与局限

**优势**：
- ✅ 通用性强（任何网站，任何控件）
- ✅ 不依赖 DOM API 或 UIA
- ✅ 像人一样"看"屏幕

**局限**：
- ❌ 依赖视觉模型（Kimi）的识别精度
- ❌ 截图可能受分辨率、缩放影响
- ❌ 动态内容（动画、视频）可能干扰识别

---

## 故障排除（详细）

### 注意事项

⚠️ 必须是 `profile="openclaw"`，避免使用 chrome relay（用户偏好）
⚠️ `browser` 工具只用于 `snapshot`（只读），禁止 `act` 操作
⚠️ 坐标转换要考虑滚动偏移和浏览器窗口位置
⚠️ 每次浏览器窗口位置变化后需重新校准

---

## 异常处理（详细）

### AI 可自动处理

| 情况 | 处理方式 |
|------|----------|
| **图形验证码** | image 识别图形内容 → 自动拖动滑块 / 点击验证 |
| **页面加载慢** | 等待 2-3 秒后重试 |
| **网络超时** | 重试 2-3 次 |
| **元素找不到** | 滚动页面 + 等待 + 重试 |
| **弹窗广告** | 找关闭按钮点击（关闭/取消/我知道了） |
| **IP 限制** | 降速操作，等待后重试 |
| **Cookie 过期** | 刷新页面重新操作 |

### 需要询问用户

| 情况 | 处理方式 |
|------|----------|
| **短信验证码** | 告知用户需要手机验证码，请用户提供 |
| **人脸识别** | 告知用户需要活体验证，请用户完成 |
| **账号登录** | 询问是否有账户，是否需要提供账号密码 |
| **支付验证** | 告知用户需要支付验证，请用户完成 |
| **双因素认证** | 告知用户需要 2FA，请用户提供验证码 |

### 登录处理流程

1. 截图让模型识别
2. 如有登录弹窗 → 提醒用户
3. 询问：是否有账户？是否需要登录？
4. 如需登录 → 询问账号密码或让用户自己登录

### 验证码处理流程

1. 截图让模型识别验证码类型
2. 图形验证码（滑块/点选）→ 尝试自动完成
3. 邮箱验证码 → 自动登录邮箱获取
4. 短信/人脸 → 提醒用户

## 工作流示例

### 示例 1：百度搜索（修复版）

```
任务：在百度搜索"人工智能"，点击第一个结果

步骤：
1. py scripts/focus_window.py "Chrome"  # 确保浏览器聚焦
2. py scripts/wait_for_text.py "百度一下" 10  # 等待页面加载
3. py scripts/click_element.py "搜索框"      # 点击搜索框（使用元素定位）
4. py scripts/input_method.py "en"          # 切换到英文输入法
5. py scripts/type_text.py "AI"             # 输入英文关键词（或中文需切换为 zh）
6. py scripts/key_press.py "enter"          # 按回车搜索
7. py scripts/wait_for_text.py "相关" 10    # 等待搜索结果加载
8. py scripts/screenshot.py                 # 截图（备用：read_webpage.py）
9. image path=<截图> prompt="描述搜索结果，找到第一个链接"
10. py scripts/click_text.py "第一个结果标题"
11. 验证完成
```

> **注意事项**：
> - 使用 `click_element.py` 替代坐标点击，避免分辨率依赖
> - 输入中文前使用 `input_method.py "zh"` 切换输入法
> - 关键步骤后使用 `wait_for_text.py` 确保页面加载完成

### 示例 2：自动登录网站

```
任务：登录 GitHub

步骤：
1. py scripts/screenshot.py
2. image path=<截图> prompt="描述页面，找到用户名输入框和密码输入框"
3. py scripts/click_text.py "Username" → 点击用户名框
4. py scripts/type_text.py "账号" → 输入账号
5. py scripts/click_text.py "Password" → 点击密码框
6. py scripts/type_text.py "密码" → 输入密码
7. py scripts/click_text.py "Sign in"
8. py scripts/screenshot.py
9. image path=<截图> prompt="验证是否登录成功"
```

### 示例 3：处理滑块验证码

```
任务：登录需要滑块验证的网站

步骤：
1. 登录失败，检测到滑块验证
2. py scripts/screenshot.py
3. image path=<截图> prompt="识别滑块验证码，找到滑块和缺口位置"
4. 计算滑动距离
5. py scripts/drag.py <起点> <终点> → 拖动滑块
6. py scripts/screenshot.py
7. image path=<截图> prompt="验证是否通过验证"
```

### 示例 4：读取网页内容

```
任务：从网页提取信息

步骤：
1. py scripts/read_webpage.py "Chrome" → 获取网页结构化内容
2. 或 py scripts/read_ui_elements.py "Chrome" → 获取按钮/链接
3. 根据内容决定下一步操作
```

## 禁止事项

- ❌ 禁止使用 browser act/click/fill/evaluate 等直接 DOM 操作（自动化）
- ✅ 允许使用 browser snapshot/tabs 只读数据（元素坐标获取）
- ❌ 禁止调用 windows-control skill（脚本已复制到本 skill）
- ❌ 禁止用 ref 定位点击（应使用坐标或元素名）
- ❌ 禁止安装浏览器插件（除 Browser Relay）
- ❌ 禁止不截图关键的验证步骤
- ❌ 禁止使用开发者工具（保持纯净）

## 本 Skill 脚本文件列表

```
scripts/
├── click.py              # 点击指定坐标
├── click_element.py     # 按名称点击元素
├── click_text.py        # 通过文字点击
├── close_window.py      # 关闭窗口
├── drag.py              # 拖拽操作
├── find_text.py         # 查找文字坐标
├── focus_window.py      # 聚焦窗口
├── get_active_window.py # 获取当前活动窗口
├── handle_dialog.py     # 处理对话框
├── input_method.py      # 切换输入法
├── key_press.py         # 按键操作
├── list_windows.py      # 列出所有窗口
├── maximize_window.py   # 最大化窗口
├── minimize_window.py   # 最小化窗口
├── mouse_move.py        # 鼠标移动
├── read_region.py       # 读取区域内容
├── read_ui_elements.py  # 读取UI元素
├── read_webpage.py      # 读取网页内容
├── read_window.py       # 读取窗口内容
├── screenshot.py        # 屏幕截图（增强版，多方法降级）
├── scroll.py            # 滚动操作
├── type_text.py         # 输入文字
├── wait_for_text.py     # 等待文字出现
└── wait_for_window.py   # 等待窗口出现
```

## 依赖

- **browser 工具** (只读模式)：用于通过 Browser Relay 获取页面元素坐标和位置信息
  - 必须使用 `profile="openclaw"` 和 `target="host"`
  - 仅允许 `snapshot`、`tabs`、`status` 动作
  - 禁止 `act`、`click`、`fill` 等操作动作
- **pyautogui**（已安装）：模拟鼠标键盘
- **pillow**（已安装）：图像处理（截图）
- **可选：image 工具**（如 Kimi）：用于截图视觉分析（备选）

## 故障排除（常见问题）

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| **截图失败** | 权限不足、无活跃窗口 | 以管理员身份运行 OpenClaw；或使用 `read_window.py` 替代 |
| **中文乱码** | 输入法状态错误 | 先按 `Shift` 切换到英文输入法；或使用 `key_press.py "shift"` |
| **点击位置不对** | 坐标变化、窗口未最大化 | 确保浏览器最大化；使用 `click_element.py` 替代坐标点击 |
| **页面无响应** | 页面检测到自动化、网络慢 | 降低操作速度（增加 duration）；加入延迟等待；避免快速连续操作 |
| **元素找不到** | 页面动态加载、滚动未到位 | 先滚动到元素位置；使用 `wait_for_text.py` |

## 性能优化建议

- 优先使用 `read_window.py` 或 `read_webpage.py` 而非截图，速度快且准确
- 使用 `click_element.py` 替代坐标点击，避免分辨率变化导致失效
- 对于大型页面，分段读取，逐步滚动
- 遇到"正在加载"提示时，等待 `wait_for_text.py` 再继续

## 最佳实践总结

### 标准工作流（推荐）
```
1. 聚焦窗口：         py scripts/focus_window.py "Chrome"
2. 等待加载：         py scripts/wait_for_text.py "预期文字"
3. 读取内容：         py scripts/read_webpage.py "Chrome"
4. 分析并操作：       根据 text 内容点击/输入
5. 切换输入法：       需要时运行 py scripts/input_method.py "en|zh"
6. 验证结果：         截图或再次读取
7. 循环直到完成
```

### 组合技巧
| 场景 | 推荐脚本组合 |
|------|-------------|
| **信息提取** | read_window.py → read_webpage.py → read_ui_elements.py |
| **复杂点击** | click_element.py（优于 click_text.py 和 click.py） |
| **表单填写** | click_element.py → input_method.py → type_text.py |
| **长页面** | scroll.py + wait_for_text.py + 分段读取 |
| **错误恢复** | list_windows.py → focus_window.py → read_window.py |

### 安全与稳定
- ✅ 使用 `wait_for_text.py` 避免竞态条件
- ✅ 使用 `click_element.py` 替代固定坐标
- ✅ 使用 `read_webpage.py` 替代截图作为主要感知手段
- ❌ 避免短时间内重复点击同一元素
- ❌ 避免在页面未完全加载时操作
