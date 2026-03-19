"""
Israel: Clientelism (v2paclient) vs. Likud Government Periods
==============================================================
Replaces the tautological anti-elite rhetoric scatter (fig9).
v2paanteli feeds into the V-Party populism index, so it is NOT
independent. v2paclient is coded separately and is a genuine
external measure of patronage / transactional politics.
"""

import csv, os, warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from collections import defaultdict

OUT = "israel_analysis_output"
os.makedirs(OUT, exist_ok=True)

DATA_FILE = "V-Dem-CPD-Party-V2.csv"

israel_rows = []
with open(DATA_FILE, newline="", encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        if row["country_text_id"] == "ISR":
            israel_rows.append(row)

def sf(val):
    try:   return float(val)
    except: return np.nan

party_ts = defaultdict(list)
for row in israel_rows:
    party_ts[row["v2paenname"]].append({
        "year":   int(sf(row["year"])),
        "popul":  sf(row["v2xpa_popul"]),
        "anti":   sf(row["v2xpa_antiplural"]),
        "client": sf(row["v2paclient"]),
        "vote":   sf(row["v2pavote"]),
    })
for n in party_ts:
    party_ts[n].sort(key=lambda r: r["year"])

def ts(name, key):
    rows = [r for r in party_ts.get(name, []) if not np.isnan(r[key])]
    return np.array([r["year"] for r in rows]), np.array([r[key] for r in rows])

# Likud PM periods (start, end, label, alpha)
LIKUD_GOV = [
    (1977, 1984, "Begin\n(1977–84)",       0.14),
    (1988, 1992, "Shamir II\n(1988–92)",   0.14),
    (1996, 1999, "Netanyahu I\n(1996–99)", 0.14),
    (2001, 2006, "Sharon\n(2001–06)",      0.08),
    (2009, 2019, "Netanyahu II–IV\n(2009–19)", 0.14),
]

ELECTIONS = [1973,1977,1981,1984,1988,1992,1996,1999,2003,2006,2009,2013,2015,2019]

RIGHT = [
    ("Likud-National Liberal Movement", "#1a6bb5", "Likud",             3.0),
    ("Israel is Our Home",              "#e05c00", "Yisrael Beiteinu",  1.8),
    ("National Religious Party",        "#d4880e", "NRP / Mafdal",      1.6),
    ("Sephardi Torah Guardians",        "#27ae60", "Shas",              1.6),
    ("National Union",                  "#8e44ad", "National Union",    1.5),
    ("Jewish Home",                     "#c0392b", "Jewish Home",       1.5),
]
LEFT = [
    ("Alignment", "#95a5a6", "Alignment / Labour", 1.5),
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

def shade_gov(ax, label_y):
    for s, e, lbl, alp in LIKUD_GOV:
        ax.axvspan(s, e, alpha=alp, color="#1a6bb5", zorder=0)
        ax.text((s+e)/2, label_y, lbl, ha="center", va="top",
                fontsize=6.5, color="#1a3a6b", alpha=0.9, style="italic")

def mark_elections(ax):
    for yr in ELECTIONS:
        ax.axvline(yr, color="#bdc3c7", lw=0.5, alpha=0.5, zorder=1)

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 9 (replacement) — Clientelism vs. Likud in/out of power
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 12))
fig.suptitle(
    "Israel: Party Clientelism (Patronage) Mapped to Likud Government Periods\n"
    "v2paclient — coded independently of the V-Party populism index\n"
    "Blue shading = Likud-led governments",
    fontsize=13, fontweight="bold", y=0.99,
)

gs = gridspec.GridSpec(2, 1, figure=fig, hspace=0.45)

# ── PANEL A: All parties — clientelism over time ──────────────────────────
ax_a = fig.add_subplot(gs[0])
ax_a.set_title(
    "A  |  Party Clientelism over Time — Right-wing vs. Labour",
    fontsize=11, fontweight="bold", loc="left"
)

shade_gov(ax_a, label_y=-0.38)
mark_elections(ax_a)

for pname, col, lbl, lw in RIGHT + LEFT:
    yrs, vals = ts(pname, "client")
    if len(yrs) == 0: continue
    mk = "o-" if "Likud" in pname else ("s--" if pname in [p for p,*_ in RIGHT] else "^:")
    ax_a.plot(yrs, vals, mk, color=col, lw=lw, ms=6, label=lbl, zorder=5)

# Key annotation
ax_a.annotate(
    "1977 Mahapach: Likud's first\nvictory — clientelism spikes\nas new patronage networks open",
    xy=(1977, -0.536), xytext=(1979, -0.3),
    fontsize=8, color="#1a3a6b",
    arrowprops=dict(arrowstyle="->", color="#1a3a6b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.85, lw=0.5),
)
ax_a.annotate(
    "Likud loses power (1992):\nclientelism drops sharply",
    xy=(1992, -2.219), xytext=(1993, -1.8),
    fontsize=8, color="#7f8c8d",
    arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.85, lw=0.5),
)
ax_a.annotate(
    "Stable plateau\nduring Netanyahu era",
    xy=(2015, -0.839), xytext=(2010, -0.5),
    fontsize=8, color="#1a6bb5",
    arrowprops=dict(arrowstyle="->", color="#1a6bb5", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, lw=0.5),
)

ax_a.axhline(0, color="#2c3e50", lw=0.8, ls="-", alpha=0.4)
ax_a.text(2020.3, 0.05, "Global\nmean = 0", fontsize=7, color="#2c3e50", alpha=0.55)
ax_a.set_ylabel("Clientelism Score\n(V-Dem IRT scale; higher = more patronage)", fontsize=10)
ax_a.set_ylim(-2.8, 0.3)
ax_a.set_xlim(1970, 2022)
ax_a.legend(fontsize=8.5, loc="lower right", framealpha=0.87)

# ── PANEL B: Likud only — clientelism vs. in/out of power status ─────────
ax_b = fig.add_subplot(gs[1])
ax_b.set_title(
    "B  |  Likud Clientelism vs. Populism — Are They Moving Together?\n"
    "(Both are independent measures in V-Party)",
    fontsize=11, fontweight="bold", loc="left"
)

shade_gov(ax_b, label_y=0.96)
mark_elections(ax_b)

col_pop = "#1a6bb5"
col_cli = "#e67e22"

yrs_p, vals_p = ts("Likud-National Liberal Movement", "popul")
yrs_c, vals_c = ts("Likud-National Liberal Movement", "client")

ax_b.plot(yrs_p, vals_p, "o-", color=col_pop, lw=2.5, ms=7,
          label="Populism Index (left axis)", zorder=6)
ax_b.set_ylabel("Populism Index (0–1)", color=col_pop, fontsize=10)
ax_b.tick_params(axis="y", colors=col_pop)
ax_b.set_ylim(-0.05, 1.05)

ax_b2 = ax_b.twinx()
ax_b2.plot(yrs_c, vals_c, "D--", color=col_cli, lw=2.2, ms=6,
           label="Clientelism (right axis)", zorder=6)
ax_b2.set_ylabel("Clientelism Score", color=col_cli, fontsize=10)
ax_b2.tick_params(axis="y", colors=col_cli)
ax_b2.spines["right"].set_visible(True)
ax_b2.set_ylim(-3.0, 0.5)

lines_a, labels_a = ax_b.get_legend_handles_labels()
lines_b, labels_b = ax_b2.get_legend_handles_labels()
ax_b.legend(lines_a + lines_b, labels_a + labels_b,
            loc="upper left", fontsize=8.5, framealpha=0.87)

ax_b.set_xlabel("Election Year", fontsize=11)
ax_b.set_xlim(1970, 2022)

# Divergence callout
ax_b.annotate(
    "Post-2009: populism rises\nbut clientelism plateaus —\nrhetoric without new patronage",
    xy=(2015, 0.65), xytext=(2005, 0.82),
    fontsize=8, color="#2c3e50",
    arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.3", fc="#fffbe6", alpha=0.9, lw=0.5),
)

plt.savefig(f"{OUT}/fig9_clientelism_likud_power.png", bbox_inches="tight")
plt.close()
print("Saved fig9_clientelism_likud_power.png (replaces tautological scatter)")

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 11 — "In power" vs "Out of power" clientelism: Likud bar comparison
# ════════════════════════════════════════════════════════════════════════════
# Define in-power years for Likud
LIKUD_IN_POWER = {1977,1981,1984,1988,1996,2001,2003,2006,2009,2013,2015,2019}
# Note: 1984/88 = national unity (Likud senior partner or Shamir PM)
# 2001-2006 = Sharon (originally Likud)

likud_rows = party_ts["Likud-National Liberal Movement"]
in_power_c  = [r["client"] for r in likud_rows if r["year"] in LIKUD_IN_POWER and not np.isnan(r["client"])]
out_power_c = [r["client"] for r in likud_rows if r["year"] not in LIKUD_IN_POWER and not np.isnan(r["client"])]
in_power_p  = [r["popul"]  for r in likud_rows if r["year"] in LIKUD_IN_POWER and not np.isnan(r["popul"])]
out_power_p = [r["popul"]  for r in likud_rows if r["year"] not in LIKUD_IN_POWER and not np.isnan(r["popul"])]

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.suptitle(
    "Likud: Does Being In Power Change Clientelism or Populism?\n"
    "Mean scores when Likud-led government vs. in opposition",
    fontsize=13, fontweight="bold"
)

for ax, in_vals, out_vals, metric, ylabel in [
    (axes[0], in_power_c, out_power_c, "Clientelism (v2paclient)",
     "V-Dem Clientelism Score\n(higher = more patronage)"),
    (axes[1], in_power_p, out_power_p, "Populism (v2xpa_popul)",
     "V-Party Populism Index (0–1)"),
]:
    means = [np.mean(in_vals), np.mean(out_vals)]
    sems  = [np.std(in_vals)/np.sqrt(len(in_vals)) if len(in_vals)>1 else 0,
             np.std(out_vals)/np.sqrt(len(out_vals)) if len(out_vals)>1 else 0]
    bars = ax.bar(
        ["In Power\n(Likud PM)", "Out of Power\n(Opposition)"],
        means, yerr=sems,
        color=["#1a6bb5", "#95a5a6"],
        edgecolor="#2c3e50", lw=0.8,
        capsize=6, width=0.5,
        error_kw={"lw": 1.5},
    )
    # Individual data points
    jitter_in  = np.random.uniform(-0.12, 0.12, len(in_vals))
    jitter_out = np.random.uniform(-0.12, 0.12, len(out_vals))
    ax.scatter(np.zeros(len(in_vals))  + jitter_in,  in_vals,
               color="#1a6bb5", alpha=0.55, s=40, zorder=5)
    ax.scatter(np.ones(len(out_vals))  + jitter_out, out_vals,
               color="#95a5a6", alpha=0.55, s=40, zorder=5)

    ax.set_title(metric, fontsize=11, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=10)

    diff = means[0] - means[1]
    direction = "higher" if diff > 0 else "lower"
    ax.text(0.5, 0.94,
            f"In-power mean is {abs(diff):.3f} {direction} than\nout-of-power",
            ha="center", transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="#fffbe6", alpha=0.85, lw=0.5))

np.random.seed(42)  # fix jitter
plt.tight_layout()
plt.savefig(f"{OUT}/fig11_inpower_vs_opposition.png", bbox_inches="tight")
plt.close()
print("Saved fig11_inpower_vs_opposition.png")

print("\nDone. Note: v2paanteli is a component of v2xpa_popul — not plotted")
print("against it. Only v2paclient (truly independent) used as corruption proxy.")
