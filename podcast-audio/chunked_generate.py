#!/usr/bin/env python3
"""分段合成长播客稿（修复版）：
按段落切块(≤600字) → 逐块合成 WAV → wave 模块合并 PCM → lameenc 编码 MP3 → afinfo 校验时长。
"""
import sys
import json
import time
import wave
import subprocess
from pathlib import Path

sys.path.insert(0, "/Users/qingzou/.workbuddy/skills/wenhao__skillhub/scripts")
from mimo_tts import synthesize, audio_duration  # noqa: E402

import lameenc  # noqa: E402

BASE = Path("/Users/qingzou/WorkBuddy/2026-10-21-18-40-10/output/course-kit/podcast-audio")
SCRIPTS = BASE / "scripts"
TMP = BASE / "_parts"
VOICE = "白桦"

STYLE_FULL = (
    "用沉稳、温和、有夜间播客讲述感的男声朗读以下内容。"
    "中文普通话，吐字清晰，语速从容（每分钟约 220 字），段落之间留出自然停顿，"
    "重点词语略微加重，最后一句放慢收尾。"
    "英文缩写（如 AI、RAG、JD、Demo、PRD、API）按字母清晰读出，"
    "《》中的栏目名称用自然的书名语气带出，不要读出书名号本身。"
)

MAX_CHARS = 600
RATE_MAX = 7.0     # 每秒最多 7 字，低于此速率视为截断
BITRATE = 112      # mp3 码率 kbps（24kHz 单声道人声）


def split_chunks(text: str) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(p) > MAX_CHARS:  # 单段超长时按句切分
            if cur:
                chunks.append(cur)
                cur = ""
            buf = ""
            for s in p.replace("。", "。|").replace("；", "；|").split("|"):
                if len(buf) + len(s) > MAX_CHARS and buf:
                    chunks.append(buf)
                    buf = s
                else:
                    buf += s
            if buf:
                chunks.append(buf)
        elif len(cur) + len(p) + 2 > MAX_CHARS:
            chunks.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks


def synth_chunk_wav(text: str, out: Path) -> tuple[float, int, int]:
    """合成单块 WAV，返回 (时长秒, 采样率, 声道数)；截断自动重试。"""
    expect = len(text) / RATE_MAX
    for attempt in range(1, 4):
        try:
            synthesize(text, str(out), voice=VOICE, style=STYLE_FULL,
                       timeout=900, retries=2, audio_format="wav")
        except Exception as e:
            print(f"    attempt {attempt} error: {str(e)[:160]}", flush=True)
            time.sleep(4)
            continue
        with wave.open(str(out), "rb") as w:
            rate, ch, frames = w.getframerate(), w.getnchannels(), w.getnframes()
        dur = frames / rate
        if dur >= expect:
            return dur, rate, ch
        print(f"    attempt {attempt} too short: {dur:.1f}s < {expect:.0f}s ({len(text)} chars)", flush=True)
        time.sleep(4)
    raise RuntimeError(f"块 {out.name} 多次合成后仍异常")


def pcm_to_mp3(pcm: bytes, rate: int, ch: int, out: Path) -> None:
    enc = lameenc.Encoder()
    enc.set_bit_rate(BITRATE)
    enc.set_in_sample_rate(rate)
    enc.set_channels(ch)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    out.write_bytes(bytes(data))


def build(name: str) -> dict:
    text = (SCRIPTS / f"{name}.txt").read_text(encoding="utf-8").strip()
    chunks = split_chunks(text)
    if not TMP.exists():
        TMP.mkdir(parents=True)
    print(f"[{name}] {len(text)} chars -> {len(chunks)} chunks", flush=True)

    pcm, rate, ch = b"", None, None
    for i, chunk in enumerate(chunks, 1):
        wav_part = TMP / f"{name}.part{i:02d}.wav"
        d, r, c = synth_chunk_wav(chunk, wav_part)
        with wave.open(str(wav_part), "rb") as w:
            pcm += w.readframes(w.getnframes())
        rate, ch = r, c
        print(f"    part {i:02d}/{len(chunks)}: {len(chunk)} chars, {d:.1f}s", flush=True)

    final = BASE / f"{name}.mp3"
    pcm_to_mp3(pcm, rate, ch, final)

    total = audio_duration(str(final))
    expect = len(text) / RATE_MAX
    status = "pass" if total >= expect else "FAIL"
    print(f"[{name}] final {total:.1f}s (expect >={expect:.0f}s) -> {status}", flush=True)
    return {"duration_sec": round(total, 1), "check": status, "chunks": len(chunks)}


if __name__ == "__main__":
    names = sys.argv[1:] or ["W1D1-开营与岗位全景", "W1D2-大模型原理通识",
                             "W1D4-AI产品形态拆解", "W1D5-行业选择与职业规划"]
    summary = {}
    for n in names:
        summary[n] = build(n)
    print("=== SUMMARY ===", flush=True)
    print(json.dumps(summary, ensure_ascii=False), flush=True)
