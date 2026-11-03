#!/usr/bin/env python3
"""把 04-播客稿.md 转成适合 TTS 的纯口播文本（去掉标题/元信息/制作备注/强调标记）。"""
import re
import sys
from pathlib import Path

ROOT = Path("/Users/qingzou/WorkBuddy/2026-10-21-18-40-10/output/course-kit")
OUT = ROOT / "podcast-audio" / "scripts"


def clean(md: str) -> str:
    md = md.lstrip("\ufeff")
    # 去掉「附：制作备注」及其后内容
    md = re.split(r"\n##\s*附[：:]", md)[0]
    lines = []
    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        if line.startswith("#"):          # 标题行整行丢弃
            continue
        if line.startswith(">"):          # 栏目/录制提示等元信息
            continue
        if set(line) <= {"-", "*", " "}:   # 分隔线
            continue
        if line.startswith("|"):           # 表格残留
            continue
        # 去掉【放慢】这类提示语，保留其后正文
        line = re.sub(r"【[^】]*】", "", line)
        line = line.replace("**", "").replace("__", "")
        line = re.sub(r"^\s*[-*+]\s+", "", line)
        line = line.strip()
        if line:
            lines.append(line)
    # 段落合并：空行保留为段间停顿
    text = "\n\n".join(p for p in "\n".join(lines).split("\n\n") if p.strip())
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(ROOT.glob("W*-物料/*/04-播客稿.md"))
    for f in files:
        day = f.parent.name
        text = clean(f.read_text(encoding="utf-8"))
        dst = OUT / f"{day}.txt"
        dst.write_text(text, encoding="utf-8")
        print(f"{day}\t{len(text)} chars\t{dst}")


if __name__ == "__main__":
    main()
