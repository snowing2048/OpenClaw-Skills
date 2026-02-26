# Browser Agent Skill - 拟人化浏览器代理

## 概述

AI 浏览器代理工具，让 AI 像人一样操作浏览器，绕过网站风控。

## 操作规范（最重要）

### 核心原则：截图 + OCR

**每一步都用截图来分析页面，像真人一样"看"**

```bash
# 1. 截图
browser action=screenshot profile=openclaw targetId=<tab_id>

# 2. 用 image 工具分析截图
image path=<截图路径> prompt="描述页面内容，找到搜索框和按钮"
```

### 为什么不用 snapshot？

- 直接用 snapshot 读取页面结构会被网站风控检测到
- 必须用截图 + OCR 来模拟人眼查看页面
- 这样才能绕过严格的风控（如淘宝、京东等）

### 点击方式

使用 windows-control 的 Python 脚本通过文字点击：

```bash
# 通过文字点击（像人一样看图点击）
py click_text.py "百度一下"
py click_text.py "搜索"
py click_text.py "登录"
```

### 键盘输入

```bash
# 输入文字（先切换到英文输入法）
py type_text.py "人工智能"
```

### 页面滚动

```bash
# 滚动页面（像人一样）
py scroll.py down 3
py scroll.py up 5
```

### 浏览器要求

- 保持浏览器纯净，不安装任何插件
- 不使用任何辅助工具
- 像真人一样用眼睛看、用鼠标点

## 异常处理

### 登录限制
- 识别登录弹窗：截图 + OCR 分析
- 提醒用户并询问是否需要登录
- 可尝试直接访问搜索 URL 绕过

### 页面状态识别

| 状态 | 特征 | 处理 |
|------|------|------|
| 登录弹窗 | 登录框、二维码 | 截图分析 → 提醒用户 |
| 加载中 | loading、spinner | 截图分析 → 等待 |
| 验证码 | 滑动验证 | 截图分析 → 提醒用户 |

## 测试用例

### Task 1: 百度搜索（正确方式）

```bash
# 1. 打开百度
browser action=open profile=openclaw target=host url=https://www.baidu.com
browser action=act profile=openclaw targetId=<tab> kind=wait timeMs=2000

# 2. 截图分析页面
browser action=screenshot profile=openclaw targetId=<tab>
image path=<截图路径> prompt="描述页面内容，找到搜索框和搜索按钮的位置"

# 3. 点击搜索框（通过文字）
py click_text.py "请输入"

# 4. 输入关键词
py type_text.py "人工智能"

# 5. 点击搜索按钮（通过文字）
py click_text.py "百度一下"

# 6. 等待结果
browser action=act profile=openclaw targetId=<tab> kind=wait timeMs=2000

# 7. 截图分析结果
browser action=screenshot profile=openclaw targetId=<tab>
image path=<截图路径> prompt="描述搜索结果，找到第一个链接"

# 8. 点击第一个结果（通过文字）
py click_text.py "人工智能 - 百度百科"

# 9. 验证到达目标页面
browser action=screenshot profile=openclaw targetId=<tab>
```

### Task 2: 淘宝搜索（需登录）

```bash
# 1. 打开淘宝
browser action=open profile=openclaw target=host url=https://www.taobao.com
browser action=act profile=openclaw targetId=<tab> kind=wait timeMs=3000

# 2. 截图分析
browser action=screenshot profile=openclaw targetId=<tab>
image path=<截图路径> prompt="描述页面内容，是否有登录弹窗"

# 3. 识别登录限制 → 提醒用户
```

### Task 3: Wikipedia 信息提取

```bash
# 1. 打开 Wikipedia
browser action=open profile=openclaw target=host url=https://en.wikipedia.org/wiki/Artificial_intelligence
browser action=act profile=openclaw targetId=<tab> kind=wait timeMs=3000

# 2. 截图分析
browser action=screenshot profile=openclaw targetId=<tab>
image path=<截图路径> prompt="描述页面标题和主要内容"

# 3. 滚动浏览
py scroll.py down 3

# 4. 继续截图分析
browser action=screenshot profile=openclaw targetId=<tab>
image path=<截图路径> prompt="描述当前页面内容"
```

## 测试验证

| 任务 | 网站 | 结果 |
|------|------|------|
| 搜索测试 | 百度 | ✅ 截图+OCR方式 |
| 电商搜索 | 淘宝 | ✅ 识别登录限制 |
| 信息提取 | Wikipedia | ✅ 截图+OCR方式 |

## 通过标准

- P0: 截图 + OCR 分析 100% 使用
- P1: 通过文字点击（click_text.py）100% 使用
- P2: 登录限制识别正确提醒用户
- 浏览器保持纯净，无插件
