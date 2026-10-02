"""Generate the talk's illustrations as SVG (Obsidian embeds them with ![[...]]).

Run: python3 make_visuals.py
"""
import math
from pathlib import Path

OUT = Path(__file__).parent
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','WenQuanYi Zen Hei',sans-serif"

BG = "#FFF8F0"
INK = "#3A3330"
MUTED = "#8A7F78"
LINE = "#E8DDD3"
HEALTH = "#6DBE8C"
WORK = "#F2A541"
PLAY = "#5DADE2"
LOVE = "#EF6F6C"
PURPLE = "#A88BD8"


def svg(w, h, body, title=""):
    head = f'<text x="{w/2}" y="46" text-anchor="middle" font-size="26" font-weight="700" fill="{INK}">{title}</text>' if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">'
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="24" fill="{BG}"/>{head}{body}</svg>'
    )


def text(x, y, s, size=18, color=INK, weight=400, anchor="middle"):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{s}</text>'


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def donut(cx, cy, r, sw, parts, start=-90, label_r=None, label_size=17):
    """parts: list of (value, color, label). Values sum to 100. Drawn as explicit arcs."""
    out, acc = [], 0
    for value, color, label in parts:
        a0, a1 = start + acc * 3.6 + 0.6, start + (acc + value) * 3.6 - 0.6
        x0, y0 = polar(cx, cy, r, a0)
        x1, y1 = polar(cx, cy, r, a1)
        large = 1 if (a1 - a0) > 180 else 0
        out.append(f'<path d="M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} 1 {x1:.2f} {y1:.2f}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
        if label:
            mid = start + (acc + value / 2) * 3.6
            lx, ly = polar(cx, cy, label_r or r, mid)
            lines = label.split("\n")
            for i, line in enumerate(lines):
                out.append(text(lx, ly + 6 + i * 20 - (len(lines) - 1) * 10, line, label_size, "#fff", 700))
        acc += value
    return "".join(out)


# 1. Scale -> circle --------------------------------------------------------
def scale_vs_circle():
    b = []
    # left: scale
    b.append(text(220, 100, "以前的想法：天平 ⚖️", 20, MUTED, 700))
    b.append(f'<line x1="220" y1="140" x2="220" y2="330" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<path d="M180 340 h80" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>')
    b.append(f'<g transform="rotate(-8 220 150)"><line x1="90" y1="150" x2="350" y2="150" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
             f'<line x1="100" y1="150" x2="100" y2="210" stroke="{MUTED}" stroke-width="2"/><line x1="340" y1="150" x2="340" y2="210" stroke="{MUTED}" stroke-width="2"/>'
             f'<rect x="50" y="210" width="100" height="56" rx="14" fill="{WORK}"/><rect x="290" y="210" width="100" height="56" rx="14" fill="{HEALTH}"/>'
             + text(100, 246, "工作", 22, "#fff", 700) + text(340, 246, "生活", 22, "#fff", 700) + "</g>")
    b.append(text(220, 390, "一边多，另一边就少", 18, MUTED))
    # arrow
    b.append(f'<path d="M420 230 h70" stroke="{MUTED}" stroke-width="5" stroke-linecap="round"/><path d="M478 216 l16 14 -16 14" fill="none" stroke="{MUTED}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    # right: circle
    b.append(text(700, 100, "我的想法：一个圆 🥧", 20, INK, 700))
    parts = [(22, LOVE, "family"), (16, PLAY, "朋友"), (16, HEALTH, "health"), (14, PURPLE, "学习"), (12, "#4FB3A9", "旅行"), (20, WORK, "工作")]
    b.append(donut(700, 240, 100, 70, parts, label_size=16))
    b.append(text(700, 248, "Life", 26, INK, 700))
    b.append(text(700, 390, "工作只是其中一块", 18, INK, 700))
    return svg(920, 430, "".join(b))


# 2. 8-8-8 clock -------------------------------------------------------------
def clock_888():
    b = [donut(260, 220, 110, 80, [(100 / 3, WORK, "工作\n8 小时"), (100 / 3, PLAY, "休息\n8 小时"), (100 / 3, HEALTH, "自己\n8 小时")], label_size=17)]
    b.append(text(260, 228, "24h", 26, INK, 700))
    b.append(text(560, 160, "1817 年 · 工厂时代", 22, INK, 700, "start"))
    b.append(text(560, 200, "Robert Owen 提出", 18, MUTED, 400, "start"))
    b.append(text(560, 228, "「8 小时工作、8 小时休息、", 18, MUTED, 400, "start"))
    b.append(text(560, 256, "  8 小时做自己的事」", 18, MUTED, 400, "start"))
    b.append(text(560, 304, "👉 为了保护工人才画的线", 19, INK, 700, "start"))
    return svg(900, 400, "".join(b), "工作和生活「分开」，其实没有很久")


# 3. Life dashboard (own illustration of the Designing Your Life idea) -------
def dashboard():
    gauges = [("💪", "健康", "Health", HEALTH, 0.65), ("💼", "工作", "Work", WORK, 0.8), ("🎨", "玩乐", "Play", PLAY, 0.35), ("❤️", "爱", "Love", LOVE, 0.7)]
    b = []
    for i, (emo, zh, en, color, f) in enumerate(gauges):
        cx, cy, r = 130 + i * 220, 230, 80
        arc = f"M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r} {cy}"
        b.append(f'<rect x="{cx - 100}" y="90" width="200" height="270" rx="20" fill="#fff" stroke="{LINE}" stroke-width="2"/>')
        b.append(f'<path d="{arc}" fill="none" stroke="{LINE}" stroke-width="22" stroke-linecap="round"/>')
        b.append(f'<path d="{arc}" fill="none" stroke="{color}" stroke-width="22" stroke-linecap="round" pathLength="100" stroke-dasharray="{f * 100} 100"/>')
        b.append(f'<g transform="rotate({180 * f} {cx} {cy})"><line x1="{cx}" y1="{cy}" x2="{cx - 60}" y2="{cy}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/></g>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{INK}"/>')
        b.append(text(cx - r, cy + 30, "空", 14, MUTED) + text(cx + r, cy + 30, "满", 14, MUTED))
        b.append(text(cx, 140, emo, 26))
        b.append(text(cx, 300, zh, 26, INK, 700) + text(cx, 330, en, 17, color, 700))
    b.append(text(460, 400, "现在每一个油表，是满的，还是快没油了？", 19, INK, 700))
    b.append(text(460, 428, "概念来自《Designing Your Life》· Bill Burnett &amp; Dave Evans（Stanford）", 14, MUTED))
    return svg(920, 450, "".join(b), "人生的四个油表")


# 4. Job title explodes into 9 things ---------------------------------------
def job_explode():
    cx, cy = 460, 290
    items = [("🏢", "环境"), ("👥", "人脉"), ("👀", "exposure"), ("🛠️", "skills"), ("📈", "experience"),
             ("💰", "income"), ("🪜", "career ladder"), ("🚀", "未来机会"), ("📚", "learning")]
    colors = [HEALTH, PLAY, PURPLE, WORK, LOVE, "#4FB3A9", WORK, PLAY, HEALTH]
    b = []
    for i, ((emo, label), c) in enumerate(zip(items, colors)):
        x, y = polar(cx, cy, 200, -90 + i * 40)
        y = cy + (y - cy) * 0.82
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{LINE}" stroke-width="3" stroke-dasharray="6 6"/>')
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="48" fill="#fff" stroke="{c}" stroke-width="4"/>')
        b.append(text(x, y - 2, emo, 24) + text(x, y + 22, label, 12 if len(label) > 10 else 14 if len(label) > 6 else 16, INK, 700))
    b.append(f'<rect x="{cx - 80}" y="{cy - 38}" width="160" height="76" rx="16" fill="{INK}"/>')
    b.append(text(cx, cy - 4, "Job Title", 22, "#fff", 700) + text(cx, cy + 22, "一个职位", 15, "#E8DDD3"))
    return svg(920, 560, "".join(b), "选一份工作 = 选一种生活方式")


# 5. Nutrition: connect the dots ---------------------------------------------
def connect_dots():
    sx, sy = 170, 260
    ends = [(700, 120, "🍱 食品", HEALTH, False), (720, 220, "🧪 产品开发", WORK, False),
            (700, 320, "🩺 健康相关", PLAY, False), (720, 420, "❓ 完全不同的方向", PURPLE, True)]
    b = []
    for ex, ey, label, c, dashed in ends:
        dash = ' stroke-dasharray="10 10"' if dashed else ""
        b.append(f'<path d="M{sx} {sy} C {sx + 220} {sy}, {ex - 260} {ey}, {ex - 20} {ey}" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"{dash}/>')
        b.append(f'<circle cx="{ex - 20}" cy="{ey}" r="12" fill="{c}"/>')
        b.append(text(ex, ey + 7, label, 20, INK, 700, "start"))
    b.append(f'<circle cx="{sx}" cy="{sy}" r="60" fill="{HEALTH}"/>')
    b.append(text(sx, sy - 4, "Nutrition", 20, "#fff", 700) + text(sx, sy + 22, "起点", 16, "#fff"))
    b.append(text(460, 500, "“You can't connect the dots looking forward.” — Steve Jobs", 17, MUTED))
    return svg(920, 530, "".join(b), "读 Nutrition，不等于只能当营养师")


# 6. Life path: 3 stages vs many stages --------------------------------------
def life_path():
    b = [text(60, 110, "以前", 20, MUTED, 700, "start")]
    for i, (label, c) in enumerate([("读书", PLAY), ("工作", WORK), ("退休", MUTED)]):
        x = 140 + i * 250
        b.append(f'<rect x="{x}" y="88" width="230" height="34" rx="17" fill="{c}"/>')
        b.append(text(x + 115, 112, label, 18, "#fff", 700))
    b.append(text(60, 230, "现在", 20, INK, 700, "start"))
    stops = [(150, 300, "读书", PLAY), (290, 200, "工作", WORK), (430, 300, "回去读书", PLAY),
             (570, 200, "gap year", HEALTH), (710, 300, "换方向", PURPLE), (850, 200, "60 岁学新东西", LOVE)]
    d = f"M{stops[0][0]} {stops[0][1]}"
    for (x0, y0, *_), (x1, y1, *_) in zip(stops, stops[1:]):
        m = (x1 - x0) / 2
        d += f" C {x0 + m} {y0}, {x1 - m} {y1}, {x1} {y1}"
    b.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 12"/>')
    for x, y, label, c in stops:
        b.append(f'<circle cx="{x}" cy="{y}" r="14" fill="{c}" stroke="#fff" stroke-width="4"/>')
        b.append(text(x, y + 42 if y > 250 else y - 28, label, 16, INK, 700))
    b.append(text(470, 400, "参考：《The 100-Year Life》· Lynda Gratton &amp; Andrew Scott", 14, MUTED))
    return svg(940, 420, "".join(b), "人生不再是一条直线")


# 7. Boundary spectrum --------------------------------------------------------
def spectrum():
    b = ['<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#5DADE2"/><stop offset="1" stop-color="#F2A541"/></linearGradient></defs>']
    b.append('<rect x="120" y="170" width="680" height="26" rx="13" fill="url(#g)"/>')
    for x in (230, 470, 690):
        b.append(f'<circle cx="{x}" cy="183" r="18" fill="#fff" stroke="{INK}" stroke-width="3"/>')
        b.append(text(x, 154, "🙂", 26))
    b.append(text(150, 250, "🚪 分得很清楚", 20, INK, 700, "start"))
    b.append(text(150, 278, "下班就是下班，周末不碰工作", 16, MUTED, 400, "start"))
    b.append(text(770, 250, "混在一起也 OK 🔄", 20, INK, 700, "end"))
    b.append(text(770, 278, "想到就处理一下，不介意", 16, MUTED, 400, "end"))
    b.append(f'<rect x="200" y="310" width="520" height="56" rx="28" fill="#fff" stroke="{LINE}" stroke-width="2"/>')
    b.append(text(460, 345, "两种都没有错 —— 重点是适不适合你", 20, INK, 700))
    b.append(text(460, 400, "研究参考：Ashforth et al. (2000) · Kreiner (2006)", 14, MUTED))
    return svg(920, 420, "".join(b), "每个人都站在不同的位置")


# 8. 9pm message --------------------------------------------------------------
def message_9pm():
    b = []
    cards = [(110, "😩", "唉，真的不想回……", "可是不回不行。", "#FDE3E2", LOVE, "被逼的"),
             (500, "😊", "这个 project 我很在意，", "花五分钟回一下 OK。", "#E1F3E8", HEALTH, "自己选的")]
    for x, face, l1, l2, bub, c, tag in cards:
        b.append(f'<rect x="{x}" y="80" width="310" height="320" rx="32" fill="#fff" stroke="{LINE}" stroke-width="3"/>')
        b.append(text(x + 155, 126, "🕘 21:00", 20, MUTED, 700))
        b.append(f'<rect x="{x + 25}" y="150" width="260" height="90" rx="18" fill="{bub}"/>')
        b.append(text(x + 155, 188, l1, 17, INK, 700) + text(x + 155, 216, l2, 17, INK, 700))
        b.append(text(x + 155, 310, face, 54))
        b.append(f'<rect x="{x + 95}" y="340" width="120" height="36" rx="18" fill="{c}"/>')
        b.append(text(x + 155, 364, tag, 17, "#fff", 700))
    b.append(text(460, 250, "vs", 28, MUTED, 700))
    b.append(text(460, 440, "做的事一样，感觉完全不一样 —— 差别是：是不是自己选的", 19, INK, 700))
    return svg(920, 470, "".join(b), "同样是晚上九点回 message")


# 9. Work slice changes over time --------------------------------------------
def work_slice():
    stages = [("现在", "想学、想看多一点", 45), ("几年后", "多陪 family、顾 health", 30), ("再以后", "也许去旅行、学新东西", 20)]
    b = []
    for i, (when, why, w) in enumerate(stages):
        cx = 160 + i * 300
        rest = 100 - w
        b.append(donut(cx, 220, 80, 56, [(w, WORK, "工作"), (rest, "#CFE6D8", "")], label_size=16))
        b.append(text(cx, 345, when, 22, INK, 700) + text(cx, 375, why, 16, MUTED))
        if i < 2:
            b.append(f'<path d="M{cx + 120} 220 h50" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/><path d="M{cx + 160} 210 l12 10 -12 10" fill="none" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/>')
    b.append(text(460, 420, "那条线是我自己画的，也可以自己移", 20, INK, 700))
    return svg(920, 450, "".join(b), "工作的位置，会跟着人生调整")


FILES = {
    "01-scale-vs-circle.svg": scale_vs_circle,
    "02-888-clock.svg": clock_888,
    "03-life-dashboard.svg": dashboard,
    "04-job-explode.svg": job_explode,
    "05-connect-dots.svg": connect_dots,
    "06-life-path.svg": life_path,
    "07-boundary-spectrum.svg": spectrum,
    "08-message-9pm.svg": message_9pm,
    "09-work-slice.svg": work_slice,
}

if __name__ == "__main__":
    for name, fn in FILES.items():
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", name)
