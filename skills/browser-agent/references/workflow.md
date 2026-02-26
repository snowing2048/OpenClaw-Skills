# Browser Agent 工作流详解

## 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 打开网页                                                 │
│    browser action=open url=<目标网址>                       │
│    browser action=wait timeMs=2000                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 截图                                                     │
│    browser action=screenshot targetId=<tab_id>              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 模型识别截图                                             │
│    image path=<截图路径> prompt="描述页面内容，找到xxx按钮" │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 执行操作（根据模型理解）                                 │
│                                                             │
│    点击：py click_text.py "按钮文字"                       │
│    输入：py type_text.py "内容"                            │
│    滚动：py scroll.py down 3                               │
│    等待：browser action=wait timeMs=2000                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 验证结果                                                 │
│    回到步骤 2，截图验证操作是否成功                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
                         重复直到完成
```

## 每一步详解

### 步骤 1: 打开网页

```bash
# 打开目标网址
browser action=open profile=openclaw target=host url=https://www.baidu.com

# 等待页面加载
browser action=act profile=openclaw targetId=<tab_id> kind=wait timeMs=2000
```

### 步骤 2: 截图

```bash
# 截图
browser action=screenshot profile=openclaw targetId=<tab_id>
```

**重要**：每次操作后都要截图，用来给模型识别页面状态。

### 步骤 3: 模型识别截图

```bash
# 把截图发给模型
image path=C:\Users\OpenClaw\.openclaw\media\browser\xxx.jpg prompt="描述这个页面，找到搜索框和搜索按钮"
```

模型会返回：
- 页面内容描述
- 找到的按钮/输入框位置
- 建议的下一步操作

### 步骤 4: 执行操作

根据模型的理解执行操作：

**点击按钮**：
```bash
py click_text.py "百度一下"
py click_text.py "搜索"
py click_text.py "登录"
```

**输入文字**：
```bash
# 确保是英文输入法
py type_text.py "人工智能"
```

**滚动页面**：
```bash
py scroll.py down 3    # 向下滚动 3 格
py scroll.py up 5      # 向上滚动 5 格
```

### 步骤 5: 验证

操作完成后，截图验证结果，然后继续下一步。

## 特殊情况处理

### 登录弹窗

1. 截图
2. 发给模型
3. 模型识别到登录弹窗
4. **停止操作，提醒用户**

```bash
# 模型返回："页面显示登录弹窗，需要输入账号密码"
# → 提醒用户："该网站需要登录，是否有账户？"
```

### 验证码

1. 截图
2. 发给模型
3. 模型识别到验证码
4. **停止操作，提醒用户**

### 页面加载失败

1. 截图
2. 发给模型
3. 模型识别到错误
4. 尝试刷新页面或换其他方式

---

## 禁止事项

| 禁止 | 原因 |
|------|------|
| 用 snapshot | 直接读取结构会被风控检测 |
| 用 ref 定位 | 不够拟人化 |
| 安装浏览器插件 | 不够纯净 |
| 不用截图直接操作 | 模型需要看图理解 |

---

## 完整示例：百度搜索

```bash
# 1. 打开百度
browser action=open profile=openclaw target=host url=https://www.baidu.com
browser action=act profile=openclaw targetId=TAB_ID kind=wait timeMs=2000

# 2. 截图
browser action=screenshot profile=openclaw targetId=TAB_ID

# 3. 模型识别
image path=/path/to/screenshot.jpg prompt="描述页面，找到搜索框和搜索按钮"

# 模型返回：看到搜索框和"百度一下"按钮

# 4. 点击搜索框
py click_text.py "请输入"

# 5. 输入关键词
py type_text.py "人工智能"

# 6. 点击搜索按钮
py click_text.py "百度一下"

# 7. 等待结果
browser action=act profile=openclaw targetId=TAB_ID kind=wait timeMs=2000

# 8. 截图验证
browser action=screenshot profile=openclaw targetId=TAB_ID
image path=/path/to/screenshot.jpg prompt="描述搜索结果，找到第一个链接"

# 模型返回：第一个结果是"人工智能 - 百度百科"

# 9. 点击第一个结果
py click_text.py "人工智能 - 百度百科"

# 10. 验证到达目标页面
browser action=screenshot profile=openclaw targetId=TAB_ID
image path=/path/to/screenshot.jpg prompt="验证是否到达百度百科页面"
```
