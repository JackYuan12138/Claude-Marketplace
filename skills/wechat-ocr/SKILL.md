---
name: wechat-ocr
description: 使用微信本地 OCR 模型识别图片中的文字。当用户需要从图片 / 截图 / 扫描件中提取文字（OCR），或提到"识别图片文字""OCR""把图片转成文字""提取图片中的文本""图里写了什么"时使用。输出结构化结果：完整文本 + 逐行文字与坐标、置信度。可跨项目使用，首次自动克隆 OCR 仓库、之后每次运行前 git pull 更新。
---

# WeChat OCR

调用微信本地 OCR 模型（`WeChatOCR.exe` + `mmmojo.dll`），把图片中的文字识别出来。纯本地运行，无需安装微信；仅首次准备环境和更新时才需要联网。

本 skill 自带引导脚本，会**自动**准备运行环境：首次使用自动把仓库 `git clone --depth 1` 到 `<SKILL_ROOT>/vendor/wechat_ocr`，之后每次运行前 `git pull --ff-only` 更新（离线或更新失败时降级使用现有副本）。

## 何时使用

- 用户给了一张/多张图片，想知道里面的文字内容
- 需要从截图、扫描件、海报、表格图片中提取文本
- 需要文字对应的位置坐标（用于后续定位/标注）

## 前置条件

- Windows 系统，Python >= 3.12（解释器遵循项目 CLAUDE.md 约定，默认 `D:\Apps\ProgramData\Claude_Code\py_venv\Scripts\python.exe`）
- Python 环境需安装 `protobuf`（`pip install protobuf`）；首次需联网以克隆仓库
- `git` 命令可用；之后离线也能用（只要 vendor 副本已存在）

## 调用方式

### 首选：引导脚本（自动准备环境 + 输出纯 JSON）

```bash
python "<SKILL_ROOT>/scripts/run_ocr.py" <图片路径> [更多图片路径...]
```

例：

```bash
python "<SKILL_ROOT>/scripts/run_ocr.py" "C:/Users/x/a.png" "C:/Users/x/b.png"
```

stdout 只输出 JSON（准备过程的日志在 stderr）：

```json
{
  "<输入路径>": {
    "taskId": 1,
    "text": "完整识别文本，多行用 \n 拼接",
    "items": [
      { "text": "单行文本", "left": 21.5, "top": 18.7, "right": 418.5, "bottom": 52.6,
        "confidence": 0.988, "pos": { "x": 21.6, "y": 18.7 } }
    ]
  }
}
```

### 备选 1：已安装包时直接调用

```bash
python -m wechat_ocr <图片路径> [更多...]
```

### 备选 2：Python 接口（程序化 / 批量）

```python
from wechat_ocr import ocr, WeChatOcr

result = ocr("path/to/image.png")
print(result.text)                      # 完整文本
for i in result.items:                  # 逐行
    print(i.text, i.left, i.top, i.confidence)

with WeChatOcr() as client:             # 批量复用同一服务
    for r in client.recognize_many(["a.png", "b.png"]):
        print(r.text)
```

结果对象支持 `.to_dict()` 转成 JSON 友好字典。

## 输出字段

| 字段 | 含义 |
|------|------|
| `text`（顶层） | 完整识别文本，逐行用 `\n` 拼接 |
| `items[].text` | 单行识别文本 |
| `items[].left/top/right/bottom` | 该行外接矩形坐标（浮点，像素） |
| `items[].confidence` | 置信度 0~1，越接近 1 越可信 |
| `items[].pos` | 该行锚点坐标 |

## 注意事项

- 识别按行返回；跨行文本用顶层 `text`（已按行拼接）。
- 每次运行会启动并关闭一次 OCR 服务，单张约几秒；多张图一次命令传多个路径，或改用 `WeChatOcr()` 上下文复用服务。
- 非图片文件、不存在的路径会报错，先确认路径正确。
- 仅个人学习使用，勿用于商业用途。
