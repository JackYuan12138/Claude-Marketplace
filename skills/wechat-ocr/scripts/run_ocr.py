#!/usr/bin/env python3
"""wechat-ocr skill 引导脚本：确保 OCR 仓库可用（克隆 / 更新），然后运行 OCR 并输出 JSON。

用法::

    python run_ocr.py <图片路径> [更多图片路径...]

逻辑：
1. 首次把仓库 clone 到 <SKILL_ROOT>/vendor/wechat_ocr，之后每次 git pull --ff-only 更新
   （离线 / 更新失败时降级使用现有副本）。
2. 用当前解释器在仓库根目录运行 `python -m wechat_ocr <图片...>`，stdout 透传纯 JSON。
"""
import sys
import subprocess
from pathlib import Path

GIT_URL = "https://github.com/JackYuan12138/wechat_ocr.git"
VENDOR_DIR_NAME = "vendor"
REPO_DIR_NAME = "wechat_ocr"

SKILL_DIR = Path(__file__).resolve().parent.parent


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _is_repo(path: Path) -> bool:
    """判断 path 是否是 wechat_ocr 仓库根（含 bin/WeChatOCR/WeChatOCR.exe 与 wechat_ocr/ 包）。"""
    return (
        (path / "bin" / "WeChatOCR" / "WeChatOCR.exe").exists()
        and (path / "wechat_ocr" / "ocr_manager.py").exists()
    )


def _find_local_repo() -> Path | None:
    """在 skill 目录的若干上级目录里寻找现成的 wechat_ocr 仓库。"""
    for parent in (SKILL_DIR.parent, SKILL_DIR.parent.parent, SKILL_DIR.parent.parent.parent):
        if _is_repo(parent):
            return parent
    return None


def resolve_repo() -> Path:
    local = _find_local_repo()
    if local is not None:
        _log(f"[wechat-ocr] 复用本地仓库: {local}")
        return local

    vendor_root = SKILL_DIR / VENDOR_DIR_NAME
    repo_dir = vendor_root / REPO_DIR_NAME

    if (repo_dir / ".git").exists():
        _log(f"[wechat-ocr] 更新已有副本: {repo_dir}")
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "pull", "--ff-only"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            _log("[wechat-ocr] 更新失败（可能离线），降级使用现有副本")
    else:
        _log(f"[wechat-ocr] 首次克隆仓库到: {repo_dir}")
        vendor_root.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", GIT_URL, str(repo_dir)],
            check=True,
        )
    return repo_dir


def main(argv) -> int:
    argv = list(argv)
    if not argv:
        print("用法: python run_ocr.py <图片路径> [更多图片路径...]", file=sys.stderr)
        return 2

    repo = resolve_repo()
    # 在仓库根目录运行，确保 wechat_ocr 包可导入、bin/ 能被引擎定位
    cmd = [sys.executable, "-m", "wechat_ocr", *argv]
    return subprocess.run(cmd, cwd=str(repo)).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
