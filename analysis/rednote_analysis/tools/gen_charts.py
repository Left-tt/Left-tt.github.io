# -*- coding: utf-8 -*-
"""生成《小红书TikTok难民潮数据产品分析报告》插图（图1-图7）"""
import os
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
os.makedirs(OUT, exist_ok=True)

# ---------- 中文字体 ----------
CAND = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
font_path = next((p for p in CAND if os.path.exists(p)), None)
if font_path:
    try:
        fm.fontManager.addfont(font_path)
        fname = fm.FontProperties(fname=font_path).get_name()
        plt.rcParams["font.family"] = fname
    except Exception as e:
        print("font warn:", e)
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#1F4E79"
BLUE = "#2E75B6"
LBLUE = "#9DC3E6"
ORANGE = "#ED7D31"
RED = "#C00000"
GREEN = "#548235"
GRAY = "#7F7F7F"
LIGHT = "#DEEBF7"
LIGHT_ORANGE = "#FBE5D6"
LIGHT_GRAY = "#F2F2F2"
LIGHT_GREEN = "#E2EFDA"

D = dt.date


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight", facecolor="white", dpi=170)
    plt.close(fig)
    print("saved", p)


# ---------- 图1：美区DAU脉冲 ----------
def fig1():
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    dates = [D(2025, 1, 8), D(2025, 1, 12), D(2025, 1, 15), D(2025, 1, 18),
             D(2025, 1, 22), D(2025, 1, 24), D(2025, 2, 5), D(2025, 3, 15)]
    dau = [30, 120, 340, 330, 220, 170, 120, 80]
    ax.fill_between(dates, dau, 0, color=LIGHT, alpha=0.7, zorder=1)
    ax.plot(dates, dau, color=NAVY, lw=2.6, marker="o", ms=5.5,
            mfc="white", mew=2, mec=NAVY, zorder=3)
    anns = [
        (D(2025, 1, 8), 30, "基线≈30万", (0, 12)),
        (D(2025, 1, 15), 340, "峰值≈340万\n(Similarweb, 1/15-17)", (0, 8)),
        (D(2025, 1, 24), 170, "回流后≈170万\n(TechCrunch, 1/24)", (-38, -40)),
        (D(2025, 3, 15), 80, "稳态≈80万\n(Rest of World, 3月)", (-42, 12)),
    ]
    for d, v, t, off in anns:
        ax.annotate(t, (d, v), textcoords="offset points", xytext=off,
                    ha="center", fontsize=9.5, color="#333333",
                    arrowprops=dict(arrowstyle="-", color="#999999", lw=0.8))
    events = [
        (D(2025, 1, 13), "1/13 登顶美区\n免费榜", 385),
        (D(2025, 1, 19), "1/19 禁令生效\nTikTok停服约14h", 345),
        (D(2025, 1, 21), "1/21 75天暂缓令", 305),
        (D(2025, 1, 24), "1/24 用户回流", 265),
    ]
    for d, t, y in events:
        ax.axvline(d, color=GRAY, ls="--", lw=1, alpha=0.65, zorder=2)
        ax.text(d, y, t, ha="center", va="bottom", fontsize=8.3, color="#595959")
    ax.set_ylim(0, 430)
    ax.set_ylabel("美区DAU（万人，第三方公开估算）", fontsize=10)
    ax.set_title("图1 小红书美区DAU脉冲：30万 → 340万 → 80万", fontsize=13, pad=12)
    ax.grid(axis="y", color="#E0E0E0", lw=0.7)
    ax.set_axisbelow(True)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    fig.text(0.01, 0.005,
             "数据源：Similarweb（经199it/腾讯财经转引）、TechCrunch、Rest of World；第三方估算，仅示趋势与量级，非平台官方数据",
             fontsize=8, color="#7F7F7F")
    save(fig, "fig1_dau_pulse.png")


# ---------- 图2：推荐机制示意 ----------
def fig2():
    fig, ax = plt.subplots(figsize=(11.2, 6.4))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 8.6)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, fs=10.3, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.08,rounding_size=0.12",
                     fc=fc, ec=ec, lw=1.5))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, weight="bold" if bold else "normal", color="#1a1a1a")

    box(0.2, 6.3, 3.5, 1.7, "① 供给脉冲\n海外内容供给爆发", LIGHT, BLUE)
    box(4.45, 6.3, 3.5, 1.7, "② 热度信号放大\n点击/互动/关注暴涨", LIGHT, BLUE)
    box(8.7, 6.3, 3.5, 1.7, "③ 分人群正反馈\n交互过的用户被持续放大", LIGHT, BLUE)
    box(8.7, 3.3, 3.5, 1.7, "④ 体感：信息流被“占领”\n（“10条9条”，S4轶事）", LIGHT_ORANGE, ORANGE)
    box(0.2, 3.3, 3.5, 1.7, "未交互用户：影响有限\n（另一部分人“无感”）", LIGHT_GRAY, GRAY)
    box(2.9, 0.9, 7.2, 1.6, "平台响应：治理三件套（英文审核 · 紧急隔离 · 翻译基建）\n无“全局调权”的公开证据（36氪《小红书紧急隔离》等）",
        LIGHT_GREEN, GREEN, fs=9.8)

    def arrow(p1, p2, color=GRAY, style="-", rad=0.0, lw=1.6):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>",
                     mutation_scale=16, color=color, lw=lw,
                     linestyle=style, connectionstyle=f"arc3,rad={rad}"))

    arrow((3.7, 7.15), (4.45, 7.15), NAVY, lw=2.0)
    arrow((7.95, 7.15), (8.7, 7.15), NAVY, lw=2.0)
    arrow((10.45, 6.3), (10.45, 5.0), NAVY, lw=2.0)
    arrow((5.6, 6.3), (2.4, 5.0), GRAY, style="--", rad=0.2)
    arrow((10.3, 3.3), (8.3, 2.5), ORANGE, lw=1.6)
    arrow((1.9, 3.3), (4.2, 2.5), GRAY, lw=1.6)
    ax.text(6.7, 7.45, "热度信号点燃通用推荐模型", fontsize=9, color=NAVY, ha="center")
    ax.text(10.45, 5.65, "个性化\n放大", fontsize=8.5, color=NAVY, ha="center")
    ax.text(3.9, 5.75, "无交互则不激活", fontsize=8.5, color=GRAY, ha="center")
    ax.text(6.2, 8.35, "图2 推荐系统“被动突变”机制示意（分析师推断，待内部数据验证）",
            fontsize=13, ha="center", weight="bold", color="#1a1a1a")
    save(fig, "fig2_reco_mechanism.png")


# ---------- 图3：翻译功能时间线 ----------
def fig3():
    fig, ax = plt.subplots(figsize=(11.4, 3.8))
    ax.set_xlim(-0.6, 10.6)
    ax.set_ylim(-3.4, 3.4)
    ax.axis("off")
    ax.plot([0, 10], [0, 0], color=NAVY, lw=2.4, zorder=1)
    ev = [
        (0, 1, "01-19 一键翻译上线\n（光明网报道）"),
        (2.4, -1, "01-20 “Prompt狂欢”爆发\n热梗翻译刷屏（36氪《小红书搭起巴别塔》）"),
        (4.7, 1, "01-20 工程师连夜封堵\n提示注入漏洞（智东西）"),
        (6.9, -1, "01-21 网络缩写实测：YYDS / XSWL /\nCPDD / nsdd 均可翻译（星岛等）"),
        (9.1, 1, "后续 持续迭代\n覆盖率扩展 · 滥用防护强化"),
    ]
    for x, side, t in ev:
        ax.plot(x, 0, "o", ms=8, mfc="white", mec=BLUE, mew=2.2, zorder=3)
        ax.text(x, side * 0.55, t, ha="center",
                va="bottom" if side > 0 else "top", fontsize=9.2, color="#1a1a1a")
    ax.text(5, 3.0, "图3 翻译功能上线与攻防节奏（2025年1月）", fontsize=13,
            ha="center", weight="bold", color="#1a1a1a")
    fig.text(0.01, 0.005, "来源：光明网、36氪、智东西、星岛头条（S1/S3）。",
             fontsize=8, color="#7F7F7F")
    save(fig, "fig3_translation_timeline.png")


# ---------- 图4：翻译成本对比 ----------
def fig4():
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    cats = ["NMT\n（传统神经机器翻译）", "LLM\n（小红书方案）"]
    vals = [1, 10]
    colors = [GRAY, ORANGE]
    bars = ax.bar(cats, vals, width=0.52, color=colors, edgecolor="#404040", lw=0.8)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.35, f"{v}×" if v > 1 else "1×",
                ha="center", fontsize=13, weight="bold", color="#1a1a1a")
    ax.annotate("“约10倍”为行业估算口径（S3）\n注入/滥用调用会进一步放大实际成本",
                xy=(1, 10.2), xytext=(0.55, 11.6), fontsize=9.5, color=RED,
                ha="center",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.set_ylim(0, 12.6)
    ax.set_ylabel("单次翻译相对成本（倍）", fontsize=10)
    ax.set_title("图4 单次翻译相对成本：NMT vs LLM", fontsize=13, pad=10)
    ax.grid(axis="y", color="#E0E0E0", lw=0.7)
    ax.set_axisbelow(True)
    fig.text(0.01, 0.005, "小红书未披露翻译成本；本图为行业估算示意，需内部核算验证。",
             fontsize=8, color="#7F7F7F")
    save(fig, "fig4_translation_cost.png")


# ---------- 图5：翻译价值漏斗 ----------
def fig5():
    fig, ax = plt.subplots(figsize=(9.6, 6.0))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.6)
    ax.axis("off")
    cx = 4.2
    widths = [7.4, 5.4, 3.5, 2.0]
    ys = [(7.3, 6.15), (5.75, 4.6), (4.2, 3.05), (2.65, 1.5)]
    labels = ["① 可翻译内容曝光", "② 点击翻译", "③ 翻译后互动", "④ 关注 / 留存"]
    metrics = [
        "指标：翻译渗透率",
        "指标：人均日调用次数",
        "★北极星：翻译后互动转化率",
        "指标：跨语言互动率 / 留存贡献",
    ]
    shades = [NAVY, BLUE, "#5B9BD5", LBLUE]
    for w1, w2, (yt, yb), lab, met, c in zip(
            widths, widths[1:] + [widths[-1]], ys, labels, metrics, shades):
        poly = Polygon([(cx - w1 / 2, yt), (cx + w1 / 2, yt),
                        (cx + w2 / 2, yb), (cx - w2 / 2, yb)],
                       fc=c, ec="#404040", lw=0.8, alpha=0.92)
        ax.add_patch(poly)
        ax.text(cx, (yt + yb) / 2, lab, ha="center", va="center",
                fontsize=10.5, color="white", weight="bold")
        ax.text(8.3, (yt + yb) / 2, met, ha="left", va="center",
                fontsize=9.5, color="#333333")
    for i, (x, y) in enumerate([(8.3, 6.72), (8.3, 5.17), (8.3, 3.62), (8.3, 2.07)]):
        pass
    ax.text(5.5, 8.3, "图5 翻译功能价值漏斗与核心指标", fontsize=13,
            ha="center", weight="bold", color="#1a1a1a")
    ax.text(5.5, 0.55, "示意图：漏斗比例为示意（无公开数值），各环节数据待内部埋点填充。",
            fontsize=8.5, ha="center", color="#7F7F7F")
    save(fig, "fig5_translation_funnel.png")


# ---------- 图6：留存估算区间 ----------
def fig6():
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    x = [1, 7, 14, 30, 60, 90]
    med = [65, 42, 32, 26, 18, 15]
    band = 8
    ax.fill_between(x, [max(0, m - band) for m in med], [m + band for m in med],
                    color=LIGHT, alpha=0.85, label="估算区间（±8pp假设带宽）")
    ax.plot(x, med, color=NAVY, lw=2.6, marker="o", ms=5.5,
            mfc="white", mew=2, mec=NAVY, label="估算中位路径")
    ax.axvspan(24, 36, color=LIGHT_GREEN, alpha=0.65)
    ax.text(30, 93, "社交类App 30日留存\n中位区间 20%-30%（示意）",
            ha="center", fontsize=8.5, color=GREEN)
    for xi, m in zip(x, med):
        ax.annotate(f"{m}%", (xi, m), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=9, color="#1a1a1a")
    ax.annotate("锚点：公开DAU/累计新增\n≈80万/300万 ≈ 26%\n(Rest of World, 2025-03)",
                xy=(30, 26), xytext=(38, 12), fontsize=8.8, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.set_xticks(x)
    ax.set_xlabel("注册后天数", fontsize=10)
    ax.set_ylabel("留存率（%）", fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_title("图6 海外新增用户留存曲线（估算区间带）", fontsize=13, pad=10)
    ax.grid(axis="y", color="#E0E0E0", lw=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc="center right", fontsize=8.5)
    fig.text(0.01, 0.005, "月留存粗估20%-35%；全部为基于公开数据的估算，需内部验证。",
             fontsize=8, color="#7F7F7F")
    save(fig, "fig6_retention_band.png")


# ---------- 图7：同池→分池演进 ----------
def fig7():
    fig, ax = plt.subplots(figsize=(11.4, 5.6))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    boxes = [
        (0.2, "阶段一 2025.01", "全球同池", "同版本 · 同社区 · 同内容池\n“地球村”叙事", LIGHT, BLUE),
        (4.55, "阶段二 2025", "治理加固", "英文审核扩容 · 翻译基建\n紧急隔离（36氪）", "#DCE9F7", "#5B9BD5"),
        (8.9, "阶段三 2026.04", "架构分池", "中外账号分拆 · 数据迁新加坡\n独立网域 · 条款差异", LIGHT_GREEN, GREEN),
    ]
    y, w, h = 1.9, 3.6, 3.0
    for x, t1, t2, t3, fc, ec in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.08,rounding_size=0.14",
                     fc=fc, ec=ec, lw=1.6))
        ax.text(x + w / 2, y + h - 0.5, t1, ha="center", fontsize=9.5,
                color="#595959", weight="bold")
        ax.text(x + w / 2, y + h / 2 + 0.18, t2, ha="center", fontsize=13,
                color="#1a1a1a", weight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.72, t3, ha="center", va="center",
                fontsize=9.8, color="#333333")
    ax.add_patch(FancyArrowPatch((3.8, 3.4), (4.55, 3.4), arrowstyle="-|>",
                 mutation_scale=18, color=GRAY, lw=2.0))
    ax.add_patch(FancyArrowPatch((8.15, 3.4), (8.9, 3.4), arrowstyle="-|>",
                 mutation_scale=18, color=GRAY, lw=2.0))
    ax.text(4.17, 3.85, "治理压力累积", ha="center", fontsize=8.8, color="#595959")
    ax.text(8.52, 3.85, "合规与商业化落地", ha="center", fontsize=8.8, color="#595959")
    ax.text(6.4, 6.0, "图7 “全球同池”实验的三阶段演进（2025.01 → 2026.04）",
            fontsize=13, ha="center", weight="bold", color="#1a1a1a")
    fig.text(0.01, 0.01, "依据：unwire / WIRED《Rednote Draws a Line Between China and the World》/ Bamboo Works（2026-04，S2/S3）。",
             fontsize=8, color="#7F7F7F")
    save(fig, "fig7_evolution.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    print("done")
