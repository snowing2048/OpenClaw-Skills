# OpenClaw Skills Collection

OpenClaw 技能集合仓库 - 存放各种 OpenClaw Agent Skills

---

## 📁 仓库结构

```
OpenClaw-Skills/
├── README.md                 # 本文件
├── CONTRIBUTING.md           # 贡献指南（可选）
└── skills/                   # 所有 skills 存放在此目录
    ├── browser-agent/        # 示例：浏览器代理技能
    │   ├── SKILL.md          # 技能说明（必需）
    │   ├── scripts/          # Python 脚本（可选）
    │   ├── references/       # 参考文档（可选）
    │   └── test_suite/       # 测试用例（可选）
    ├── browser-workflow-progress/
    │   └── SKILL.md
    ├── risk-approval-gate/
    │   └── SKILL.md
    └── windows-control/
        └── SKILL.md
```

---

## 📋 Skill 标准结构

每个 skill 应该是一个独立的子目录，包含：

### 必需文件

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 技能的核心说明文档，包含技能描述、使用方法、工具调用方式等 |

### 可选文件

| 文件/目录 | 说明 |
|-----------|------|
| `scripts/` | Python 脚本工具集 |
| `references/` | 参考文档、工作流程说明 |
| `test_suite/` | 测试用例 |
| `TEST_STANDARD.md` | 测试标准文档 |

---

## 🚀 如何添加新 Skill

### 步骤 1：创建 Skill 目录

```bash
cd OpenClaw-Skills
mkdir -p skills/your-skill-name
```

### 步骤 2：创建 SKILL.md

```bash
cd skills/your-skill-name
# 创建 SKILL.md，参考现有 skill 的格式
```

### 步骤 3：添加其他文件（可选）

```bash
mkdir scripts references test_suite
# 添加你的脚本、文档、测试等
```

### 步骤 4：提交并推送

```bash
git add .
git commit -m "feat: add your-skill-name skill"
git push origin main
```

---

## 📝 SKILL.md 模板

```markdown
# Skill Name

## Description
简要描述技能的功能和用途。

## When to Use
- 场景 1
- 场景 2

## Tools Used
- `tool_name`: 用途说明

## Usage Example
```bash
# 示例命令或代码
```

## Notes
注意事项、限制条件等。
```

---

## 🔧 现有 Skills

| Skill | 说明 | 状态 |
|-------|------|------|
| [browser-agent](skills/browser-agent/) | 拟人化浏览器代理 | ✅ 完成 |
| [browser-workflow-progress](skills/browser-workflow-progress/) | 浏览器工作流编排 | 📝 待完善 |
| [risk-approval-gate](skills/risk-approval-gate/) | 高危操作人类确认门 | 📝 待完善 |
| [windows-control](skills/windows-control/) | Windows 桌面控制 | 📝 待完善 |

---

## 📌 注意事项

1. **每个 skill 独立**：skill 之间不应互相依赖
2. **命名规范**：使用 `kebab-case` 命名（如 `browser-agent`）
3. **文档完整**：至少包含 `SKILL.md`
4. **测试覆盖**：建议提供测试用例或测试标准

---

## 🤝 贡献指南

欢迎提交新的 skills！请确保：

- [ ] Skill 目录结构正确
- [ ] `SKILL.md` 内容完整
- [ ] 无敏感信息（API Keys、密码等）
- [ ] 代码有基本注释

---

## 📄 License

MIT License
