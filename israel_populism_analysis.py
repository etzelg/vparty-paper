"""
Israel Populism & Anti-Pluralism Over-Time Analysis
====================================================
Using V-Party (V-Dem) Dataset V2 (1949-2019)

Focuses on Likud and other right-wing / religious-nationalist parties.
"""

import csv
import math
import os
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.lines import Line2D
from collections import defaultdict

# ── Output directory ────────────────────────────────────────────────────────
OUT = "israel_analysis_output"
os.makedirs(OUT, exist_ok=True)

# ── Load Israeli data ────────────────────────────────────────────────────────
DATA_FILE = "V-Dem-CPD-Party-V2.csv"

israel_rows = []
with open(DATA_FILE, newline="", encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        if row["country_text_id"] == "ISR":
            israel_rows.append(row)

def safe_float(val, default=np.nan):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# ── Party definitions & colour palette ──────────────────────────────────────
# Right-wing / nationalist / religious-nationalist parties of interest
FOCUS_PARTIES = {
    "Likud-National Liberal Movement": {
        "label": "Likud",
        "color": "#1a6bb5",        # Likud blue
        "lw": 3.0,
        "zorder": 10,
        "camp": "secular-right",
    },
    "Israel is Our Home": {
        "label": "Yisrael Beiteinu",
        "color": "#e05c00",
        "lw": 2.0,
        "zorder": 8,
        "camp": "secular-right",
    },
    "Jewish Home": {
        "label": "Jewish Home (HaBayit HaYehudi)",
        "color": "#c0392b",
        "lw": 2.0,
        "zorder": 8,
        "camp": "religious-right",
    },
    "National Union": {
        "label": "National Union",
        "color": "#8e44ad",
        "lw": 1.8,
        "zorder": 7,
        "camp": "religious-right",
    },
    "National Religious Party": {
        "label": "National Religious Party (Mafdal)",
        "color": "#d4880e",
        "lw": 1.8,
        "zorder": 7,
        "camp": "religious-right",
    },
    "Sephardi Torah Guardians": {
        "label": "Shas",
        "color": "#27ae60",
        "lw": 1.8,
        "zorder": 7,
        "camp": "ultra-orthodox",
    },
    "alliance: Yamina": {
        "label": "Yamina",
        "color": "#b03060",
        "lw": 1.8,
        "zorder": 7,
        "camp": "religious-right",
    },
    "New Right": {
        "label": "New Right (HaYamin HaHadash)",
        "color": "#e74c3c",
        "lw": 1.8,
        "zorder": 7,
        "camp": "secular-right",
    },
    # Left / centre for contrast
    "Alignment": {
        "label": "Alignment / Labour",
        "color": "#7f8c8d",
        "lw": 1.5,
        "zorder": 5,
        "camp": "left-centre",
    },
    "Blue and White": {
        "label": "Blue and White",
        "color": "#2980b9",
        "lw": 1.5,
        "zorder": 5,
        "camp": "left-centre",
    },
    "There is a Future": {
        "label": "Yesh Atid",
        "color": "#16a085",
        "lw": 1.5,
        "zorder": 5,
        "camp": "left-centre",
    },
    "Joint List": {
        "label": "Joint List",
        "color": "#636e72",
        "lw": 1.5,
        "zorder": 4,
        "camp": "left-centre",
    },
}

# ── Build per-party time series ──────────────────────────────────────────────
party_data = defaultdict(list)

for row in israel_rows:
    name = row["v2paenname"]
    year = safe_float(row["year"])
    popul = safe_float(row["v2xpa_popul"])
    popul_lo = safe_float(row["v2xpa_popul_codelow"])
    popul_hi = safe_float(row["v2xpa_popul_codehigh"])
    anti = safe_float(row["v2xpa_antiplural"])
    anti_lo = safe_float(row["v2xpa_antiplural_codelow"])
    anti_hi = safe_float(row["v2xpa_antiplural_codehigh"])
    vote = safe_float(row["v2pavote"])
    seats = safe_float(row["v2paseatshare"])

    if np.isnan(year):
        continue

    party_data[name].append({
        "year": int(year),
        "popul": popul,
        "popul_lo": popul_lo,
        "popul_hi": popul_hi,
        "anti": anti,
        "anti_lo": anti_lo,
        "anti_hi": anti_hi,
        "vote": vote,
        "seats": seats,
    })

# Sort by year
for name in party_data:
    party_data[name].sort(key=lambda r: r["year"])

# ── Helper ───────────────────────────────────────────────────────────────────
def ts(name, key):
    """Return (years[], values[]) for a given party and metric."""
    rows = party_data.get(name, [])
    yrs = [r["year"] for r in rows if not np.isnan(r[key])]
    vals = [r[key] for r in rows if not np.isnan(r[key])]
    return np.array(yrs), np.array(vals)

def ts_band(name, key_lo, key_hi):
    rows = party_data.get(name, [])
    yrs = [r["year"] for r in rows if not np.isnan(r[key_lo]) and not np.isnan(r[key_hi])]
    lo = [r[key_lo] for r in rows if not np.isnan(r[key_lo]) and not np.isnan(r[key_hi])]
    hi = [r[key_hi] for r in rows if not np.isnan(r[key_lo]) and not np.isnan(r[key_hi])]
    return np.array(yrs), np.array(lo), np.array(hi)

# ── Key Israeli election years ────────────────────────────────────────────────
ELECTIONS = [1949,1951,1955,1959,1961,1965,1969,1973,1977,1981,
             1984,1988,1992,1996,1999,2003,2006,2009,2013,2015,2019]

ANNOTATIONS = {
    1977: "Likud first\nelectoral victory",
    1996: "Netanyahu's first\nterm begins",
    2009: "Netanyahu returns\nto power",
    2015: "Likud surge\n(populist shift)",
    2019: "Political\ncrisis / 3 elections",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "figure.dpi": 150,
})

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Likud: Populism & Anti-Pluralism with confidence bands
# ════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
fig.suptitle(
    "Likud's Populism and Anti-Pluralism Trajectories, 1973–2019",
    fontsize=16, fontweight="bold", y=0.98
)

metrics = [
    ("popul", "popul_lo", "popul_hi", "V-Party Populism Index", "#1a6bb5", axes[0]),
    ("anti",  "anti_lo",  "anti_hi",  "V-Party Anti-Pluralism Index", "#c0392b", axes[1]),
]

for key, klo, khi, title, col, ax in metrics:
    yrs, vals = ts("Likud-National Liberal Movement", key)
    band_yrs, lo, hi = ts_band("Likud-National Liberal Movement", klo, khi)

    ax.fill_between(band_yrs, lo, hi, alpha=0.18, color=col, label="95% confidence interval")
    ax.plot(yrs, vals, "o-", color=col, lw=2.5, ms=7, label="Likud", zorder=10)

    # Election year gridlines
    for yr in ELECTIONS:
        ax.axvline(yr, color="#bdc3c7", lw=0.7, alpha=0.6)

    # Annotations
    for yr, txt in ANNOTATIONS.items():
        if yr in yrs:
            idx = list(yrs).index(yr)
            yval = vals[idx]
            ax.annotate(
                txt,
                xy=(yr, yval),
                xytext=(yr + 1, yval + 0.07),
                fontsize=7.5,
                color="#2c3e50",
                arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=0.8),
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, lw=0),
            )

    ax.set_ylabel(title, fontsize=11)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=9)

axes[1].set_xlabel("Election Year", fontsize=11)
axes[1].set_xlim(1970, 2021)

plt.tight_layout()
plt.savefig(f"{OUT}/fig1_likud_trajectory.png", bbox_inches="tight")
plt.close()
print("Saved fig1_likud_trajectory.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Right-wing bloc: Populism over time (multi-party)
# ════════════════════════════════════════════════════════════════════════════
RIGHT_PARTIES = [
    "Likud-National Liberal Movement",
    "Israel is Our Home",
    "Jewish Home",
    "National Union",
    "National Religious Party",
    "Sephardi Torah Guardians",
    "alliance: Yamina",
    "New Right",
]

fig, ax = plt.subplots(figsize=(14, 7))
ax.set_title(
    "Populism Index — Israeli Right-Wing Parties, 1949–2019\n"
    "(V-Party Populism Score; higher = more populist)",
    fontsize=14, fontweight="bold"
)

for pname in RIGHT_PARTIES:
    if pname not in party_data:
        continue
    cfg = FOCUS_PARTIES.get(pname, {"label": pname, "color": "grey", "lw": 1.5, "zorder": 5})
    yrs, vals = ts(pname, "popul")
    if len(yrs) == 0:
        continue
    ax.plot(
        yrs, vals,
        "o-",
        color=cfg["color"],
        lw=cfg["lw"],
        ms=6,
        label=cfg["label"],
        zorder=cfg.get("zorder", 5),
    )

for yr in ELECTIONS:
    ax.axvline(yr, color="#bdc3c7", lw=0.6, alpha=0.5)

ax.set_xlabel("Election Year", fontsize=11)
ax.set_ylabel("V-Party Populism Index (0–1)", fontsize=11)
ax.set_ylim(-0.05, 1.05)
ax.set_xlim(1948, 2021)
ax.legend(loc="upper left", fontsize=9, framealpha=0.85)

# Shade Netanyahu eras
ax.axvspan(1996, 1999, alpha=0.07, color="navy", label="Netanyahu PM (1st)")
ax.axvspan(2009, 2019, alpha=0.07, color="navy")
ax.text(1996.3, 0.97, "Netanyahu\nPM I", fontsize=7, color="navy", va="top")
ax.text(2009.3, 0.97, "Netanyahu PM II–IV", fontsize=7, color="navy", va="top")

plt.tight_layout()
plt.savefig(f"{OUT}/fig2_right_bloc_populism.png", bbox_inches="tight")
plt.close()
print("Saved fig2_right_bloc_populism.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Right-wing bloc: Anti-Pluralism over time
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 7))
ax.set_title(
    "Anti-Pluralism Index — Israeli Right-Wing Parties, 1949–2019\n"
    "(V-Party Anti-Pluralism Score; higher = more anti-pluralist)",
    fontsize=14, fontweight="bold"
)

for pname in RIGHT_PARTIES:
    if pname not in party_data:
        continue
    cfg = FOCUS_PARTIES.get(pname, {"label": pname, "color": "grey", "lw": 1.5, "zorder": 5})
    yrs, vals = ts(pname, "anti")
    if len(yrs) == 0:
        continue
    ax.plot(
        yrs, vals,
        "s--" if pname != "Likud-National Liberal Movement" else "o-",
        color=cfg["color"],
        lw=cfg["lw"],
        ms=6,
        label=cfg["label"],
        zorder=cfg.get("zorder", 5),
    )

for yr in ELECTIONS:
    ax.axvline(yr, color="#bdc3c7", lw=0.6, alpha=0.5)

ax.set_xlabel("Election Year", fontsize=11)
ax.set_ylabel("V-Party Anti-Pluralism Index (0–1)", fontsize=11)
ax.set_ylim(-0.02, 0.6)
ax.set_xlim(1948, 2021)
ax.legend(loc="upper left", fontsize=9, framealpha=0.85)

ax.axvspan(1996, 1999, alpha=0.07, color="navy")
ax.axvspan(2009, 2019, alpha=0.07, color="navy")
ax.text(1996.3, 0.57, "Netanyahu\nPM I", fontsize=7, color="navy", va="top")
ax.text(2009.3, 0.57, "Netanyahu PM II–IV", fontsize=7, color="navy", va="top")

plt.tight_layout()
plt.savefig(f"{OUT}/fig3_right_bloc_antipluralism.png", bbox_inches="tight")
plt.close()
print("Saved fig3_right_bloc_antipluralism.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Likud vs. Left/Centre: Side-by-side comparison
# ════════════════════════════════════════════════════════════════════════════
COMPARE = {
    "Right-Wing Bloc": {
        "parties": ["Likud-National Liberal Movement", "Israel is Our Home", "Jewish Home", "National Union"],
        "color": "#c0392b",
    },
    "Religious / Ultra-Orthodox": {
        "parties": ["National Religious Party", "Sephardi Torah Guardians"],
        "color": "#d4880e",
    },
    "Left / Centre Bloc": {
        "parties": ["Alignment", "Blue and White", "There is a Future"],
        "color": "#2980b9",
    },
}

fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=False)
fig.suptitle(
    "Israeli Political Blocs: Populism vs. Anti-Pluralism (1949–2019)\n"
    "Vote-share weighted bloc averages",
    fontsize=14, fontweight="bold"
)

METRICS = [
    ("popul", "Populism Index", axes[0]),
    ("anti",  "Anti-Pluralism Index", axes[1]),
]

for key, ylabel, ax in METRICS:
    for bloc_name, cfg in COMPARE.items():
        # Collect all party-year points in bloc, weighted by vote share
        by_year = defaultdict(list)
        for pname in cfg["parties"]:
            rows = party_data.get(pname, [])
            for r in rows:
                if not np.isnan(r[key]) and not np.isnan(r["vote"]):
                    by_year[r["year"]].append((r[key], r["vote"]))

        if not by_year:
            continue

        years_sorted = sorted(by_year.keys())
        wavg = []
        for yr in years_sorted:
            vals_w = by_year[yr]
            total_w = sum(w for _, w in vals_w)
            if total_w > 0:
                wav = sum(v * w for v, w in vals_w) / total_w
            else:
                wav = np.mean([v for v, _ in vals_w])
            wavg.append(wav)

        ax.plot(
            years_sorted, wavg,
            "o-",
            color=cfg["color"],
            lw=2.2,
            ms=6,
            label=bloc_name,
        )

    for yr in ELECTIONS:
        ax.axvline(yr, color="#bdc3c7", lw=0.6, alpha=0.5)

    ax.set_xlabel("Election Year", fontsize=11)
    ax.set_ylabel(f"V-Party {ylabel} (0–1)", fontsize=11)
    ax.set_xlim(1948, 2021)
    ax.legend(fontsize=9, framealpha=0.85)
    ax.set_title(ylabel, fontsize=12)

plt.tight_layout()
plt.savefig(f"{OUT}/fig4_bloc_comparison.png", bbox_inches="tight")
plt.close()
print("Saved fig4_bloc_comparison.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Likud: Populism × Vote Share (bubble chart)
# ════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle(
    "Likud: Electoral Performance vs. Populism & Anti-Pluralism",
    fontsize=14, fontweight="bold"
)

likud_rows = party_data["Likud-National Liberal Movement"]
years_l  = [r["year"] for r in likud_rows]
popul_l  = [r["popul"] for r in likud_rows]
anti_l   = [r["anti"]  for r in likud_rows]
vote_l   = [r["vote"]  for r in likud_rows]

# Normalise bubble size
max_vote = max(v for v in vote_l if not np.isnan(v))
sizes = [300 * (v / max_vote) ** 1.5 for v in vote_l]

cmap = plt.cm.plasma
norm = plt.Normalize(min(years_l), max(years_l))

for ax, (xvals, xlabel) in zip(
    axes,
    [
        (popul_l, "V-Party Populism Index"),
        (anti_l,  "V-Party Anti-Pluralism Index"),
    ]
):
    sc = ax.scatter(
        xvals,
        vote_l,
        s=sizes,
        c=years_l,
        cmap=cmap,
        norm=norm,
        edgecolors="#2c3e50",
        lw=0.8,
        alpha=0.85,
        zorder=5,
    )
    # Label each bubble with year
    for xv, yv, yr in zip(xvals, vote_l, years_l):
        if not (np.isnan(xv) or np.isnan(yv)):
            ax.annotate(str(yr), (xv, yv), fontsize=7.5, ha="center", va="bottom",
                        xytext=(0, 6), textcoords="offset points")
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel("Likud Vote Share (%)", fontsize=11)
    ax.set_ylim(5, 45)

plt.colorbar(sc, ax=axes[1], label="Election Year")
plt.tight_layout()
plt.savefig(f"{OUT}/fig5_likud_votes_vs_populism.png", bbox_inches="tight")
plt.close()
print("Saved fig5_likud_votes_vs_populism.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Comprehensive dashboard (4-panel)
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 13))
fig.suptitle(
    "Israel: Rise of Populism and Anti-Pluralism in Right-Wing Politics (1949–2019)\n"
    "V-Party Dataset | V-Dem Project",
    fontsize=16, fontweight="bold", y=0.99,
)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

# ── Panel A: Likud populism + anti-pluralism dual axis ──────────────────────
ax_a = fig.add_subplot(gs[0, 0])
ax_a.set_title("A  |  Likud: Dual-Index Trajectory", fontsize=12, fontweight="bold")

col_pop = "#1a6bb5"
col_anti = "#c0392b"

yrs_p, vals_p = ts("Likud-National Liberal Movement", "popul")
yrs_a, vals_a = ts("Likud-National Liberal Movement", "anti")

l1, = ax_a.plot(yrs_p, vals_p, "o-", color=col_pop, lw=2.2, ms=6, label="Populism")
ax_a2 = ax_a.twinx()
l2, = ax_a2.plot(yrs_a, vals_a, "s--", color=col_anti, lw=2.0, ms=5, label="Anti-Pluralism")
ax_a2.set_ylabel("Anti-Pluralism Index", color=col_anti, fontsize=9)
ax_a2.tick_params(axis="y", colors=col_anti)
ax_a2.spines["right"].set_visible(True)
ax_a2.set_ylim(0, 0.6)

ax_a.set_ylabel("Populism Index", color=col_pop, fontsize=9)
ax_a.tick_params(axis="y", colors=col_pop)
ax_a.set_ylim(-0.05, 1.05)
ax_a.set_xlim(1963, 2021)
ax_a.set_xlabel("Year")
ax_a.legend(handles=[l1, l2], loc="upper left", fontsize=8)

for yr in ELECTIONS:
    ax_a.axvline(yr, color="#bdc3c7", lw=0.5, alpha=0.5)

# ── Panel B: All right-wing parties — populism ──────────────────────────────
ax_b = fig.add_subplot(gs[0, 1])
ax_b.set_title("B  |  Right-Wing Parties: Populism Scores", fontsize=12, fontweight="bold")

for pname in RIGHT_PARTIES:
    cfg = FOCUS_PARTIES.get(pname, {"label": pname, "color": "grey", "lw": 1.2, "zorder": 4})
    yrs, vals = ts(pname, "popul")
    if len(yrs) == 0:
        continue
    ax_b.plot(yrs, vals, "o-", color=cfg["color"], lw=cfg["lw"], ms=5,
              label=cfg["label"], zorder=cfg.get("zorder", 4))

ax_b.set_ylim(-0.05, 1.05)
ax_b.set_xlim(1948, 2021)
ax_b.set_xlabel("Year")
ax_b.set_ylabel("Populism Index (0–1)")
ax_b.legend(fontsize=7.5, loc="upper left", framealpha=0.85)
for yr in ELECTIONS:
    ax_b.axvline(yr, color="#bdc3c7", lw=0.5, alpha=0.4)
ax_b.axvspan(2009, 2019, alpha=0.07, color="navy")

# ── Panel C: All right-wing parties — anti-pluralism ────────────────────────
ax_c = fig.add_subplot(gs[1, 0])
ax_c.set_title("C  |  Right-Wing Parties: Anti-Pluralism Scores", fontsize=12, fontweight="bold")

for pname in RIGHT_PARTIES:
    cfg = FOCUS_PARTIES.get(pname, {"label": pname, "color": "grey", "lw": 1.2, "zorder": 4})
    yrs, vals = ts(pname, "anti")
    if len(yrs) == 0:
        continue
    mk = "o-" if pname == "Likud-National Liberal Movement" else "s--"
    ax_c.plot(yrs, vals, mk, color=cfg["color"], lw=cfg["lw"], ms=5,
              label=cfg["label"], zorder=cfg.get("zorder", 4))

ax_c.set_ylim(-0.02, 0.65)
ax_c.set_xlim(1948, 2021)
ax_c.set_xlabel("Year")
ax_c.set_ylabel("Anti-Pluralism Index (0–1)")
ax_c.legend(fontsize=7.5, loc="upper left", framealpha=0.85)
for yr in ELECTIONS:
    ax_c.axvline(yr, color="#bdc3c7", lw=0.5, alpha=0.4)
ax_c.axvspan(2009, 2019, alpha=0.07, color="navy")

# ── Panel D: Vote share stacked — right bloc evolution ──────────────────────
ax_d = fig.add_subplot(gs[1, 1])
ax_d.set_title("D  |  Right-Wing Vote Share Evolution", fontsize=12, fontweight="bold")

RIGHT_VOTE_PARTIES = [
    ("Likud-National Liberal Movement", "#1a6bb5", "Likud"),
    ("Israel is Our Home",              "#e05c00", "Yisrael Beiteinu"),
    ("Jewish Home",                     "#c0392b", "Jewish Home"),
    ("National Union",                  "#8e44ad", "National Union"),
    ("National Religious Party",        "#d4880e", "Mafdal / NRP"),
    ("Sephardi Torah Guardians",        "#27ae60", "Shas"),
]

for pname, col, label in RIGHT_VOTE_PARTIES:
    yrs, vals = ts(pname, "vote")
    if len(yrs) == 0:
        continue
    ax_d.plot(yrs, vals, "o-", color=col, lw=1.8, ms=5, label=label)

ax_d.set_xlabel("Year")
ax_d.set_ylabel("Vote Share (%)")
ax_d.set_xlim(1948, 2021)
ax_d.legend(fontsize=7.5, loc="upper right", framealpha=0.85)
for yr in ELECTIONS:
    ax_d.axvline(yr, color="#bdc3c7", lw=0.5, alpha=0.4)

plt.savefig(f"{OUT}/fig6_dashboard.png", bbox_inches="tight")
plt.close()
print("Saved fig6_dashboard.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 7 — Heatmap: All Israeli parties × populism/anti-pluralism (latest)
# ════════════════════════════════════════════════════════════════════════════
# Use the most recent observation per party
all_parties_latest = {}
for pname, rows in party_data.items():
    latest = max(rows, key=lambda r: r["year"])
    all_parties_latest[pname] = latest

# Filter to parties with both scores
hm_data = [
    (pname, d["popul"], d["anti"], d["vote"], d["year"])
    for pname, d in all_parties_latest.items()
    if not np.isnan(d["popul"]) and not np.isnan(d["anti"])
]
hm_data.sort(key=lambda x: x[1], reverse=True)  # sort by populism

names_hm = [FOCUS_PARTIES[p]["label"] if p in FOCUS_PARTIES else p for p, *_ in hm_data]
popul_hm = np.array([x[1] for x in hm_data])
anti_hm  = np.array([x[2] for x in hm_data])
vote_hm  = np.array([x[3] for x in hm_data])
year_hm  = np.array([x[4] for x in hm_data])

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_title(
    "Israeli Parties: Populism vs. Anti-Pluralism\n(latest observation per party; bubble = vote share)",
    fontsize=13, fontweight="bold"
)

# Colour by camp
camp_colors = {
    "secular-right": "#1a6bb5",
    "religious-right": "#c0392b",
    "ultra-orthodox": "#27ae60",
    "left-centre": "#95a5a6",
}
colors_hm = []
for pname, *_ in hm_data:
    camp = FOCUS_PARTIES.get(pname, {}).get("camp", "left-centre")
    colors_hm.append(camp_colors[camp])

sizes_hm = [max(30, 400 * (v / 40) ** 1.5) if not np.isnan(v) else 40 for v in vote_hm]

sc = ax.scatter(popul_hm, anti_hm, s=sizes_hm, c=colors_hm,
                edgecolors="#2c3e50", lw=0.8, alpha=0.82, zorder=5)

for nm, xv, yv in zip(names_hm, popul_hm, anti_hm):
    ax.annotate(nm, (xv, yv), fontsize=7.2, ha="center", va="bottom",
                xytext=(0, 6), textcoords="offset points")

# Legend for camps
legend_els = [
    mpatches.Patch(color=camp_colors["secular-right"],   label="Secular Right"),
    mpatches.Patch(color=camp_colors["religious-right"],  label="Religious-Nationalist"),
    mpatches.Patch(color=camp_colors["ultra-orthodox"],   label="Ultra-Orthodox"),
    mpatches.Patch(color=camp_colors["left-centre"],      label="Left / Centre"),
]
ax.legend(handles=legend_els, loc="upper left", fontsize=9, title="Camp")

ax.set_xlabel("V-Party Populism Index (0 = not populist, 1 = highly populist)", fontsize=11)
ax.set_ylabel("V-Party Anti-Pluralism Index (0 = pluralist, 1 = anti-pluralist)", fontsize=11)
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.02, 0.65)

# Quadrant lines
ax.axvline(0.5, color="#e74c3c", lw=1, ls=":", alpha=0.6)
ax.axhline(0.15, color="#e74c3c", lw=1, ls=":", alpha=0.6)
ax.text(0.52, 0.62, "High Populism\n& Anti-Pluralism", fontsize=8, color="#c0392b", alpha=0.8)
ax.text(0.01, 0.62, "Low Populism\n& Anti-Pluralism", fontsize=8, color="#27ae60", alpha=0.8)

plt.tight_layout()
plt.savefig(f"{OUT}/fig7_scatter_latest.png", bbox_inches="tight")
plt.close()
print("Saved fig7_scatter_latest.png")


# ════════════════════════════════════════════════════════════════════════════
# PRINT SUMMARY TABLE
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print(f"{'PARTY':<42} {'YEARS':<12} {'POPUL 1st':>9} {'POPUL last':>10} {'ANTI 1st':>9} {'ANTI last':>9}")
print("=" * 85)

for pname in RIGHT_PARTIES + ["Alignment", "There is a Future", "Blue and White"]:
    rows = party_data.get(pname, [])
    if not rows:
        continue
    label = FOCUS_PARTIES.get(pname, {}).get("label", pname)
    first = rows[0]
    last  = rows[-1]
    p0 = f"{first['popul']:.3f}" if not np.isnan(first["popul"]) else "  N/A"
    p1 = f"{last['popul']:.3f}"  if not np.isnan(last["popul"])  else "  N/A"
    a0 = f"{first['anti']:.3f}"  if not np.isnan(first["anti"])  else "  N/A"
    a1 = f"{last['anti']:.3f}"   if not np.isnan(last["anti"])   else "  N/A"
    yr_range = f"{first['year']}–{last['year']}"
    print(f"{label:<42} {yr_range:<12} {p0:>9} {p1:>10} {a0:>9} {a1:>9}")

print("=" * 85)
print(f"\nAll figures saved to: {OUT}/")
