"""
Israel: Political Corruption Trends from QoG Dataset
=====================================================
Maps V-Dem, World Bank, and ICRG corruption indices against
Likud government periods (1977–2024), with special focus on
the Netanyahu era (1996–99, 2009–present).

Key variables:
  vdem_corr    — V-Dem Political Corruption Index (0=clean, 1=corrupt)
  vdem_execorr — V-Dem Executive Corruption Index (0=clean, 1=corrupt)
  vdem_exbribe — V-Dem Executive Bribery (ordinal, higher=cleaner)
  vdem_exembez — V-Dem Executive Embezzlement (ordinal, higher=cleaner)
  wbgi_cce     — World Bank Control of Corruption Estimate (higher=better)
  icrg_qog     — ICRG Quality of Government composite (higher=better)
  ti_cpi       — TI Corruption Perceptions Index (higher=cleaner)
"""

import openpyxl, os, warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict

OUT = "israel_analysis_output"
os.makedirs(OUT, exist_ok=True)

# ── Load QoG data ─────────────────────────────────────────────────────────
wb = openpyxl.load_workbook("qog israel.xlsx", read_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0])
yr_idx = header.index("year")

def col(name):
    return header.index(name) if name in header else None

def series(name):
    i = col(name)
    if i is None:
        return np.array([]), np.array([])
    pts = [(rows[j][yr_idx], float(rows[j][i]))
           for j in range(1, len(rows))
           if rows[j][i] is not None]
    if not pts:
        return np.array([]), np.array([])
    yrs, vals = zip(*sorted(pts))
    return np.array(yrs), np.array(vals)

# ── Likud / Netanyahu government periods ─────────────────────────────────
LIKUD_GOV = [
    (1977, 1984, "Begin I-II\n(1977–84)",          0.15),
    (1984, 1992, "National Unity /\nShamir (1984–92)", 0.07),  # lighter — shared
    (1996, 1999, "Netanyahu I\n(1996–99)",          0.15),
    (2001, 2006, "Sharon\n(2001–06)",               0.09),
    (2009, 2024, "Netanyahu II–VI\n(2009–24)",      0.15),
]

NETANYAHU = [
    (1996, 1999),
    (2009, 2024),
]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "figure.dpi": 150,
})

def shade_gov(ax, label_y, fontsize=6.5, col="#1a6bb5"):
    for s, e, lbl, alp in LIKUD_GOV:
        ax.axvspan(s, e, alpha=alp, color=col, zorder=0)
        ax.text((s+e)/2, label_y, lbl, ha="center", va="top",
                fontsize=fontsize, color="#1a3a6b", alpha=0.85, style="italic")

def shade_netanyahu_only(ax, label_y):
    """Stronger highlight for Netanyahu-only periods."""
    for s, e in NETANYAHU:
        ax.axvspan(s, e, alpha=0.18, color="#c0392b", zorder=0)

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 12 — Main 4-panel corruption dashboard
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 15))
fig.suptitle(
    "Israel: Political Corruption Trends, 1948–2024\n"
    "QoG Standard Dataset | Blue shading = Likud-led governments | "
    "Red shading = Netanyahu-specifically",
    fontsize=14, fontweight="bold", y=0.995,
)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)

# ── Panel A: V-Dem Political Corruption Index (overall) ──────────────────
ax_a = fig.add_subplot(gs[0, 0])
ax_a.set_title(
    "A  |  V-Dem Political Corruption Index (vdem_corr)\n"
    "0 = least corrupt  →  1 = most corrupt",
    fontsize=10.5, fontweight="bold", loc="left"
)

shade_gov(ax_a, label_y=0.235)
shade_netanyahu_only(ax_a, label_y=0.235)

yrs, vals = series("vdem_corr")
ax_a.plot(yrs, vals, "o-", color="#2c3e50", lw=2.2, ms=5, zorder=6, label="vdem_corr")
ax_a.fill_between(yrs, vals, alpha=0.12, color="#2c3e50")

# Annotate peak
pk_idx = np.argmax(vals)
ax_a.annotate(
    f"Peak: {vals[pk_idx]:.3f}\n({int(yrs[pk_idx])})",
    xy=(yrs[pk_idx], vals[pk_idx]),
    xytext=(yrs[pk_idx]-12, vals[pk_idx]+0.015),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.85, lw=0.5),
)

ax_a.set_ylabel("Corruption Index (0–1)", fontsize=10)
ax_a.set_ylim(0.07, 0.26)
ax_a.set_xlim(1946, 2026)
ax_a.set_xlabel("Year", fontsize=10)

# ── Panel B: V-Dem Executive Corruption ──────────────────────────────────
ax_b = fig.add_subplot(gs[0, 1])
ax_b.set_title(
    "B  |  V-Dem Executive Corruption (vdem_execorr)\n"
    "0 = least corrupt  →  1 = most corrupt",
    fontsize=10.5, fontweight="bold", loc="left"
)

shade_gov(ax_b, label_y=0.258)
shade_netanyahu_only(ax_b, label_y=0.258)

yrs_e, vals_e = series("vdem_execorr")
ax_b.plot(yrs_e, vals_e, "o-", color="#c0392b", lw=2.5, ms=5, zorder=6, label="vdem_execorr")
ax_b.fill_between(yrs_e, vals_e, alpha=0.12, color="#c0392b")

# Key annotations
ax_b.annotate(
    "Netanyahu I ends:\n0.142 (2000)",
    xy=(2000, 0.142), xytext=(1990, 0.165),
    fontsize=8, color="#555",
    arrowprops=dict(arrowstyle="->", color="#555", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8, lw=0),
)
ax_b.annotate(
    "Netanyahu indicted:\n0.240 (2019)",
    xy=(2019, 0.240), xytext=(2010, 0.248),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.85, lw=0.5),
)
ax_b.annotate(
    "Peak: 0.245\n(2022)",
    xy=(2022, 0.245), xytext=(2014, 0.255),
    fontsize=8, color="#8e1b0e",
    arrowprops=dict(arrowstyle="->", color="#8e1b0e", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.85, lw=0.5),
)

ax_b.set_ylabel("Executive Corruption (0–1)", fontsize=10)
ax_b.set_ylim(0.09, 0.28)
ax_b.set_xlim(1946, 2026)
ax_b.set_xlabel("Year", fontsize=10)

# ── Panel C: World Bank Control of Corruption ─────────────────────────────
ax_c = fig.add_subplot(gs[1, 0])
ax_c.set_title(
    "C  |  World Bank Control of Corruption (wbgi_cce)\n"
    "Higher = better governance (more control of corruption)",
    fontsize=10.5, fontweight="bold", loc="left"
)

shade_gov(ax_c, label_y=1.78, col="#1a6bb5")
shade_netanyahu_only(ax_c, label_y=1.78)

yrs_w, vals_w = series("wbgi_cce")
ax_c.plot(yrs_w, vals_w, "o-", color="#27ae60", lw=2.5, ms=6, zorder=6, label="wbgi_cce")
ax_c.fill_between(yrs_w, vals_w, alpha=0.12, color="#27ae60")

ax_c.annotate(
    "1996: 1.668\n(peak governance score)",
    xy=(1996, 1.668), xytext=(1998, 1.72),
    fontsize=8, color="#27ae60",
    arrowprops=dict(arrowstyle="->", color="#27ae60", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#e8f8f0", alpha=0.85, lw=0.5),
)
ax_c.annotate(
    "2009 onward:\nstabilises ~0.70–0.85\n(~50% drop from 1996)",
    xy=(2015, 0.850), xytext=(2003, 0.72),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.85, lw=0.5),
)

ax_c.set_ylabel("Control of Corruption Score", fontsize=10)
ax_c.set_ylim(0.5, 1.95)
ax_c.set_xlim(1993, 2026)
ax_c.set_xlabel("Year", fontsize=10)

# ── Panel D: ICRG Quality of Government ───────────────────────────────────
ax_d = fig.add_subplot(gs[1, 1])
ax_d.set_title(
    "D  |  ICRG Quality of Government (icrg_qog)\n"
    "Higher = better (composite: corruption + law & order + bureaucracy)",
    fontsize=10.5, fontweight="bold", loc="left"
)

shade_gov(ax_d, label_y=0.90, col="#1a6bb5")
shade_netanyahu_only(ax_d, label_y=0.90)

yrs_i, vals_i = series("icrg_qog")
ax_d.plot(yrs_i, vals_i, "o-", color="#8e44ad", lw=2.5, ms=6, zorder=6, label="icrg_qog")
ax_d.fill_between(yrs_i, vals_i, alpha=0.12, color="#8e44ad")

ax_d.annotate(
    f"Peak: {max(vals_i):.3f} (1996)",
    xy=(1996, max(vals_i)),
    xytext=(1990, 0.87),
    fontsize=8, color="#8e44ad",
    arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8, lw=0),
)
ax_d.annotate(
    f"2024: {vals_i[-1]:.3f}",
    xy=(int(yrs_i[-1]), vals_i[-1]),
    xytext=(2016, 0.73),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.8, lw=0),
)

ax_d.set_ylabel("ICRG QoG Score (0–1)", fontsize=10)
ax_d.set_ylim(0.5, 0.95)
ax_d.set_xlim(1982, 2026)
ax_d.set_xlabel("Year", fontsize=10)

# Shared legend
leg_els = [
    mpatches.Patch(color="#1a6bb5", alpha=0.25, label="Likud-led government"),
    mpatches.Patch(color="#c0392b", alpha=0.28, label="Netanyahu PM specifically"),
]
fig.legend(handles=leg_els, loc="lower center", ncol=2, fontsize=10,
           framealpha=0.85, bbox_to_anchor=(0.5, 0.001))

plt.savefig(f"{OUT}/fig12_qog_corruption_dashboard.png", bbox_inches="tight")
plt.close()
print("Saved fig12_qog_corruption_dashboard.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 13 — Executive corruption sub-components (bribery + embezzlement)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle(
    "Israel: V-Dem Executive Corruption Sub-Components\n"
    "Ordinal scale: higher = cleaner  |  Blue = Likud govts  |  Red = Netanyahu",
    fontsize=13, fontweight="bold"
)

SUBCOMP = [
    ("vdem_exbribe", "Executive Bribery\n(vdem_exbribe)", "#e67e22", axes[0]),
    ("vdem_exembez", "Executive Embezzlement\n(vdem_exembez)", "#8e44ad", axes[1]),
]

for varname, title, col_c, ax in SUBCOMP:
    yrs_s, vals_s = series(varname)
    if len(yrs_s) == 0:
        continue

    for s, e, lbl, alp in LIKUD_GOV:
        ax.axvspan(s, e, alpha=alp, color="#1a6bb5", zorder=0)
    for s, e in NETANYAHU:
        ax.axvspan(s, e, alpha=0.15, color="#c0392b", zorder=0)

    ax.plot(yrs_s, vals_s, "o-", color=col_c, lw=2.5, ms=6, zorder=6)
    ax.fill_between(yrs_s, vals_s, alpha=0.12, color=col_c)

    # Annotate trend
    first_v, last_v = vals_s[0], vals_s[-1]
    first_y, last_y = int(yrs_s[0]), int(yrs_s[-1])
    change = last_v - first_v
    direction = "▼ decline" if change < 0 else "▲ rise"
    ax.text(0.03, 0.05,
            f"{first_y}: {first_v:.2f}\n{last_y}: {last_v:.2f}\nChange: {change:+.2f} ({direction})",
            transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="#fffbe6", alpha=0.9, lw=0.5))

    min_idx = np.argmin(vals_s)
    ax.annotate(
        f"Low: {vals_s[min_idx]:.2f}\n({int(yrs_s[min_idx])})",
        xy=(yrs_s[min_idx], vals_s[min_idx]),
        xytext=(yrs_s[min_idx]-8, vals_s[min_idx]-0.1),
        fontsize=8, color="#c0392b",
        arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.85, lw=0.5),
    )

    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("V-Dem Ordinal Score (higher = cleaner)", fontsize=10)
    ax.set_xlim(1946, 2026)

plt.tight_layout()
plt.savefig(f"{OUT}/fig13_exec_corruption_subcomponents.png", bbox_inches="tight")
plt.close()
print("Saved fig13_exec_corruption_subcomponents.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 14 — Corruption + Populism on same timeline (the core synthesis)
# ═══════════════════════════════════════════════════════════════════════════
# Load V-Party Likud populism data
import csv

party_ts = defaultdict(list)
with open("V-Dem-CPD-Party-V2.csv", newline="", encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        if row["country_text_id"] == "ISR" and "Likud" in row["v2paenname"]:
            def sf(v):
                try: return float(v)
                except: return np.nan
            yr = sf(row["year"])
            if not np.isnan(yr):
                party_ts["likud_popul"].append((int(yr), sf(row["v2xpa_popul"])))
                party_ts["likud_anti"].append((int(yr), sf(row["v2xpa_antiplural"])))

likud_popul_yrs  = np.array([y for y, v in party_ts["likud_popul"] if not np.isnan(v)])
likud_popul_vals = np.array([v for y, v in party_ts["likud_popul"] if not np.isnan(v)])
likud_anti_yrs   = np.array([y for y, v in party_ts["likud_anti"]  if not np.isnan(v)])
likud_anti_vals  = np.array([v for y, v in party_ts["likud_anti"]  if not np.isnan(v)])

fig, ax1 = plt.subplots(figsize=(16, 7))
fig.suptitle(
    "Israel: The Corruption–Populism Nexus (1973–2024)\n"
    "V-Dem Executive Corruption (country-level) vs. Likud Populism & Anti-Pluralism (party-level)\n"
    "Blue shading = Likud-led govts  |  Red shading = Netanyahu specifically",
    fontsize=13, fontweight="bold",
)

for s, e, lbl, alp in LIKUD_GOV:
    ax1.axvspan(s, e, alpha=alp, color="#1a6bb5", zorder=0)
for s, e in NETANYAHU:
    ax1.axvspan(s, e, alpha=0.13, color="#c0392b", zorder=0)

# Left axis: country-level corruption (execorr)
col_corr = "#c0392b"
yrs_e, vals_e = series("vdem_execorr")
l1, = ax1.plot(yrs_e, vals_e, "o-", color=col_corr, lw=2.5, ms=6,
               label="Executive Corruption Index (country, left axis)", zorder=6)
ax1.set_ylabel("V-Dem Executive Corruption (0=clean, 1=corrupt)", color=col_corr, fontsize=10)
ax1.tick_params(axis="y", colors=col_corr)
ax1.set_ylim(0.08, 0.30)

# Right axis: Likud party-level populism
ax2 = ax1.twinx()
ax2.spines["right"].set_visible(True)
col_pop = "#1a6bb5"
col_anti = "#e67e22"

l2, = ax2.plot(likud_popul_yrs, likud_popul_vals, "s--", color=col_pop, lw=2.2, ms=7,
               label="Likud Populism Index (party, right axis)", zorder=7)
l3, = ax2.plot(likud_anti_yrs,  likud_anti_vals,  "^:", color=col_anti, lw=1.8, ms=6,
               label="Likud Anti-Pluralism (party, right axis)", zorder=7)
ax2.set_ylabel("V-Party Index (0–1)", color="#2c3e50", fontsize=10)
ax2.set_ylim(-0.05, 1.05)

ax1.set_xlabel("Year", fontsize=11)
ax1.set_xlim(1970, 2026)

# Annotations
ax1.annotate(
    "Netanyahu indicted (Nov 2019)\nExecutive corruption: 0.240",
    xy=(2019, 0.240), xytext=(2010, 0.275),
    fontsize=8.5, color=col_corr,
    arrowprops=dict(arrowstyle="->", color=col_corr, lw=1.0),
    bbox=dict(boxstyle="round,pad=0.3", fc="#ffeaea", alpha=0.9, lw=0.6),
)
ax2.annotate(
    "Likud populism: 0.743\n(2019 election)",
    xy=(2019, 0.743), xytext=(2012, 0.88),
    fontsize=8.5, color=col_pop,
    arrowprops=dict(arrowstyle="->", color=col_pop, lw=1.0),
    bbox=dict(boxstyle="round,pad=0.3", fc="#eaf2ff", alpha=0.9, lw=0.6),
)
ax1.annotate(
    "1996: WB Control of Corruption\nat historic high (1.67)",
    xy=(1996, 0.120), xytext=(1984, 0.148),
    fontsize=8, color="#27ae60",
    arrowprops=dict(arrowstyle="->", color="#27ae60", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.2", fc="#e8f8f0", alpha=0.85, lw=0),
)

lines = [l1, l2, l3]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="upper left", fontsize=9, framealpha=0.88)

plt.tight_layout()
plt.savefig(f"{OUT}/fig14_corruption_populism_synthesis.png", bbox_inches="tight")
plt.close()
print("Saved fig14_corruption_populism_synthesis.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 15 — Non-V-Dem corruption sources only
#             (World Bank, ICRG, Transparency International)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(3, 1, figsize=(15, 13), sharex=False)
fig.suptitle(
    "Israel: Political Corruption — Independent (Non-V-Dem) Sources\n"
    "World Bank  |  ICRG  |  Transparency International\n"
    "Blue shading = Likud-led governments  |  Red shading = Netanyahu",
    fontsize=13, fontweight="bold", y=0.99,
)

panels = [
    ("wbgi_cce", "World Bank Control of Corruption\n(wbgi_cce) — higher = better governance",
     "#27ae60", "Control of Corruption Estimate", (0.4, 2.0)),
    ("icrg_qog", "ICRG Quality of Government\n(icrg_qog) — composite: corruption + law & order + bureaucracy quality\nhigher = better",
     "#8e44ad", "ICRG QoG Score (0–1)", (0.45, 1.0)),
    ("ti_cpi",   "Transparency International CPI\n(ti_cpi) — higher = cleaner / less corrupt",
     "#e67e22", "TI CPI Score (0–100)", (50, 75)),
]

for ax, (varname, title, col_c, ylabel, ylim) in zip(axes, panels):
    yrs_s, vals_s = series(varname)
    if len(yrs_s) == 0:
        ax.set_title(f"{title} — NO DATA", fontsize=10)
        continue

    for s, e, lbl, alp in LIKUD_GOV:
        ax.axvspan(s, e, alpha=alp, color="#1a6bb5", zorder=0)
        if (s >= min(yrs_s) - 2) and (s <= max(yrs_s) + 2):
            ax.text((s+e)/2, ylim[1]*0.97, lbl, ha="center", va="top",
                    fontsize=6, color="#1a3a6b", alpha=0.85, style="italic")
    for s, e in NETANYAHU:
        ax.axvspan(s, e, alpha=0.15, color="#c0392b", zorder=0)

    ax.plot(yrs_s, vals_s, "o-", color=col_c, lw=2.5, ms=7, zorder=6)
    ax.fill_between(yrs_s, vals_s, alpha=0.12, color=col_c)

    # Trend line
    z = np.polyfit(yrs_s, vals_s, 1)
    p = np.poly1d(z)
    xx = np.linspace(min(yrs_s), max(yrs_s), 200)
    ax.plot(xx, p(xx), "--", color="#7f8c8d", lw=1.3, alpha=0.6,
            label=f"Trend (slope {z[0]:+.4f}/yr)")

    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left")
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_ylim(ylim)
    ax.set_xlim(min(yrs_s) - 2, 2026)
    ax.set_xlabel("Year", fontsize=10)
    ax.legend(fontsize=9, loc="lower left")

    # Annotate first and last
    ax.annotate(f"{int(yrs_s[0])}: {vals_s[0]:.2f}",
                xy=(yrs_s[0], vals_s[0]),
                xytext=(yrs_s[0]+1, vals_s[0] + (ylim[1]-ylim[0])*0.05),
                fontsize=8, color=col_c,
                arrowprops=dict(arrowstyle="->", color=col_c, lw=0.7))
    ax.annotate(f"{int(yrs_s[-1])}: {vals_s[-1]:.2f}",
                xy=(yrs_s[-1], vals_s[-1]),
                xytext=(yrs_s[-1]-8, vals_s[-1] + (ylim[1]-ylim[0])*0.05),
                fontsize=8, color=col_c,
                arrowprops=dict(arrowstyle="->", color=col_c, lw=0.7))

leg_els = [
    mpatches.Patch(color="#1a6bb5", alpha=0.25, label="Likud-led government"),
    mpatches.Patch(color="#c0392b", alpha=0.28, label="Netanyahu PM"),
]
fig.legend(handles=leg_els, loc="lower center", ncol=2, fontsize=10,
           framealpha=0.85, bbox_to_anchor=(0.5, 0.001))

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig(f"{OUT}/fig15_nonvdem_corruption.png", bbox_inches="tight")
plt.close()
print("Saved fig15_nonvdem_corruption.png")


# ═══════════════════════════════════════════════════════════════════════════
# PRINT SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════
print()
print("=" * 80)
print(f"{'Year':<6} {'vdem_corr':>10} {'vdem_execorr':>13} {'wbgi_cce':>10} {'icrg_qog':>10}")
print("=" * 80)

yrs_all  = series("vdem_corr")[0]
vc_dict  = dict(zip(*series("vdem_corr")))
ve_dict  = dict(zip(*series("vdem_execorr")))
wb_dict  = dict(zip(*series("wbgi_cce")))
iq_dict  = dict(zip(*series("icrg_qog")))

# PM labels
def pm(y):
    if   1977 <= y < 1984: return "Begin (Likud)"
    elif 1984 <= y < 1990: return "Nat. Unity"
    elif 1990 <= y < 1992: return "Shamir (Likud)"
    elif 1992 <= y < 1996: return "Rabin/Peres (Labour)"
    elif 1996 <= y < 1999: return "Netanyahu I"
    elif 1999 <= y < 2001: return "Barak (Labour)"
    elif 2001 <= y < 2006: return "Sharon"
    elif 2006 <= y < 2009: return "Olmert (Kadima)"
    elif y >= 2009:        return "Netanyahu II–VI"
    return ""

key_yrs = [1977,1984,1988,1992,1996,1999,2003,2006,2009,2013,2015,2019,2022,2024]
for y in key_yrs:
    vc = f"{vc_dict[y]:.3f}" if y in vc_dict else "  N/A"
    ve = f"{ve_dict[y]:.3f}" if y in ve_dict else "  N/A"
    wb = f"{wb_dict[y]:.3f}" if y in wb_dict else "  N/A"
    iq = f"{iq_dict[y]:.3f}" if y in iq_dict else "  N/A"
    print(f"{y:<6} {vc:>10} {ve:>13} {wb:>10} {iq:>10}   {pm(y)}")

print("=" * 80)
print(f"\nAll figures saved to: {OUT}/")
print("\nDirectionality reminder:")
print("  vdem_corr / vdem_execorr : 0 = LEAST corrupt, 1 = MOST corrupt  (higher = worse)")
print("  wbgi_cce / icrg_qog      : higher = BETTER governance            (higher = better)")
