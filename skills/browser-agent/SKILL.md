---
name: browser-agent
description: 拟人化浏览器代理。让 AI 像真人一样操作浏览器，绕过网站风控检测。核心方式：截图 → 模型看图 → click_text.py 点击。
---

# Browser Agent

让 AI 像真人一样操作浏览器，完全拟人化，绕过网站风控。

## Core Workflow（核心工作流）

```
1. 截图：browser screenshot
2. 识别：image 工具分析截图（模型直接看图）
3. 操作：click_text.py / type_text.py / scroll.py
4. 验证：截图确认结果
5. 重复直到完成
```

**关键原则**：
- 每一步都要截图让模型看图
- 不要用 browser snapshot 直接读取页面结构
- 用 click_text.py 通过文字点击（像人找按钮）
- 浏览器保持纯净，不安装插件

## Commands

### 截图与识别

| 命令 | 用途 |
|------|------|
| `browser action=screenshot` | 截取当前页面 |
| `image path=<截图> prompt="描述页面"` | 让模型看图分析 |

### 点击操作

| 命令 | 用途 |
|------|------|
| `py click_text.py "按钮文字"` | 通过文字点击 |
| `py click_text.py "文字" --window "Chrome"` | 在指定窗口点击 |

### 输入操作

| 命令 | 用途 |
|------|------|
| `py type_text.py "内容"` | 输入文字（当前焦点） |
| 先 `py click_text.py "输入框"` 再 `py type_text.py "内容"` | 点击后再输入 |

### 滚动操作

| 命令 | 用途 |
|------|------|
| `py scroll.py down 3` | 向下滚动 3 格 |
| `py scroll.py up 5` | 向上滚动 5 格 |

### 窗口管理

| 命令 | 用途 |
|------|------|
| `py focus_window.py "Chrome"` | 聚焦浏览器窗口 |
| `py close_window.py "title"` | 关闭窗口 |

### 读取内容

| 命令 | 用途 |
|------|------|
| `py find_text.py "文字"` | 找文字坐标 |
| `py read_window.py "Chrome"` | 读取窗口内容 |

### 对话框处理

| 命令 | 用途 |
|------|------|
| `py handle_dialog.py list` | 列出所有对话框 |
| `py handle_dialog.py click "确定"` | 点击对话框按钮 |
| `py handle_dialog.py dismiss` | 关闭对话框 |

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

### 需要询问用户

| 情况 | 处理方式 |
|------|----------|
| **短信验证码** | 告知用户需要手机验证码，请用户提供 |
| **人脸识别** | 告知用户需要活体验证，请用户完成 |
| **账号登录** | 询问是否有账户，是否需要提供账号密码 |
| **支付验证** | 告知用户需要支付验证，请用户完成 |

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

### 示例 1：百度搜索

```
任务：在百度搜索"人工智能"，点击第一个结果

步骤：
1. browser action=open url=https://www.baidu.com
2. browser action=screenshot → 获取截图路径
3. image path=<截图> prompt="描述页面，找到搜索框和搜索按钮"
4. py click_text.py "搜索框文字" → 点击搜索框
5. py type_text.py "人工智能" → 输入关键词
6. py click_text.py "百度一下" → 点击搜索按钮
7. browser action=screenshot
8. image path=<截图> prompt="描述搜索结果，找到第一个链接"
9. py click_text.py "第一个结果标题"
10. 验证完成
```

### 示例 2：自动登录网站

```
任务：登录 GitHub

步骤：
1. browser action=open url=https://github.com/login
2. browser action=screenshot
3. image path=<截图> prompt="描述页面，找到用户名输入框和密码输入框"
4. py click_text.py "用户名输入框" → 点击用户名框
5. py type_text.py "账号" → 输入账号
6. py click_text.py "密码输入框" → 点击密码框
7. py type_text.py "密码" → 输入密码
8. py click_text.py "登录按钮"
9. browser action=screenshot
10. image path=<截图> prompt="验证是否登录成功"
```

### 示例 3：信息提取

```
任务：从 Wikipedia 提取人工智能词条的主要内容

步骤：
1. browser action=open url=https://en.wikipedia.org/wiki/Artificial_intelligence
2. browser action=screenshot
3. image path=<截图> prompt="描述页面标题和主要内容"
4. py scroll.py down 3 → 向下滚动
5. browser action=screenshot
6. image path=<截图> prompt="描述当前页面内容"
7. 重复滚动和截图直到获取足够信息
```

## 禁止事项

- ❌ 禁止用 browser snapshot 直接读取页面结构
- ❌ 禁止用 ref 定位点击
- ❌ 禁止安装浏览器插件
- ❌ 禁止不截图就直接操作

## 依赖工具

- browser（截图、打开网页）
- image（模型看图分析）
- windows-control 脚本（click_text.py, type_text.py, scroll.py 等）
