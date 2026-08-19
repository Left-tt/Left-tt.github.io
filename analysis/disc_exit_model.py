#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIE 内部可行性分析(FAR)量化模型:实体游戏光盘退场的经济影响评估
=============================================================
作者: 首席数据分析师(模拟)
说明:
  - 模型以 FY2025 公开财报/行业数据为锚点,所有假设集中在 BASE 与 SCENARIOS。
  - 计算四种情景(A 维持现状 / B 分阶段退场 / C 激进一刀切 / D 分阶段+缓释)相对
    情景A的5年ΔEBIT(单位:十亿美元),并给出NPV、敏感性(龙卷风图)与盈亏平衡面。
  - 所有参数均为确定性假设(无随机项),结果可复现。
单位约定:金额 $B(十亿美元);盘/份数量 M(百万)。
"""

import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------
# 中文字体探测(macOS / Linux / Windows 常见字体)
# ---------------------------------------------------------------
from matplotlib import font_manager

CJK_FONTS = [
    "PingFang SC", "Hiragino Sans GB", "Heiti SC", "Songti SC",
    "Arial Unicode MS", "Noto Sans CJK SC", "Microsoft YaHei", "SimHei",
]
_available = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in CJK_FONTS if f in _available), None)
if FONT:
    plt.rcParams["font.sans-serif"] = [FONT, "DejaVu Sans"]
else:
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    FONT = None
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CHARTS = os.path.join(HERE, "..", "charts")
OUT_DATA = os.path.join(HERE, "..", "analysis")
os.makedirs(OUT_CHARTS, exist_ok=True)
os.makedirs(OUT_DATA, exist_ok=True)

YEARS = ["FY2026", "FY2027", "FY2028", "FY2029", "FY2030"]

# ---------------------------------------------------------------
# 基线锚点(FY2025,美元计,公开数据近似)
# ---------------------------------------------------------------
BASE = {
    # 数字业务:软件+附加内容+网络服务,索尼口径收入与综合贡献利润率
    "rev_digital": 19.0,       # $B / 年
    "m_digital": 0.68,         # 数字业务综合贡献利润率
    "g_digital_org": 0.04,     # 数字业务自然年增速(无决策干预时)

    # 实体业务:约7000万张/年,仅占PlayStation总营收约3%
    "rev_physical": 0.90,      # $B / 年,索尼从实体软件中拿到的直接收入
    "m_physical": 0.45,        # 实体业务贡献利润率(压盘/物流/退货拨备后)
    "n_discs": 70.0,           # 百万张 / 年
    "d_physical_org": -0.12,   # 实体自然年衰减率(数字迁移+零售萎缩)

    # 二手市场:全球$7.2B,假设PlayStation占约一半
    "used_units_ps": 70.0,     # 百万份 / 年(PS二手交易量,估计)
    "used_gmv_ps": 3.6,        # $B / 年(PS二手交易额,估计)
    "net_take_used_digital": 30.0,  # 二手买家转数字时,索尼每份净收入($)

    # 其他
    "discount": 0.10,          # 折现率(WACC近似)
    "price_sensitive_share": 0.25,  # 数字业务中对价格敏感(依赖二手流动性)的部分
}

# 单张实体盘给索尼的收入(≈0.9B/70M)
BASE["rev_per_disc_sony"] = BASE["rev_physical"] * 1e9 / (BASE["n_discs"] * 1e6)  # ≈$12.9

# 实体买家转数字后,索尼单份净收入(第一方净得~$45、第三方版税~$19,加权≈$35)
NET_TAKE_DIGITAL = 35.0
# 未即时转化的"观望"买家最终以促销/订阅方式进入数字生态时的净收入(折扣后≈$20)
NET_TAKE_DEFERRED = 20.0
STICK_PER_UNIT = 5.25     # 转化后每位用户每年额外数字消费(游戏+订阅增量),$
LTV_PER_CHURNED = 20.0    # 流失的实体用户每年损失的数字生态价值(游戏+服务),$
COST_SAVING_PER_DISC = 3.5  # 每少压一张盘,索尼节省的压盘/物流/退货成本,$

# ---------------------------------------------------------------
# 情景定义
# phase: 各年实体盘生产保留比例(相对基线自然水平)
# phi : 实体需求中全价转化到数字的比例
# chi : 实体需求中流失/外溢(PC、其他平台、退坑)的比例
#       其余 1-phi-chi 为"观望者",最终以折扣/订阅方式转入数字生态
# psi : 二手买家中转化到数字的比例
# lam : 二手流动性消失对价格敏感数字消费的拖累系数
# theta: 玩家抵制/品牌受损导致的数字生态贡献损失比例(逐年)
# ---------------------------------------------------------------
SCENARIOS = {
    "A": dict(name="A 维持现状(基线)", phase=[1, 1, 1, 1, 1],
              phi=0.0, chi=0.0, psi=0.0, lam=0.0, theta=[0, 0, 0, 0, 0],
              retailer=[0, 0, 0, 0, 0], price_uplift=0.0, liq_start=99,
              mitigation=[0, 0, 0, 0, 0], collector=[0, 0, 0, 0, 0],
              used_timing=[0, 0, 0, 0, 0]),
    "B": dict(name="B 分阶段退场(2年过渡)",
              phase=[1, 0.5, 0.0, 0.0, 0.0],
              phi=0.60, chi=0.15, psi=0.25, lam=0.06,
              theta=[0.0, 0.015, 0.010, 0.005, 0.0],
              retailer=[0, 0, 0.03, 0.03, 0.03],
              price_uplift=0.005, liq_start=2,
              mitigation=[0, 0, 0, 0, 0], collector=[0, 0, 0, 0, 0],
              used_timing=[0, 0.5, 0.5, 0, 0]),
    "C": dict(name="C 激进一刀切(立即停产)",
              phase=[1, 0.0, 0.0, 0.0, 0.0],
              phi=0.50, chi=0.25, psi=0.15, lam=0.12,
              theta=[0.0, 0.030, 0.020, 0.010, 0.0],
              retailer=[0, 0.05, 0.05, 0.05, 0.05],
              price_uplift=0.005, liq_start=1,
              mitigation=[0, 0, 0, 0, 0], collector=[0, 0, 0, 0, 0],
              used_timing=[0, 1.0, 0, 0, 0]),
    "D": dict(name="D 分阶段+缓释方案(推荐)",
              phase=[1, 0.6, 0.12, 0.12, 0.12],
              phi=0.72, chi=0.10, psi=0.35, lam=0.04,
              theta=[0.0, 0.008, 0.005, 0.002, 0.0],
              retailer=[0, 0, 0.03, 0.03, 0.03],
              price_uplift=0.005, liq_start=2,
              mitigation=[0, 0.10, 0.10, 0.10, 0.0],   # 缓释项目成本(二手折抵/存档/让利)
              collector=[0, 0, 0.08, 0.08, 0.08],      # 收藏版/限量实体净贡献
              used_timing=[0, 0.5, 0.5, 0, 0]),
    "B_nb": dict(name="B 分阶段(假设零抵制)",  # 隔离"玩家反对"的成本
                 phase=[1, 0.5, 0.0, 0.0, 0.0],
                 phi=0.60, chi=0.15, psi=0.25, lam=0.06,
                 theta=[0, 0, 0, 0, 0],
                 retailer=[0, 0, 0.03, 0.03, 0.03],
                 price_uplift=0.005, liq_start=2,
                 mitigation=[0, 0, 0, 0, 0], collector=[0, 0, 0, 0, 0],
                 used_timing=[0, 0.5, 0.5, 0, 0]),
}

EFFECT_KEYS = ["conversion", "conversion_disc", "stickiness", "churn_direct",
               "churn_ltv", "used_conversion", "liquidity", "cost_saving",
               "backlash", "retailer", "price_uplift", "mitigation", "collector"]


def run_scenario(cfg):
    """返回 dict: yearly=[{year,delta,effects}], cum, npv"""
    yearly = []
    conv_base_prev = 0.0   # 累计转化用户(百万),用于次年粘性
    churn_base_prev = 0.0  # 累计流失用户(百万)
    cum = 0.0
    npv = 0.0
    for t, yr in enumerate(YEARS):
        discA = BASE["n_discs"] * (1 + BASE["d_physical_org"]) ** t
        discS = discA * cfg["phase"][t]
        elim = discA - discS  # 当年少压的盘(百万张)
        digC = (BASE["rev_digital"] * (1 + BASE["g_digital_org"]) ** t
                * BASE["m_digital"])  # 数字业务贡献($B)

        conv_units = elim * cfg["phi"]
        conversion = conv_units * (NET_TAKE_DIGITAL - BASE["rev_per_disc_sony"]) / 1e3
        churn_units = elim * cfg["chi"]
        deferred_units = max(0.0, elim - conv_units - churn_units)  # 观望者,最终折价转入数字
        conversion_disc = deferred_units * (NET_TAKE_DEFERRED - BASE["rev_per_disc_sony"]) / 1e3
        stickiness = (conv_base_prev) * STICK_PER_UNIT / 1e3
        churn_direct = churn_units * BASE["rev_per_disc_sony"] / 1e3
        churn_ltv = churn_base_prev * LTV_PER_CHURNED / 1e3
        used_conversion = (BASE["used_units_ps"] * cfg["psi"]
                           * BASE["net_take_used_digital"] / 1e3 * cfg["used_timing"][t])
        liquidity = (cfg["lam"] * BASE["price_sensitive_share"] * digC
                     if t >= cfg["liq_start"] else 0.0)
        cost_saving = elim * COST_SAVING_PER_DISC / 1e3
        backlash = cfg["theta"][t] * digC
        retailer = cfg["retailer"][t]
        price_uplift = cfg["price_uplift"] * digC if t >= cfg["liq_start"] + 1 else 0.0
        mitigation = cfg["mitigation"][t]
        collector = cfg["collector"][t]

        effects = dict(conversion=conversion, conversion_disc=conversion_disc,
                       stickiness=stickiness,
                       churn_direct=-churn_direct, churn_ltv=-churn_ltv,
                       used_conversion=used_conversion, liquidity=-liquidity,
                       cost_saving=cost_saving, backlash=-backlash,
                       retailer=-retailer, price_uplift=price_uplift,
                       mitigation=-mitigation, collector=collector)
        delta = sum(effects.values())
        cum += delta
        npv += delta / (1 + BASE["discount"]) ** (t + 1)
        yearly.append(dict(year=yr, delta=delta, effects=effects))
        conv_base_prev += conv_units + deferred_units  # 全部非流失买家进入数字生态
        churn_base_prev += churn_units
    return dict(yearly=yearly, cum=cum, npv=npv)


def main():
    results = {k: run_scenario(v) for k, v in SCENARIOS.items()}

    # ---------------- 情景对比图 ----------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    styles = {"A": ("#888", "-"), "B": ("#1f77b4", "-"), "C": ("#d62728", "-"),
              "D": ("#2ca02c", "-"), "B_nb": ("#1f77b4", "--")}
    for k, r in results.items():
        cumline = np.cumsum([y["delta"] for y in r["yearly"]])
        ax.plot(YEARS, cumline, styles[k][1], color=styles[k][0], lw=2.2,
                label=SCENARIOS[k]["name"], marker="o", ms=4)
    ax.axhline(0, color="#333", lw=1)
    ax.set_title("各情景相对基线(A)的累计ΔEBIT($B)")
    ax.set_ylabel("累计ΔEBIT,十亿美元")
    ax.set_xlabel("财年")
    ax.legend(fontsize=8.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_CHARTS, "fig_cumulative.png"), dpi=160)
    plt.close(fig)

    # ---------------- B情景年度效应分解 ----------------
    labels = {"conversion": "实体→数字转化(全价)", "conversion_disc": "观望者折价转化",
              "stickiness": "转化用户粘性",
              "churn_direct": "用户流失(直接)", "churn_ltv": "用户流失(LTV)",
              "used_conversion": "二手买家转化", "liquidity": "二手流动性拖累",
              "cost_saving": "压盘/物流节省", "backlash": "玩家抵制",
              "retailer": "零售渠道摩擦", "price_uplift": "定价权提升",
              "mitigation": "缓释投入", "collector": "收藏版收入"}
    rB = results["B"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(YEARS))
    n_eff = len(EFFECT_KEYS)
    w = 0.8 / n_eff
    cmap = plt.get_cmap("RdYlGn")
    for i, kk in enumerate(EFFECT_KEYS):
        vals = [y["effects"][kk] for y in rB["yearly"]]
        colors = []
        vmax = max(abs(v) for v in vals) if vals else 1
        for v in vals:
            norm = abs(v) / vmax if vmax else 0
            colors.append(cmap(0.5 + (0.5 if v >= 0 else -0.5) * norm))
        ax.bar(x + (i - n_eff / 2) * w, vals, w, label=labels[kk], color=colors, alpha=0.9)
    ax.axhline(0, color="#333", lw=1)
    ax.set_xticks(x, YEARS)
    ax.set_title("B情景(分阶段退场)年度ΔEBIT效应分解")
    ax.set_ylabel("ΔEBIT,十亿美元/年")
    ax.legend(fontsize=7, ncol=3, loc="lower right")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_CHARTS, "fig_components.png"), dpi=160)
    plt.close(fig)

    # ---------------- 龙卷风图(B情景NPV敏感性) ----------------
    base_npv = results["B"]["npv"]
    tornado = []
    variants = {
        "phi 实体转化率": (0.45, 0.75),
        "chi 用户流失率": (0.05, 0.25),
        "psi 二手转化率": (0.15, 0.35),
        "lam 流动性拖累": (0.02, 0.10),
        "theta 抵制强度": (0.5, 2.0),      # 乘数
        "used 二手交易量": (50.0, 90.0),   # 百万份
        "m_digital 数字利润率": (0.63, 0.73),
        "retailer 渠道摩擦": (0.0, 0.06),  # $B/年
    }
    for label, (lo, hi) in variants.items():
        def _npv(scale_or_val):
            cfg = dict(SCENARIOS["B"])
            if label == "theta 抵制强度":
                cfg["theta"] = [v * scale_or_val for v in SCENARIOS["B"]["theta"]]
            elif label == "used 二手交易量":
                bb = dict(BASE); bb["used_units_ps"] = scale_or_val
                return run_with_base(cfg, bb)["npv"]
            elif label == "phi 实体转化率":
                cfg["phi"] = scale_or_val
            elif label == "chi 用户流失率":
                cfg["chi"] = scale_or_val
            elif label == "psi 二手转化率":
                cfg["psi"] = scale_or_val
            elif label == "lam 流动性拖累":
                cfg["lam"] = scale_or_val
            elif label == "m_digital 数字利润率":
                bb = dict(BASE); bb["m_digital"] = scale_or_val
                return run_with_base(cfg, bb)["npv"]
            elif label == "retailer 渠道摩擦":
                cfg["retailer"] = [0, 0, scale_or_val, scale_or_val, scale_or_val]
            return run_scenario(cfg)["npv"]
        n_lo, n_hi = _npv(lo), _npv(hi)
        tornado.append((label, n_lo, n_hi))
    tornado.sort(key=lambda t: abs(t[2] - t[1]))
    fig, ax = plt.subplots(figsize=(9, 5))
    ypos = np.arange(len(tornado))
    for i, (label, lo, hi) in enumerate(tornado):
        ax.barh(i, hi - base_npv, left=base_npv, color="#2ca02c", alpha=0.85,
                height=0.6, label="高值" if i == 0 else None)
        ax.barh(i, lo - base_npv, left=base_npv, color="#d62728", alpha=0.85,
                height=0.6, label="低值" if i == 0 else None)
    ax.axvline(base_npv, color="#333", lw=1.2)
    ax.set_yticks(ypos, [t[0] for t in tornado], fontsize=9)
    ax.set_xlabel("B情景5年NPV($B)")
    ax.set_title(f"敏感性龙卷风图(中心值:基准NPV={base_npv:.2f}$B)")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_CHARTS, "fig_tornado.png"), dpi=160)
    plt.close(fig)

    # ---------------- 盈亏平衡面(phi × chi,B情景) ----------------
    phis = np.linspace(0.10, 0.90, 41)
    chis = np.linspace(0.02, 0.60, 41)
    grid = np.zeros((len(phis), len(chis)))
    for i, ph in enumerate(phis):
        for j, ch in enumerate(chis):
            cfg = dict(SCENARIOS["B"])
            cfg["phi"] = ph
            cfg["chi"] = min(ch, 1.0 - ph)  # 转化+流失不得超过100%
            grid[i, j] = run_scenario(cfg)["npv"]
    gmin, gmax = float(grid.min()), float(grid.max())
    print(f"[盈亏平衡面] NPV范围: {gmin:.2f} ~ {gmax:.2f}")
    fig, ax = plt.subplots(figsize=(8.5, 6))
    X, Y = np.meshgrid(chis, phis)
    cs = ax.contourf(X, Y, grid, levels=14, cmap="RdYlGn")
    ctr = ax.contour(X, Y, grid, levels=[0], colors="k", linewidths=2)
    if ctr.allsegs:
        ax.clabel(ctr, fmt="NPV=0")
    else:
        ax.text(0.5, 0.5, "网格范围内NPV均为正", transform=ax.transAxes,
                ha="center", va="center", fontsize=11, color="#333")
    ax.scatter([SCENARIOS["B"]["chi"]], [SCENARIOS["B"]["phi"]], marker="*",
               s=220, color="#1f77b4", zorder=5, label="B基准假设")
    ax.scatter([SCENARIOS["D"]["chi"]], [SCENARIOS["D"]["phi"]], marker="*",
               s=220, color="#2ca02c", zorder=5, label="D缓释方案假设")
    ax.set_xlabel("实体用户流失率 χ")
    ax.set_ylabel("实体→数字转化率 φ")
    ax.set_title("B情景5年NPV盈亏平衡面(φ × χ)")
    ax.legend(fontsize=9)
    fig.colorbar(cs, label="NPV($B)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_CHARTS, "fig_breakeven.png"), dpi=160)
    plt.close(fig)

    # ---------------- 数据输出 ----------------
    rows = []
    for k, r in results.items():
        for y in r["yearly"]:
            rows.append([SCENARIOS[k]["name"], y["year"],
                         round(y["delta"], 4),
                         round(y["effects"]["conversion"], 4),
                         round(y["effects"]["backlash"], 4),
                         round(y["effects"]["liquidity"], 4)])
    with open(os.path.join(OUT_DATA, "model_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "year", "delta_ebit_bn", "conversion", "backlash",
                    "liquidity_drag"])
        w.writerows(rows)

    summary = {
        k: {"name": SCENARIOS[k]["name"],
            "npv_5y_bn": round(r["npv"], 3),
            "cum_ebit_5y_bn": round(r["cum"], 3),
            "fy2027_delta": round(r["yearly"][1]["delta"], 3),
            "fy2028_delta": round(r["yearly"][2]["delta"], 3),
            "total_backlash_cost": round(
                -sum(y["effects"]["backlash"] for y in r["yearly"]), 3)}
        for k, r in results.items()
    }
    with open(os.path.join(OUT_DATA, "model_summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    backlash_cost = (results["B_nb"]["npv"] - results["B"]["npv"])
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n[玩家抵制成本(情景B)] 5年NPV口径 ≈ ${backlash_cost:.2f}B")
    print(f"[B基准] NPV={results['B']['npv']:.3f}B | D方案 NPV={results['D']['npv']:.3f}B "
          f"| C一刀切 NPV={results['C']['npv']:.3f}B")
    print("图表输出:", os.path.abspath(OUT_CHARTS))


def run_with_base(cfg, bb):
    """在自定义BASE下运行(用于敏感性)。"""
    saved = dict(BASE)
    BASE.clear(); BASE.update(bb)
    BASE["rev_per_disc_sony"] = BASE["rev_physical"] * 1e9 / (BASE["n_discs"] * 1e6)
    try:
        return run_scenario(cfg)
    finally:
        BASE.clear(); BASE.update(saved)


if __name__ == "__main__":
    main()
