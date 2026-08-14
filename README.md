# claude-marketplace

个人 Claude Code skill 市场，存放自己沉淀下来的 skills。

## 安装

```bash
# 添加市场
/plugin marketplace add JackYuan12138/claude-marketplace

# 安装某个 skill（每个 skill 对应一个 plugin）
/plugin install wechat-ocr@claude-marketplace
```

## 已收录 skills

| skill | 说明 |
|-------|------|
| `wechat-ocr` | 使用微信本地 OCR 模型识别图片文字，输出完整文本 + 逐行坐标与置信度 |

## 约定

- 每个 skill 一个 plugin，声明于 `.claude-plugin/marketplace.json`。
- skill 本体放在 `skills/<name>/`，内含 `SKILL.md`（frontmatter + 用法说明）与可选 `scripts/`。
- 依赖外部引擎的 skill 采用「运行时克隆/更新」：引导脚本首次 `git clone --depth 1`，之后 `git pull --ff-only` 更新，离线降级使用本地副本。
