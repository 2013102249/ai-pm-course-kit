#!/usr/bin/env python3
"""批量生成 10 条播客音频（6 条 8 分钟正片 + 4 条 60 秒口播）。"""
import sys
import json
from pathlib import Path

sys.path.insert(0, "/Users/qingzou/.workbuddy/skills/wenhao__skillhub/scripts")
from mimo_tts import synthesize, audio_duration  # noqa: E402

BASE = Path("/Users/qingzou/WorkBuddy/2026-10-21-18-40-10/output/course-kit/podcast-audio")
SCRIPTS = BASE / "scripts"
OUT = BASE

VOICE = "白桦"

STYLE_FULL = (
    "用沉稳、温和、有夜间播客讲述感的男声朗读以下内容。"
    "中文普通话，吐字清晰，语速从容（每分钟约 220 字），段落之间留出自然停顿，"
    "重点词语略微加重，最后一句放慢收尾。"
    "英文缩写（如 AI、RAG、JD、Demo、PRD、API）按字母清晰读出，"
    "《》中的栏目名称用自然的书名语气带出，不要读出书名号本身。"
)

STYLE_SHORT = (
    "用沉稳、清晰、干练的男声朗读以下学员群通知。"
    "中文普通话，吐字清晰，语速平稳稍快（每分钟约 260 字），"
    "要点之间停顿半秒，数字读准确，最后一句略微放慢。"
)

JOBS = []
for name in ["W1D1-开营与岗位全景", "W1D2-大模型原理通识", "W1D3-提示词与上下文工程",
             "W1D4-AI产品形态拆解", "W1D5-行业选择与职业规划", "W6D1-Vibe Coding与AI工程提效"]:
    JOBS.append((SCRIPTS / f"{name}.txt", OUT / f"{name}.mp3", STYLE_FULL))
for name in ["W6D2-开发冲刺I", "W6D3-开发冲刺II", "W6D4-测试验收与用户试用", "W6D5-结业路演"]:
    JOBS.append((SCRIPTS / f"{name}-60s.txt", OUT / f"{name}-60秒口播.mp3", STYLE_SHORT))

results = []
for txt_path, out_path, style in JOBS:
    text = txt_path.read_text(encoding="utf-8").strip()
    label = out_path.stem
    try:
        synthesize(text, str(out_path), voice=VOICE, style=style, timeout=900, retries=3)
        dur = audio_duration(str(out_path))
        expect = len(text) / 3.8  # 预估最短可接受时长（秒）
        ok = dur < 0 or dur >= expect * 0.6
        r = {"job": label, "ok": True, "duration_sec": round(dur, 1) if dur > 0 else None,
             "chars": len(text), "duration_check": "pass" if ok else "SUSPECT"}
    except Exception as e:
        r = {"job": label, "ok": False, "error": str(e)[:300]}
    results.append(r)
    print(json.dumps(r, ensure_ascii=False), flush=True)

print("=== SUMMARY ===")
print(json.dumps({"total": len(results),
                  "success": sum(1 for r in results if r["ok"]),
                  "failed": [r["job"] for r in results if not r["ok"]],
                  "suspect": [r["job"] for r in results if r.get("duration_check") == "SUSPECT"]},
                 ensure_ascii=False), flush=True)
