#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 8 节产品思维小课：8 MD + 8 SVG（1200x800，紫 #7C3AED / 蓝 #2563EB）+ 00-总览。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUT = "/Users/mac/WorkBuddy/2026-10-21-18-40-10/output/course-kit/00-产品思维小课/"
os.makedirs(OUT, exist_ok=True)

PURPLE, BLUE, INK, BODY, MUTE = "#7C3AED", "#2563EB", "#111827", "#374151", "#6B7280"
LINE, SOFT = "#E5E7EB", "#F1EDFB"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg_open(title):
    return ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">',
        '<defs><linearGradient id="hd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>' % (PURPLE, BLUE),
        '<rect width="1200" height="800" fill="#F8F8FC"/>',
        '<rect width="1200" height="96" fill="url(#hd)"/>',
        '<text x="50" y="60" font-size="30" font-weight="700" fill="#FFFFFF">%s</text>' % esc(title),
        '<text x="1150" y="60" font-size="15" fill="#FFFFFF" text-anchor="end" opacity="0.85">AI 产品经理就业训练营 · 产品思维小课</text>']

def svg_close(note):
    return ['<line x1="0" y1="752" x2="1200" y2="752" stroke="%s"/>' % LINE,
        '<text x="50" y="778" font-size="14" fill="%s">%s</text>' % (MUTE, esc(note)),
        '<text x="1150" y="778" font-size="14" fill="%s" text-anchor="end">紫 %s / 蓝 %s · 1200×800</text>' % (MUTE, PURPLE, BLUE), '</svg>']

def box(x, y, w, h, fill, stroke, rx=12):
    return '<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, y, w, h, rx, fill, stroke)

def text(x, y, s, size=18, color=BODY, weight="normal", anchor="start"):
    return '<text x="%d" y="%d" font-size="%d" fill="%s" font-weight="%s" text-anchor="%s">%s</text>' % (x, y, size, color, weight, anchor, esc(s))

def harrow(x1, y, x2, color=BLUE):
    return '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5"/><polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (
        x1, y, x2 - 10, y, color, x2, y, x2 - 14, y - 6, x2 - 14, y + 6, color)

# ---------- 8 张框架图 ----------
def svg01():
    s = svg_open("需求真伪 · 四问滤网：四问全过才立项，一问答不上就先别做")
    s.append(box(60, 350, 150, 100, PURPLE, PURPLE, 14))
    s.append(text(135, 392, "一个需求", 20, "#FFFFFF", "700", "middle"))
    s.append(text(135, 420, "进站", 20, "#FFFFFF", "700", "middle"))
    s.append(harrow(215, 400, 265))
    qs = [("问 1 · 谁在痛？", "有具体的人吗？叫得出名字吗"),
          ("问 2 · 痛多久？", "高频还是偶发？一次还是每天"),
          ("问 3 · 怎么活？", "没有它，用户现在用什么替代"),
          ("问 4 · 不做会怎样？", "最坏结果写得出具体场景吗")]
    y = 130
    for i, (t, d) in enumerate(qs):
        c = PURPLE if i % 2 == 0 else BLUE
        s.append(box(270, y, 430, 118, "#FFFFFF", c))
        s.append('<rect x="270" y="%d" width="6" height="118" rx="3" fill="%s"/>' % (y, c))
        s.append(text(296, y + 42, t, 21, INK, "700"))
        s.append(text(296, y + 78, d, 16.5, BODY))
        y += 138
    s.append(harrow(705, 400, 760))
    s.append(box(765, 150, 385, 150, SOFT, PURPLE, 14))
    s.append(text(957, 205, "四问全过 → 真需求", 22, PURPLE, "700", "middle"))
    s.append(text(957, 245, "进排期，写进需求清单", 16, BODY, anchor="middle"))
    s.append(box(765, 470, 385, 150, "#F3F4F6", "#9CA3AF", 14))
    s.append(text(957, 525, "任一问答不上 → 先别做", 22, MUTE, "700", "middle"))
    s.append(text(957, 565, "归档并写明卡在哪一问", 16, BODY, anchor="middle"))
    s.append(text(60, 690, "口诀：先找人，再问频率，再看替代品，最后算不做的代价——四问滤过，才轮得到排期。", 17, INK, "700"))
    return s + svg_close("产品思维小课 01 · 需求真伪 ｜ 课堂用法：讲师念反例 → 投屏本图讲 1 分钟 → 学员两两互问三个追问")

def svg02():
    s = svg_open("用户访谈 · 三层下钻：问过去的行为，不问未来的意愿")
    layers = [("表层 · 他说要什么", "「我想要个深色模式」——最容易想到的答案，价值最低", "#9CA3AF", 80),
              ("动机层 · 他为什么", "连追两层为什么：怕费眼？深夜用？显专业？——从这里开始值钱", BLUE, 240),
              ("场景层 · 上次何时何地", "上次发生是什么时候、在哪、和谁、之前试过什么——行为最诚实", PURPLE, 400)]
    for t, d, c, y in layers:
        s.append(box(90, y, 700, 130, "#FFFFFF", c))
        s.append('<rect x="90" y="%d" width="6" height="130" rx="3" fill="%s"/>' % (y, c))
        s.append(text(120, y + 45, t, 21, INK, "700"))
        s.append(text(120, y + 85, d, 16.5, BODY))
    for i, y in enumerate([145, 305]):
        s.append(harrow(440, y, 440, PURPLE))
        s.append('<polygon points="434,%d 446,%d 440,%d" fill="%s"/>' % (y + 26, y + 26, y + 12, PURPLE))
    s.append(text(620, 175, "下钻", 17, PURPLE, "700"))
    s.append(text(620, 335, "下钻", 17, PURPLE, "700"))
    s.append(box(840, 240, 310, 250, SOFT, PURPLE, 14))
    s.append(text(995, 295, "黄金规则", 21, PURPLE, "700", "middle"))
    s.append(text(995, 340, "问过去的行为：", 18, INK, "700", "middle"))
    s.append(text(995, 372, "「上次是什么时候？」", 17, BODY, anchor="middle"))
    s.append(text(995, 412, "不问未来的意愿：", 18, INK, "700", "middle"))
    s.append(text(995, 444, "「将来你会用吗？」", 17, BODY, anchor="middle"))
    s.append(text(60, 690, "口诀：他说要的是答案，他做过的是证据——访谈挖到场景层才算挖到矿。", 17, INK, "700"))
    return s + svg_close("产品思维小课 02 · 用户访谈 ｜ 课堂用法：反例 → 本图 1 分钟 → 两两微型访谈 3 分钟（对同桌挖两层为什么）")

def svg03():
    s = svg_open("PRD 结构 · 六块骨架：异常流不少于正常流，『不做什么』必须写")
    blocks = [("01 背景与目标", "为什么做，目标可衡量", PURPLE), ("02 用户与场景", "给谁用、在什么场景下用", BLUE),
              ("03 需求详述", "正常流 + 异常流，异常不少于正常", PURPLE), ("04 数据埋点", "上线后怎么知道好没好", BLUE),
              ("05 边界与不做的事", "防止范围膨胀的第一道闸", BLUE), ("06 非功能要求", "性能、安全、合规底线", PURPLE)]
    pos = [(70, 140), (440, 140), (810, 140), (70, 380), (440, 380), (810, 380)]
    for (t, d, c), (x, y) in zip(blocks, pos):
        s.append(box(x, y, 320, 190, "#FFFFFF", c))
        s.append('<rect x="%d" y="%d" width="320" height="8" rx="4" fill="%s"/>' % (x, y, c))
        s.append(text(x + 26, y + 62, t, 21, INK, "700"))
        s.append(text(x + 26, y + 106, d, 16.5, BODY))
    s.append(text(70, 645, "检查法：只读第 01 块，开发能不能说出要做什么？只读第 03 块异常流，客服能不能接住故障？", 17, INK, "700"))
    s.append(text(70, 678, "常见病：把 03 写成一句『做一个 XX 系统』——那不是 PRD，是许愿。", 16, MUTE))
    return s + svg_close("产品思维小课 03 · PRD 结构 ｜ 课堂用法：反例 → 本图 1 分钟 → 今日架构草图每个工具补一行『失败时怎么办』")

def svg04():
    s = svg_open("指标定义 · 一横一纵：一个北极星，三个过程指标，两条护栏")
    s.append(box(400, 130, 400, 120, PURPLE, PURPLE, 14))
    s.append(text(600, 180, "北极星指标 · 唯一", 22, "#FFFFFF", "700", "middle"))
    s.append(text(600, 216, "回答「用户得到了什么价值」", 15.5, "#FFFFFF", anchor="middle"))
    s.append(harrow(600, 255, 600, BLUE))
    s.append('<polygon points="594,275 606,275 600,289" fill="%s"/>' % BLUE)
    proc = [("过程指标 1", "本周动什么"), ("过程指标 2", "几天能看到变化"), ("过程指标 3", "归因到具体动作")]
    x = 180
    for t, d in proc:
        s.append(box(x, 300, 260, 120, "#FFFFFF", BLUE))
        s.append(text(x + 130, 350, t, 19, INK, "700", "middle"))
        s.append(text(x + 130, 385, d, 15.5, BODY, anchor="middle"))
        x += 290
    s.append(box(180, 470, 840, 110, SOFT, PURPLE, 14))
    s.append(text(600, 515, "护栏指标 × 2 —— 什么涨是不能接受的", 20, PURPLE, "700", "middle"))
    s.append(text(600, 552, "例：次日留存、客诉率。过程指标涨、护栏指标跌 = 动作变形，立刻停。", 16, BODY, anchor="middle"))
    s.append(text(60, 690, "口诀：北极星指方向，过程指标管动作，护栏指标防变形——三个都没有，就是『把活跃度搞上去』。", 17, INK, "700"))
    return s + svg_close("产品思维小课 04 · 指标定义 ｜ 课堂用法：反例 → 本图 1 分钟 → 今日研究提纲写 1 北极星 + 2 护栏，同桌互查")

def svg05():
    s = svg_open("优先级排序 · 价值-成本四象限：只允许一个进『先做』")
    ox, oy, w, h = 330, 140, 640, 480
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (ox, oy, ox, oy + h, INK))
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (ox, oy + h, ox + w, oy + h, INK))
    s.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (ox, oy - 10, ox - 8, oy + 4, ox + 8, oy + 4, INK))
    s.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (ox + w + 10, oy + h, ox + w - 4, oy + h - 8, ox + w - 4, oy + h + 8, INK))
    s.append(text(ox - 14, oy + h / 2, "用户价值高", 16, INK, "700", "end"))
    s.append(text(ox + w / 2, oy + h + 34, "实现成本 →", 16, INK, "700", "middle"))
    q = [(ox, oy, w / 2 - 6, h / 2 - 6, "左上 · 计划做", "高价值高成本：拆小再上", SOFT, PURPLE, PURPLE),
         (ox + w / 2 + 6, oy, w / 2 - 6, h / 2 - 6, "右上 · 先做", "高价值低成本：本周就动", "#EDE9FE", PURPLE, PURPLE),
         (ox, oy + h / 2 + 6, w / 2 - 6, h / 2 - 6, "左下 · 不做", "低价值高成本：写下来防复活", "#F3F4F6", "#9CA3AF", MUTE),
         (ox + w / 2 + 6, oy + h / 2 + 6, w / 2 - 6, h / 2 - 6, "右下 · 顺手做", "低价值低成本：攒着批量", "#EFF6FF", BLUE, BLUE)]
    for x, y, qw, qh, t, d, f, st, tc in q:
        s.append(box(x, y, qw, qh, f, st))
        s.append(text(x + qw / 2, y + qh / 2 - 10, t, 21, tc, "700", "middle"))
        s.append(text(x + qw / 2, y + qh / 2 + 26, d, 15, BODY, anchor="middle"))
    s.append(text(60, 690, "口诀：全标『紧急』等于没有优先级——四象限分完，右上只留一个，左下的写下来，防止它下周复活。", 17, INK, "700"))
    return s + svg_close("产品思维小课 05 · 优先级排序 ｜ 课堂用法：反例 → 本图 1 分钟 → 今日 3 个候选动作只许 1 个进『先做』")

def svg06():
    s = svg_open("复盘方法 · 四步复盘环：结论必须落到『谁 + 何时 + 做什么』")
    steps = [("① 目标回顾", "当初要什么？白纸黑字翻出来", PURPLE), ("② 结果对比", "差多少？只摆数字，不摆情绪", BLUE),
             ("③ 差距归因", "先查流程再查人：信息？能力？意愿？", BLUE), ("④ 行动改进", "谁 + 什么时间前 + 做什么", PURPLE)]
    x = 70
    for i, (t, d, c) in enumerate(steps):
        s.append(box(x, 260, 240, 180, "#FFFFFF", c))
        s.append('<rect x="%d" y="260" width="240" height="8" rx="4" fill="%s"/>' % (x, c))
        s.append(text(x + 120, 320, t, 21, INK, "700", "middle"))
        w = d.split("：")
        s.append(text(x + 120, 362, w[0], 16, BODY, anchor="middle"))
        if len(w) > 1: s.append(text(x + 120, 392, w[1], 16, BODY, anchor="middle"))
        if i < 3: s.append(harrow(x + 246, 350, x + 296))
        x += 290
    s.append('<path d="M 1060 350 C 1120 350 1120 560 1060 560 L 190 560" stroke="%s" stroke-width="2.5" fill="none" stroke-dasharray="8 6"/>' % PURPLE)
    s.append('<polygon points="190,554 176,560 190,566" fill="%s"/>' % PURPLE)
    s.append(text(620, 600, "下一轮目标从第 ④ 步长出来——复盘不是终点，是下个循环的起点", 16, PURPLE, "700", "middle"))
    s.append(text(60, 690, "口诀：先查流程再查人；『下次注意』不是结论——写不出人和时间的复盘，等于没开。", 17, INK, "700"))
    return s + svg_close("产品思维小课 06 · 复盘方法 ｜ 课堂用法：反例 → 本图 1 分钟 → 今日冲刺结束开 5 分钟迷你复盘，产出 1 条改进项")

def svg07():
    s = svg_open("跨团队协作 · RACI 四角色：没有 R 没人做，有两个 A 必打架")
    s.append(box(400, 122, 400, 66, PURPLE, PURPLE, 33))
    s.append(text(600, 164, "铁律：每个任务的 A 只能有一个", 20, "#FFFFFF", "700", "middle"))
    raci = [("R · Responsible", "谁执行", "动手干活的人。没有 R 的任务 = 没人做", PURPLE, 220),
            ("A · Accountable", "谁拍板", "唯一负责拍板的人。两个 A = 必打架", BLUE, 330),
            ("C · Consulted", "谁被咨询", "动手前要问过的人——问过才算数", PURPLE, 440),
            ("I · Informed", "谁被告知", "知会即可，别指望 I 会动——他『收到』只是礼貌", BLUE, 550)]
    for t, sub, d, c, y in raci:
        s.append(box(110, y, 720, 92, "#FFFFFF", c))
        s.append('<rect x="110" y="%d" width="6" height="92" rx="3" fill="%s"/>' % (y, c))
        s.append(text(140, y + 38, t, 20, INK, "700"))
        s.append(text(460, y + 38, sub, 18, c, "700"))
        s.append(text(140, y + 70, d, 16, BODY))
    s.append(box(880, 220, 270, 422, SOFT, PURPLE, 14))
    s.append(text(1015, 268, "发需求前自检", 20, PURPLE, "700", "middle"))
    s.append(text(905, 312, "① R 有名字吗", 16.5, BODY))
    s.append(text(905, 348, "② A 是不是只有 1 个", 16.5, BODY))
    s.append(text(905, 384, "③ C 知道自己被咨询吗", 16.5, BODY))
    s.append(text(905, 420, "④ 群里 @ 的人各是哪个字母", 16.5, BODY))
    s.append(text(905, 478, "「人人回复收到」", 17, MUTE, "700"))
    s.append(text(905, 508, "≠「有人负责」", 17, MUTE, "700"))
    s.append(text(905, 560, "卡住 24 小时就升级", 16, INK, "700"))
    s.append(text(60, 690, "口诀：@ 全员 = 没@任何人——发任务先标字母，R 动手、A 拍板、C 被问、I 只看。", 17, INK, "700"))
    return s + svg_close("产品思维小课 07 · 跨团队协作 ｜ 课堂用法：反例 → 本图 1 分钟 → 今日给整合日任务清单标 RACI，A 只能是自己")

def svg08():
    s = svg_open("表达与汇报 · 结论先行三段式：第一句话就是你的判断或请求")
    segs = [("第一段 · 结论", "一句话说清你的判断或请求——先给答案，不给铺垫", PURPLE, 140),
            ("第二段 · 依据", "2–3 条支撑，必须含数字：基准值 → 结果值 + 来源", BLUE, 310),
            ("第三段 · 行动", "下一步要什么、要谁拍板、什么时候要——没有行动段的汇报是散文", PURPLE, 480)]
    for t, d, c, y in segs:
        s.append(box(90, y, 1020, 140, "#FFFFFF", c))
        s.append('<rect x="90" y="%d" width="10" height="140" rx="5" fill="%s"/>' % (y, c))
        s.append(text(130, y + 52, t, 22, INK, "700"))
        s.append(text(130, y + 98, d, 17.5, BODY))
        s.append(text(1060, y + 52, "%d/3" % (segs.index((t, d, c, y)) + 1), 20, c, "700", "middle"))
    s.append(box(90, 645, 1020, 56, SOFT, BLUE, 12))
    s.append(text(600, 681, "背景沉到最后：对方追问再讲——「所以你要我做什么」这句话，永远别让它出现在你的汇报里", 17, INK, "700", "middle"))
    return s + svg_close("产品思维小课 08 · 表达与汇报 ｜ 课堂用法：反例 → 本图 1 分钟 → 30 秒自我介绍按三段式，今日对 2 位同学各讲一遍")

SVGS = {"01": svg01, "02": svg02, "03": svg03, "04": svg04, "05": svg05, "06": svg06, "07": svg07, "08": svg08}

# ---------- 8 节 MD ----------
LESSONS = [
 dict(num="01", zh="需求真伪", week="W1D1 开营与岗位全景", fname="01-需求真伪",
  case="某团队老板在会上拍板：「加个签到功能，用户肯定喜欢。」全员两周赶工上线。三个月后悄悄下线——日打开率 3%，评论区最高赞是「别再弹签到提醒了」。",
  frame="四问滤网。一个需求进来，依次过四道问：**①谁在痛**——有具体的人吗，叫得出名字吗；**②痛多久**——高频还是偶发；**③现在怎么活**——没有这个功能，用户用什么替代；**④不做会怎样**——最坏结果写不写得成具体场景。四问全过才立项，任意一问答不上，就先归档并写明卡在哪一问。",
  asks=["这个需求背后的人叫什么名字？什么岗位？", "他没有这个功能的过去一年，是怎么活下来的？", "如果本月不做，最坏会发生什么？写得出场景吗？"],
  action="下课前，用四问滤网检查你定位卡里的「我要转行 AI 产品」——四个问题各写一句答案。转行也是需求，先对自己验真伪。",
  preview="一个「签到功能」的反例 + 四问滤网，开营第一天先检查自己的转行决策。"),
 dict(num="02", zh="用户访谈", week="W2D1 模型能力边界与选型", fname="02-用户访谈",
  case="访谈者问：「你希望我们的产品加什么功能？」用户热情地答了「深色模式」。两周后上线，使用率 4%——用户说的是他最容易想到的答案，不是他的真实动机。",
  frame="三层下钻。表层是**他说要什么**（价值最低）；往下是**动机层**——连追两层「为什么」，怕费眼？深夜用？显专业？；再往下是**场景层**——上次发生是什么时候、在哪、和谁、之前试过什么。黄金规则：**问过去的行为，不问未来的意愿**——行为最诚实，意愿最廉价。",
  asks=["用户说「我想要」的时候，你追了几层为什么？", "只许问一个问题，你问「将来会不会用」，还是「上次什么时候用过类似的」？", "他给的答案是方案还是动机？你用什么分辨？"],
  action="课间对同桌做 3 分钟微型访谈：只问过去行为（「上次你……是什么时候」），往下挖两层「为什么」，把挖到的动机写成一句话——W2D5 立项预研直接用。",
  preview="「深色模式」的反例 + 三层下钻，为周五立项准备第一批真实动机。"),
 dict(num="03", zh="PRD 结构", week="W3D1 Agent 架构原理", fname="03-PRD结构",
  case="一份 PRD 的需求详述只有六个字：「做一个会员系统。」开发按各自理解开工，返工三次。上线当天客服炸锅——没有任何一节定义过「会员到期后权益怎么算」。",
  frame="六块骨架。**①背景与目标**（为什么做、目标可衡量）；**②用户与场景**（给谁用、什么场景）；**③需求详述**（正常流 + 异常流，异常流不少于正常流）；**④数据埋点**（上线后怎么知道好没好）；**⑤边界与不做的事**（防范围膨胀的第一道闸）；**⑥非功能要求**（性能、安全、合规）。自检法：只读第①块，开发能不能说出要做什么；只读第③块异常流，客服能不能接住故障。",
  asks=["你的 PRD 里，异常流比正常流多还是少？", "哪一节明确写了「不做什么」？", "开发只读第一块，能不能说出要干什么？"],
  action="今天画 Agent 架构草图时，给工具清单里每个工具补一行「失败时怎么办」——把异常流思维先用在你自己的图上。",
  preview="「六个字 PRD」的反例 + 六块骨架，今天画架构图时先用异常流思维。"),
 dict(num="04", zh="指标定义", week="W4D1 用户研究与需求分析", fname="04-指标定义",
  case="负责人喊：「这季度把活跃度搞上去。」团队狂发弹窗和签到奖励，DAU 涨了 5%。次日留存掉了 8%——被拉来的人第二天就走了，「活跃」变成了「打扰」。",
  frame="一横一纵。顶部一个**北极星指标**：唯一，回答「用户得到了什么价值」；下面 3 个**过程指标**：本周动什么、几天能看到变化、能归因到哪个具体动作；旁边 2 个**护栏指标**：什么涨是不能接受的（比如次日留存、客诉率）。过程指标涨、护栏指标跌 = 动作变形，立刻停。",
  asks=["你的项目如果只能盯一个数，是哪个？为什么是它？", "这个指标涨了，什么东西会受害？", "今天要做的动作，预计让哪个过程指标在几天内动？"],
  action="今天的用户研究提纲里，给主项目写下 1 个北极星 + 2 个护栏指标，写完和同桌交换——让对方找出「哪个指标其实没法衡量」。",
  preview="「活跃度」的反例 + 一横一纵，今天研究提纲里先立北极星和护栏。"),
 dict(num="05", zh="优先级排序", week="W5D1 AI 产品增长", fname="05-优先级排序",
  case="五个需求全部标着「紧急」。团队五个并行，两周后每个都完成了一半。评审会上被问「哪个上线了」，会议室安静了十秒。",
  frame="价值-成本四象限。横轴实现成本，纵轴用户价值：**右上先做**（高价值低成本，本周就动）；**左上计划做**（高价值高成本，拆小再上）；**右下顺手做**（低价值低成本，攒着批量处理）；**左下不做**（低价值高成本，写下来防止它下周复活）。纪律：分完之后，右上只留一个。",
  asks=["你说「紧急」的依据是什么？谁定义的紧急？", "本周只能上线一个，砍谁？为什么是它？", "做一半的三个和做完的一个，你的用户更想要哪个？"],
  action="今天的增长方案有 3 个候选动作——把它们放进四象限，只允许 1 个进「先做」，另外两个明确写「排队」和「不做」。",
  preview="「五个全做」的反例 + 价值-成本四象限，今天只许一个动作进先做区。"),
 dict(num="06", zh="复盘方法", week="W6D1 Vibe Coding 与 AI 工程提效", fname="06-复盘方法",
  case="项目翻车，复盘会开成了追责会。人人自危，结论只有一句「下次注意」。三个月后，同样的坑原样再踩一遍。",
  frame="四步复盘环。**①目标回顾**——当初要什么，白纸黑字翻出来；**②结果对比**——差多少，只摆数字不摆情绪；**③差距归因**——先查流程再查人：信息不通？能力不够？还是意愿问题；**④行动改进**——谁、在什么时间前、做什么，三要素缺一不算结论。下一轮目标从第④步长出来：复盘不是终点，是下个循环的起点。",
  asks=["上次的复盘结论，是「下次注意」还是「具体动作」？", "归因的时候，你先查流程还是先问是谁？", "复盘产出的每条行动，「谁 + 何时 + 做什么」三要素齐了吗？"],
  action="今天开发冲刺结束前，用四步环开一次 5 分钟迷你复盘——只产出 1 条改进项，但必须写全「谁 + 什么时间前 + 做什么」，明天早会第一个过它。",
  preview="「追责会」的反例 + 四步复盘环，今天冲刺收工时开 5 分钟迷你复盘。"),
 dict(num="07", zh="跨团队协作", week="W7D1 行业纵深", fname="07-跨团队协作",
  case="需求群里 @ 了 6 个人，人人回复「收到」。上线当天发现没人动——每个人都以为这只是在「知会」，该有人去做，但那个人不是自己。",
  frame="RACI 四角色。**R（Responsible）谁执行**——动手的人，没有 R 的任务没人做；**A（Accountable）谁拍板**——唯一负责拍板的人，两个 A 必打架；**C（Consulted）谁被咨询**——动手前问过才算数；**I（Informed）谁被告知**——知会即可，别指望 I 会动，他回「收到」只是礼貌。发需求前先标字母：卡住超过 24 小时，走升级路径。",
  asks=["你上一条群通知里，谁是 R？谁是 I？分清了吗？", "一个任务能不能有两个 A？为什么不能？", "跨团队卡住超过 24 小时，你的升级路径是什么？"],
  action="给明天作品集整合日的任务清单标 RACI——每一项确认 A 只有一个人，而且那个人就是你自己。",
  preview="「人人都回复收到」的反例 + RACI 四角色，明天整合日的任务清单先标好字母。"),
 dict(num="08", zh="表达与汇报", week="W8D1 面试全景地图", fname="08-表达与汇报",
  case="汇报人从项目背景讲起，五分钟后还在铺垫。老板打断：「所以你要我做什么？」——一句话能说清的事，错过了决策窗口。",
  frame="结论先行三段式。第一段**结论**：一句话说清你的判断或请求，先给答案不给铺垫；第二段**依据**：2–3 条支撑，必须含数字——基准值→结果值 + 来源；第三段**行动**：下一步要什么、要谁拍板、什么时候要——没有行动段的汇报是散文。背景沉到最后，对方追问再讲。",
  asks=["你汇报的第一句是结论还是背景？", "你的汇报里有几个数字？面试官能记住几个？", "说完之后，你要对方做的决定是什么？"],
  action="用三段式把「我是谁 + 我做过什么」压成 30 秒：结论（我能胜任哪个岗位）→ 依据（1 个项目 + 2 个数字）→ 行动（我想得到什么机会）。今天至少对 2 位同学各讲一遍。",
  preview="「五分钟铺垫」的反例 + 结论先行三段式——面试第一天，先装上 30 秒电梯演讲。"),
]

def lesson_md(c):
    asks = "\n".join("%d. %s" % (i + 1, a) for i, a in enumerate(c["asks"]))
    body_len = len(c["case"]) + len(c["frame"]) + sum(len(a) for a in c["asks"]) + len(c["action"])
    return """﻿# 产品思维小课 {num} · {zh}

> 使用时点：{week} 开课前 10 分钟 ｜ 配图：`{fname}.svg`（判断框架，投屏用）｜ 主讲正文 {chars} 字（上限 600）
> 时间分配：反例 2 分钟 → 框架 3 分钟 → 追问互问 4 分钟 → 今天的动作 1 分钟（合计 10 分钟）

## 一、真实反例（讲师念，2 分钟）

{case}

## 二、判断框架（看图讲 3 分钟）

{frame}

（投屏 `{fname}.svg`，学员对号入座 30 秒：图里四个格子 / 三层 / 四步，你现在的位置在哪一格？）

## 三、三个追问（两两互问，4 分钟）

> 规则：两人一组，每人至少问对方 1 题，回答不超过 30 秒；答不上不要解释，记下来——答不上的地方就是这节课该带走的地方。

{asks}

## 四、今天的动作（写进导学案空白处，1 分钟）

{action}

---
*主讲字数 {chars} 字（反例 + 框架 + 追问 + 动作，不含标题与说明行）。目录见 `00-总览.md`。*
""".format(num=c["num"], zh=c["zh"], week=c["week"], fname=c["fname"], chars=body_len,
           case=c["case"], frame=c["frame"], asks=asks, action=c["action"])

for c in LESSONS:
    with open(OUT + c["fname"] + ".md", "w", encoding="utf-8") as f:
        f.write(lesson_md(c))
    with open(OUT + c["fname"] + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(SVGS[c["num"]]()))
    print("OK", c["num"], c["zh"])

# 总览
rows = "\n".join("| %s | %s | %s | %s |" % (c["num"], c["zh"], c["week"], c["preview"]) for c in LESSONS)
with open(OUT + "00-总览.md", "w", encoding="utf-8") as f:
    f.write("""# 产品思维小课 · 总览（8 节）

> AI 产品经理就业训练营 · 每周第一次课前 10 分钟 ｜ 每节固定四件套：真实反例（3 句）→ 判断框架（1 张图）→ 三个追问（两两互问）→ 今天的动作（当日课堂练习用）
> 设计目标：秦田（测试转产品）、唐嘉焱（设计转产品）补「产品基本知识与思维」，王盛宇、潘韶华、罗思蕊（零基础跨行）用同一套小课建立共同语言——**每天 10 分钟，八周攒出一本产品思维工具箱**。

| 节 | 主题 | 使用时点 | 今天就能用在哪 |
|---|---|---|---|
{rows}

## 使用规则

1. 开课前 10 分钟，讲师（或轮值学员）照读反例 → 投屏框架图 → 两两互问 → 布置「今天的动作」。
2. 每节主讲正文 ≤600 字，10 分钟内含一次口头练习（追问互问或动作陈述）。
3. 「今天的动作」全部与当日课程任务挂钩：小课不是加课，是当天任务的第一块垫脚石。
4. 第八周结营时，8 张框架图就是你面试反问环节的「我的方法论」素材——面试官问「你怎么判断需求真伪」，图就在你脑子里。
""".format(rows=rows))
print("OK 00-总览.md")
