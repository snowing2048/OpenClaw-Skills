# Browser Agent Scripts - 使用说明

## 📁 目录结构

```
skills/browser-agent/
├── scripts/
│   ├── auto_screenshot.py    # 通用截图模块（核心）
│   ├── screenshot.py         # 截图脚本
│   ├── click.py              # 点击脚本（带自动截图）
│   ├── type_text.py          # 输入脚本（带自动截图）
│   ├── key_press.py          # 按键脚本（带自动截图）
│   └── ...
└── tmp/
    └── _artifacts/
        └── screenshots/      # 默认截图输出目录
            ├── click_before_20260227_120000.png
            ├── click_after_20260227_120001.png
            ├── click_20260227_120001.json
            └── ...
```

---

## 🚀 快速开始

### 基本用法（使用默认输出目录）

```bash
# 点击坐标 (500, 300)
py scripts/click.py 500 300

# 输入文字
py scripts/type_text.py "Hello World"

# 按回车键
py scripts/key_press.py "enter"

# 截图
py scripts/screenshot.py
```

**自动截图**：每个操作前后都会自动截图，保存到 `tmp/_artifacts/screenshots/`

---

### 指定输出目录

```bash
# 使用 --output-dir 或 -o 参数
py scripts/click.py 500 300 --output-dir "C:/Users/OpenClaw/Desktop/test_run"
py scripts/type_text.py "AI" -o "C:/path/to/output"
py scripts/key_press.py "ctrl+s" --output-dir "./screenshots"
```

---

## 📸 自动截图功能

### 每个脚本都会自动生成：

1. **操作前截图**：`{operation}_before_{timestamp}.png`
2. **操作后截图**：`{operation}_after_{timestamp}.png`
3. **元数据 JSON**：`{operation}_{timestamp}.json`

### 元数据 JSON 示例

```json
{
  "operation": "click",
  "params": {
    "x": 616,
    "y": 166,
    "button": "left",
    "clicks": 1
  },
  "timestamp": "2026-02-27T12:00:00.123456",
  "session_id": "20260227_120000",
  "before_screenshot": {
    "success": true,
    "path": "C:/.../click_before_20260227_120000.png",
    "filename": "click_before_20260227_120000.png",
    "timestamp": "20260227_120000"
  },
  "after_screenshot": {
    "success": true,
    "path": "C:/.../click_after_20260227_120001.png",
    "filename": "click_after_20260227_120001.png",
    "timestamp": "20260227_120001"
  }
}
```

---

## 🔧 Python 模块用法

### 在自定义脚本中使用 `AutoScreenshotter`

```python
from auto_screenshot import AutoScreenshotter

# 初始化
shot = AutoScreenshotter(output_dir="C:/path/to/output")

# 方法 1: 手动截图
before = shot.capture("before")
# ... 执行操作 ...
after = shot.capture("after")

# 方法 2: 自动序列（推荐）
result = shot.capture_sequence(
    operation_type="click",
    params={"x": 500, "y": 300},
    execute_fn=lambda: pyautogui.click(500, 300)
)

print(f"Success: {result['success']}")
print(f"Before: {result['before']['path']}")
print(f"After: {result['after']['path']}")
print(f"Metadata: {result['metadata']}")

# 保存元数据
shot.save_metadata("custom_op", {"note": "test"}, before, after)
```

---

### 快速截图函数

```python
from auto_screenshot import quick_screenshot

# 快速截图，返回 base64 和文件路径
result = quick_screenshot(
    output_dir="C:/path/to/output",
    filename="my_screenshot.png"
)

print(result["base64"])  # base64 编码
print(result["path"])    # 文件路径
```

---

## 📋 完整工作流示例

### 百度搜索任务

```bash
# 1. 创建任务目录
mkdir "C:/Users/OpenClaw/Desktop/baidu_test_20260227"

# 2. 打开百度
browser(action="open", targetUrl="https://www.baidu.com/")

# 3. 截图识别搜索框
py scripts/screenshot.py --output-dir "C:/Users/OpenClaw/Desktop/baidu_test_20260227"

# 4. 用 image 工具识别坐标（返回 {"center": [616, 166]}）

# 5. 点击搜索框
py scripts/click.py 616 166 --output-dir "C:/Users/OpenClaw/Desktop/baidu_test_20260227"

# 6. 输入 "AI"
py scripts/type_text.py "AI" --output-dir "C:/Users/OpenClaw/Desktop/baidu_test_20260227"

# 7. 按回车
py scripts/key_press.py "enter" --output-dir "C:/Users/OpenClaw/Desktop/baidu_test_20260227"

# 8. 验证结果
py scripts/screenshot.py --output-dir "C:/Users/OpenClaw/Desktop/baidu_test_20260227"
```

**输出目录结构**：
```
baidu_test_20260227/
├── screenshot_20260227_120000.png
├── click_before_20260227_120001.png
├── click_after_20260227_120002.png
├── click_20260227_120002.json
├── type_before_20260227_120003.png
├── type_after_20260227_120004.png
├── type_20260227_120004.json
├── keypress_before_20260227_120005.png
├── keypress_after_20260227_120006.png
└── keypress_20260227_120006.json
```

---

## 🎯 优势

### 1. **调试友好**
- 每次操作都有前后对比图
- 元数据 JSON 记录所有参数
- 可按时间线回溯整个操作流程

### 2. **视觉识别支持**
- 截图自动保存，方便后续 `image` 工具调用
- 坐标识别更准确（全屏截图，非浏览器内截图）
- 支持多轮识别 - 操作 - 验证循环

### 3. **维护方便**
- 所有操作记录结构化存储
- 可按会话（session_id）分组
- JSON 元数据易于程序化处理

### 4. **向后兼容**
- 保留原有命令行参数
- `screenshot.py` 仍输出 base64（管道兼容）
- 默认输出目录自动创建

---

## ⚠️ 注意事项

1. **磁盘空间**：每次操作生成 2 张图 + 1 个 JSON，长时间运行注意清理
2. **性能**：截图会增加操作耗时（约 0.5-1 秒/次）
3. **权限**：需要屏幕截图权限（Windows 设置 → 隐私 → 屏幕截图）
4. **并发**：多进程运行时建议使用不同输出目录

---

## 🔍 调试技巧

### 查看最近的操作记录

```powershell
# 查看最新的元数据
Get-ChildItem "tmp/_artifacts/screenshots/*.json" | Sort-LastWriteTime -Descending | Select-Object -First 5

# 查看某个操作的所有截图
Get-ChildItem "tmp/_artifacts/screenshots/click_*.png"
```

### 分析操作流程

```python
import json
from pathlib import Path

# 读取所有元数据
screenshots_dir = Path("tmp/_artifacts/screenshots")
operations = []

for meta_file in screenshots_dir.glob("*.json"):
    with open(meta_file) as f:
        operations.append(json.load(f))

# 按时间排序
operations.sort(key=lambda x: x["timestamp"])

# 打印操作序列
for op in operations:
    print(f"{op['timestamp']} - {op['operation']}: {op['params']}")
```

---

## 📞 支持

遇到问题？检查：
1. 输出目录是否有写入权限
2. 是否安装了 `pyautogui` 和 `Pillow`
3. Windows 截图权限是否开启
