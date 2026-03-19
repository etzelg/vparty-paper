"""
Israel: Political Corruption Proxies Mapped to Likud Years in Power
====================================================================
V-Party dataset does not contain the main V-Dem country-level corruption
indices (v2x_corr, v2execorr). Instead we use the closest available
party-level proxies:

  v2paclient  – Party Clientelism  (higher = more patronage/rent-seeking)
  v2paanteli  – Anti-Elite Rhetoric (higher = stronger anti-establishment framing,
                 often co-varies with norm-breaking / corruption tolerance)

Both are plotted against shaded Likud-led government periods.
"""

import csv, math, os, warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from collections import defaultdict

OUT = "israel_analysis_output"
os.makedirs(OUT, exist_ok=True)

DATA_FILE = "V-Dem-CPD-Party-V2.csv"

# ── Load Israeli data ────────────────────────────────────────────────────────
israel_rows = []
with open(DATA_FILE, newline="", encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        if row["country_text_id"] == "ISR":
            israel_rows.append(row)

def sf(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return np.nan

# Build per-party time series
party_ts = defaultdict(list)
for row in israel_rows:
    name = row["v2paenname"]
    party_ts[name].append({
        "year":     int(sf(row["year"])),
        "popul":    sf(row["v2xpa_popul"]),
        "anti":     sf(row["v2xpa_antiplural"]),
        "client":   sf(row["v2paclient"]),       # clientelism (higher = more)
        "anteli":   sf(row["v2paanteli"]),        # anti-elite rhetoric
        "pariah":   sf(row["v2papariah"]),        # delegitimised out-groups
        "vote":     sf(row["v2pavote"]),
        "seats":    sf(row["v2paseatshare"]),
    })

for name in party_ts:
    party_ts[name].sort(key=lambda r: r["year"])

def ts(name, key):
    rows = [r for r in party_ts.get(name, []) if not np.isnan(r[key])]
    return np.array([r["year"] for r in rows]), np.array([r[key] for r in rows])

# ── Likud Government Periods ─────────────────────────────────────────────────
# (start, end, label, alpha)
LIKUD_GOV = [
    (1977, 1984, "Begin I & II\n(1977–84)",       0.12),
    (1988, 1992, "Shamir II\n(1988–92)",           0.12),
    (1996, 1999, "Netanyahu I\n(1996–99)",         0.12),
    (2001, 2006, "Sharon\n(2001–06)",              0.08),   # Sharon left for Kadima 2005
    (2009, 2019, "Netanyahu II–IV\n(2009–19)",     0.12),
]

ELECTIONS = [1949,1951,1955,1959,1961,1965,1969,1973,1977,1981,
             1984,1988,1992,1996,1999,2003,2006,2009,2013,2015,2019]

RIGHT_WING = [
    ("Likud-National Liberal Movement", "#1a6bb5", "Likud",              3.0),
    ("Israel is Our Home",              "#e05c00", "Yisrael Beiteinu",   1.8),
    ("Jewish Home",                     "#c0392b", "Jewish Home",        1.8),
    ("National Religious Party",        "#d4880e", "NRP / Mafdal",       1.6),
    ("Sephardi Torah Guardians",        "#27ae60", "Shas",               1.6),
    ("National Union",                  "#8e44ad", "National Union",     1.6),
]

LEFT_CENTRE = [
    ("Alignment",       "#95a5a6", "Alignment / Labour", 1.6),
    ("There is a Future","#2980b9","Yesh Atid",          1.6),
    ("Blue and White",  "#16a085", "Blue and White",     1.6),
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

def shade_gov(ax, ymin=None, ymax=None):
    """Shade Likud government periods."""
    for s, e, lbl, alp in LIKUD_GOV:
        ax.axvspan(s, e, alpha=alp, color="#1a6bb5", zorder=0)
        if ymax is not None:
            ax.text((s + e) / 2, ymax * 0.96, lbl,
                    ha="center", va="top", fontsize=6.5, color="#1a3a6b",
                    alpha=0.85, style="italic")

def mark_elections(ax):
    for yr in ELECTIONS:
        ax.axvline(yr, color="#bdc3c7", lw=0.5, alpha=0.5, zorder=1)

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 8 — Main corruption-proxy dashboard (3 panels)
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 14))
fig.suptitle(
    "Israel: Corruption-Linked Political Indicators Mapped to Likud Government Periods\n"
    "V-Party Dataset (V-Dem) | Blue shading = Likud-led governments",
    fontsize=14, fontweight="bold", y=0.99,
)

gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.45)

# ── PANEL A: Anti-Elite Rhetoric ─────────────────────────────────────────────
ax_a = fig.add_subplot(gs[0])
ax_a.set_title(
    "A  |  Anti-Elite Rhetoric  (v2paanteli)\n"
    "Higher = stronger 'establishment is corrupt / rigged against the people' framing",
    fontsize=11, fontweight="bold", loc="left"
)

shade_gov(ax_a, ymax=3.5)
mark_elections(ax_a)

for pname, col, lbl, lw in RIGHT_WING:
    yrs, vals = ts(pname, "anteli")
    if len(yrs) == 0: continue
    mk = "o-" if "Likud" in pname else "s--"
    ax_a.plot(yrs, vals, mk, color=col, lw=lw, ms=6, label=lbl, zorder=5)

for pname, col, lbl, lw in LEFT_CENTRE:
    yrs, vals = ts(pname, "anteli")
    if len(yrs) == 0: continue
    ax_a.plot(yrs, vals, "^:", color=col, lw=lw, ms=5, label=lbl, zorder=4, alpha=0.7)

# Netanyahu indictment annotation
ax_a.annotate(
    "Netanyahu\nindicted\n(Nov 2019)",
    xy=(2019, 3.156), xytext=(2014.5, 3.3),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.0),
    bbox=dict(boxstyle="round,pad=0.3", fc="#ffeaea", alpha=0.85, lw=0.5),
)
ax_a.annotate(
    "Likud first\nin power",
    xy=(1977, 0.44), xytext=(1978.5, 0.9),
    fontsize=7.5, color="#1a3a6b",
    arrowprops=dict(arrowstyle="->", color="#1a3a6b", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75, lw=0),
)

ax_a.set_ylabel("Anti-Elite Rhetoric Score", fontsize=10)
ax_a.set_ylim(-1.5, 3.7)
ax_a.set_xlim(1970, 2021)
ax_a.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.85)
ax_a.axhline(0, color="#2c3e50", lw=0.8, ls="-", alpha=0.4)
ax_a.text(2020.5, 0.05, "Global\nmean", fontsize=7, color="#2c3e50", alpha=0.6)

# ── PANEL B: Party Clientelism ────────────────────────────────────────────────
ax_b = fig.add_subplot(gs[1])
ax_b.set_title(
    "B  |  Party Clientelism  (v2paclient)\n"
    "Higher (less negative) = more patronage / exchange-based politics",
    fontsize=11, fontweight="bold", loc="left"
)

shade_gov(ax_b, ymax=-0.4)
mark_elections(ax_b)

for pname, col, lbl, lw in RIGHT_WING:
    yrs, vals = ts(pname, "client")
    if len(yrs) == 0: continue
    mk = "o-" if "Likud" in pname else "s--"
    ax_b.plot(yrs, vals, mk, color=col, lw=lw, ms=6, label=lbl, zorder=5)

for pname, col, lbl, lw in LEFT_CENTRE:
    yrs, vals = ts(pname, "client")
    if len(yrs) == 0: continue
    ax_b.plot(yrs, vals, "^:", color=col, lw=lw, ms=5, label=lbl, zorder=4, alpha=0.7)

ax_b.annotate(
    "Likud gains power;\nclientelism rises sharply\n(Mahapach 1977)",
    xy=(1977, -0.536), xytext=(1979, -0.65),
    fontsize=7.5, color="#1a3a6b",
    arrowprops=dict(arrowstyle="->", color="#1a3a6b", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, lw=0.5),
)

ax_b.set_ylabel("Clientelism Score (V-Dem IRT scale)", fontsize=10)
ax_b.set_ylim(-2.8, 0.3)
ax_b.set_xlim(1970, 2021)
ax_b.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.85)
ax_b.axhline(0, color="#2c3e50", lw=0.8, ls="-", alpha=0.4)
ax_b.text(2020.5, 0.05, "Global\nmean", fontsize=7, color="#2c3e50", alpha=0.6)

# ── PANEL C: Populism + Anti-pluralism (Likud only, with corruption framing)
ax_c = fig.add_subplot(gs[2])
ax_c.set_title(
    "C  |  Likud: Populism & Anti-Pluralism — The Full Picture\n"
    "Both indices accelerate during Netanyahu's 2009–2019 tenure (concurrent with corruption investigations)",
    fontsize=11, fontweight="bold", loc="left"
)

shade_gov(ax_c, ymax=0.9)
mark_elections(ax_c)

col_pop = "#1a6bb5"
col_anti = "#c0392b"

yrs_p, vals_p = ts("Likud-National Liberal Movement", "popul")
yrs_a, vals_a = ts("Likud-National Liberal Movement", "anti")

ax_c.plot(yrs_p, vals_p, "o-", color=col_pop, lw=2.5, ms=7, label="Populism Index", zorder=6)
ax_c.plot(yrs_a, vals_a, "s--", color=col_anti, lw=2.2, ms=6, label="Anti-Pluralism Index", zorder=6)

# Shade 95% CI for populism
from_ts_band = lambda name, klo, khi: (
    [r["year"] for r in party_ts[name] if not np.isnan(r[klo]) and not np.isnan(r[khi])],
    [r[klo] for r in party_ts[name] if not np.isnan(r[klo]) and not np.isnan(r[khi])],
    [r[khi] for r in party_ts[name] if not np.isnan(r[klo]) and not np.isnan(r[khi])],
)

# Load band data directly
band_rows = [r for r in israel_rows if "Likud" in r["v2paenname"]]
band_rows.sort(key=lambda r: int(sf(r["year"])))
b_yrs  = [int(sf(r["year"]))      for r in band_rows if sf(r["v2xpa_popul_codelow"]) == sf(r["v2xpa_popul_codelow"])]
b_lo   = [sf(r["v2xpa_popul_codelow"])  for r in band_rows if sf(r["v2xpa_popul_codelow"]) == sf(r["v2xpa_popul_codelow"])]
b_hi   = [sf(r["v2xpa_popul_codehigh"]) for r in band_rows if sf(r["v2xpa_popul_codelow"]) == sf(r["v2xpa_popul_codelow"])]

valid = [(y, l, h) for y, l, h in zip(b_yrs, b_lo, b_hi)
         if not np.isnan(l) and not np.isnan(h)]
if valid:
    vb_y, vb_lo, vb_hi = zip(*valid)
    ax_c.fill_between(vb_y, vb_lo, vb_hi, alpha=0.12, color=col_pop)

ax_c.annotate("2015:\nPopulism 0.65\nAnti-plural 0.16",
    xy=(2015, 0.65), xytext=(2011.5, 0.78),
    fontsize=7.5, color=col_pop,
    arrowprops=dict(arrowstyle="->", color=col_pop, lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8, lw=0))

ax_c.annotate("2019:\nPopulism 0.74\nAnti-plural 0.31",
    xy=(2019, 0.743), xytext=(2016.5, 0.88),
    fontsize=7.5, color="#8e1b0e",
    arrowprops=dict(arrowstyle="->", color="#8e1b0e", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.2", fc="#ffeaea", alpha=0.8, lw=0))

ax_c.set_ylabel("Index Score (0–1)", fontsize=10)
ax_c.set_ylim(-0.05, 1.0)
ax_c.set_xlim(1970, 2021)
ax_c.set_xlabel("Election Year", fontsize=11)
ax_c.legend(fontsize=9, loc="upper left", framealpha=0.85)

plt.savefig(f"{OUT}/fig8_corruption_proxy_likud_govts.png", bbox_inches="tight")
plt.close()
print("Saved fig8_corruption_proxy_likud_govts.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 9 — Anti-Elite Rhetoric vs. Populism scatter by election year (Likud)
# ════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle(
    "Likud: Corruption-Proxy Indicators vs. Populism & Anti-Pluralism",
    fontsize=14, fontweight="bold"
)

likud_rows_sorted = sorted(party_ts["Likud-National Liberal Movement"], key=lambda r: r["year"])
lkd_years  = [r["year"]   for r in likud_rows_sorted]
lkd_popul  = [r["popul"]  for r in likud_rows_sorted]
lkd_anti   = [r["anti"]   for r in likud_rows_sorted]
lkd_anteli = [r["anteli"] for r in likud_rows_sorted]
lkd_client = [r["client"] for r in likud_rows_sorted]

cmap = plt.cm.plasma
norm = plt.Normalize(min(lkd_years), max(lkd_years))

PAIRS = [
    (lkd_anteli, lkd_popul,  "Anti-Elite Rhetoric (v2paanteli)", "Populism Index",        axes[0]),
    (lkd_anteli, lkd_anti,   "Anti-Elite Rhetoric (v2paanteli)", "Anti-Pluralism Index",  axes[1]),
]

for xv, yv, xlabel, ylabel, ax in PAIRS:
    valid = [(x, y, yr) for x, y, yr in zip(xv, yv, lkd_years)
             if not np.isnan(x) and not np.isnan(y)]
    if not valid: continue
    xv2, yv2, yrs2 = zip(*valid)

    sc = ax.scatter(xv2, yv2, c=yrs2, cmap=cmap, norm=norm,
                    s=120, edgecolors="#2c3e50", lw=0.8, alpha=0.9, zorder=5)
    for x, y, yr in zip(xv2, yv2, yrs2):
        ax.annotate(str(yr), (x, y), fontsize=7.5, ha="center", va="bottom",
                    xytext=(0, 7), textcoords="offset points")

    # Trend line
    xarr, yarr = np.array(xv2), np.array(yv2)
    z = np.polyfit(xarr, yarr, 1)
    p = np.poly1d(z)
    xx = np.linspace(min(xarr), max(xarr), 100)
    ax.plot(xx, p(xx), "--", color="#7f8c8d", lw=1.2, alpha=0.6, label=f"Trend (r={np.corrcoef(xarr, yarr)[0,1]:.2f})")

    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(f"Likud {ylabel}", fontsize=10)
    ax.legend(fontsize=9)

plt.colorbar(sc, ax=axes[1], label="Election Year")
plt.tight_layout()
plt.savefig(f"{OUT}/fig9_antielite_vs_populism_scatter.png", bbox_inches="tight")
plt.close()
print("Saved fig9_antielite_vs_populism_scatter.png")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 10 — Composite index: "Illiberal Score" per party
#              = average(normalised populism, anti-pluralism, anti-elite rhetoric)
# ════════════════════════════════════════════════════════════════════════════

# Normalise anteli to 0-1 for all Israeli parties first
all_anteli = [r["anteli"] for rows in party_ts.values() for r in rows if not np.isnan(r["anteli"])]
ae_min, ae_max = min(all_anteli), max(all_anteli)

fig, ax = plt.subplots(figsize=(14, 6))
ax.set_title(
    "Composite 'Democratic Backsliding Risk' Score — Israeli Parties over Time\n"
    "Average of: Populism + Anti-Pluralism + Normalised Anti-Elite Rhetoric",
    fontsize=13, fontweight="bold"
)

shade_gov(ax, ymax=1.0)
mark_elections(ax)

ALL_FOCUS = RIGHT_WING + LEFT_CENTRE

for pname, col, lbl, lw in ALL_FOCUS:
    rows = [r for r in party_ts.get(pname, [])
            if not np.isnan(r["popul"]) and not np.isnan(r["anti"]) and not np.isnan(r["anteli"])]
    if not rows:
        continue
    years = [r["year"] for r in rows]
    # Normalise anteli to 0-1
    ae_norm = [(r["anteli"] - ae_min) / (ae_max - ae_min) for r in rows]
    composite = [(r["popul"] + r["anti"] + ae) / 3
                 for r, ae in zip(rows, ae_norm)]

    mk = "o-" if "Likud" in pname else ("s--" if pname in [p for p, *_ in RIGHT_WING] else "^:")
    lw_use = lw if "Likud" in pname else max(lw - 0.3, 1.2)
    ax.plot(years, composite, mk, color=col, lw=lw_use, ms=5, label=lbl, zorder=5 if "Likud" in pname else 4)

ax.set_xlabel("Election Year", fontsize=11)
ax.set_ylabel("Composite Backsliding Risk Score (0–1)", fontsize=11)
ax.set_ylim(-0.05, 1.05)
ax.set_xlim(1970, 2021)
ax.legend(fontsize=8.5, loc="upper left", ncol=2, framealpha=0.87)

plt.tight_layout()
plt.savefig(f"{OUT}/fig10_composite_backsliding.png", bbox_inches="tight")
plt.close()
print("Saved fig10_composite_backsliding.png")


# ════════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ════════════════════════════════════════════════════════════════════════════
print()
print("=" * 95)
print(f"{'PARTY':<38} {'YR':<5} {'POPUL':>6} {'ANTIPLU':>8} {'ANTIELI':>9} {'CLIENT':>9} {'VOTE%':>6}")
print("=" * 95)

KEY_PARTIES = [
    ("Likud-National Liberal Movement", "Likud"),
    ("Israel is Our Home",              "Yisrael Beiteinu"),
    ("Jewish Home",                     "Jewish Home"),
    ("National Religious Party",        "NRP/Mafdal"),
    ("Sephardi Torah Guardians",        "Shas"),
    ("National Union",                  "National Union"),
    ("Alignment",                       "Alignment/Labour"),
]

for pname, label in KEY_PARTIES:
    rows = party_ts.get(pname, [])
    if not rows:
        continue
    print(f"\n  {label}")
    for r in rows:
        p = f"{r['popul']:.3f}"  if not np.isnan(r["popul"])   else "  N/A"
        a = f"{r['anti']:.3f}"   if not np.isnan(r["anti"])    else "  N/A"
        ae= f"{r['anteli']:.3f}" if not np.isnan(r["anteli"])  else "  N/A"
        cl= f"{r['client']:.3f}" if not np.isnan(r["client"])  else "  N/A"
        v = f"{r['vote']:.1f}"   if not np.isnan(r["vote"])    else " N/A"
        print(f"  {'':36} {r['year']:<5} {p:>6} {a:>8} {ae:>9} {cl:>9} {v:>6}")

print("\n" + "=" * 95)
print(f"\nAll figures saved to: {OUT}/")
print("\nNOTE: The main V-Dem country-level corruption indices (v2x_corr, v2execorr)")
print("are NOT included in the V-Party dataset. The proxies used here are:")
print("  v2paclient  — party-level clientelism / patronage linkages")
print("  v2paanteli  — anti-elite rhetoric (strongly correlated with norm erosion)")
print("To add v2x_corr, merge the main V-Dem Country-Year dataset on (country, year).")
