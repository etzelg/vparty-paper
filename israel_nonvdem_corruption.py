"""
Israel: Non-V-Dem Corruption Measures Against Netanyahu Periods
===============================================================
Two independent, corruption-specific (non-composite) sources:

  wbgi_cce   — World Bank Control of Corruption Estimate (1996–2024)
               Higher = better (less corrupt). Standard normal scale.

  ti_cpi     — Transparency International CPI, stitched series (1996–2024)
               Old methodology (ti_cpi_om, 0–10 scale, 1996–2011) rescaled
               to 0–100 and spliced with new methodology (ti_cpi, 2012–2024).
               Higher = cleaner / less corrupt.
"""

import openpyxl, os, warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

OUT = "israel_analysis_output"
os.makedirs(OUT, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────
wb_file = openpyxl.load_workbook("qog israel.xlsx", read_only=True)
ws = wb_file.active
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0])
yr_idx = header.index("year")

def series(name):
    i = header.index(name)
    pts = sorted(
        [(int(rows[j][yr_idx]), float(rows[j][i]))
         for j in range(1, len(rows)) if rows[j][i] is not None]
    )
    return np.array([y for y, v in pts]), np.array([v for y, v in pts])

# ── Stitch TI CPI ─────────────────────────────────────────────────────────
# Old methodology: 0–10 scale → rescale ×10 to 0–100
yrs_om, vals_om = series("ti_cpi_om")   # 1996–2011
yrs_new, vals_new = series("ti_cpi")    # 2012–2024
vals_om_rescaled = vals_om * 10

# Where the two series overlap (they don't here, but check):
# om ends 2011, new starts 2012 — clean join.
ti_yrs  = np.concatenate([yrs_om,  yrs_new])
ti_vals = np.concatenate([vals_om_rescaled, vals_new])

# Mark the splice point
splice_year = 2012

# World Bank
wb_yrs, wb_vals = series("wbgi_cce")

# ── Government periods ────────────────────────────────────────────────────
# Shading: all Likud/right-wing governments
ALL_GOV = [
    (1977, 1992, "Begin–Shamir era\n(1977–92)",    0.08, "#1a6bb5"),
    (1996, 1999, "Netanyahu I\n(1996–99)",          0.18, "#c0392b"),
    (2001, 2006, "Sharon\n(2001–06)",               0.08, "#1a6bb5"),
    (2009, 2024, "Netanyahu II–VI\n(2009–24)",      0.18, "#c0392b"),
]

# Netanyahu-only for annotation reference
NETANYAHU = [(1996, 1999, "Netanyahu I"), (2009, 2024, "Netanyahu II–VI")]

# Labour / Kadima periods for reference
LABOUR = [(1992, 1996), (1999, 2001), (2006, 2009)]

PM_LABELS = {
    1996: "Netanyahu I\ntakes office",
    1999: "Barak\n(Labour)",
    2001: "Sharon",
    2006: "Olmert\n(Kadima)",
    2009: "Netanyahu II\ntakes office",
    2021: "Bennett\n(brief)",
    2022: "Netanyahu\nreturns",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "figure.dpi": 150,
})

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 16 — Two-panel: TI CPI (top) + World Bank CCE (bottom)
# ═══════════════════════════════════════════════════════════════════════════
fig, (ax_ti, ax_wb) = plt.subplots(2, 1, figsize=(15, 11), sharex=True)
fig.suptitle(
    "Israel: Political Corruption — Two Independent Non-V-Dem Measures\n"
    "Red shading = Netanyahu governments  |  Blue = other right-wing/Likud governments",
    fontsize=14, fontweight="bold", y=0.99,
)

for ax, (yrs, vals, ylabel, ylim, col, title, note) in [
    (ax_ti, (ti_yrs, ti_vals,
             "TI CPI Score (0–100)\nhigher = cleaner",
             (54, 85),
             "#e67e22",
             "A  |  Transparency International CPI  (stitched 1996–2024)",
             "Old methodology (×10 rescaled) ——— New methodology")),
    (ax_wb, (wb_yrs, wb_vals,
             "WB Control of Corruption\n(standard normal; higher = less corrupt)",
             (0.5, 1.85),
             "#27ae60",
             "B  |  World Bank Control of Corruption Estimate  (1996–2024)",
             "Source: Worldwide Governance Indicators")),
]:
    # Government shading
    for s, e, lbl, alp, gcol in ALL_GOV:
        xs = max(s, int(yrs[0]))
        xe = min(e, 2025)
        if xs < xe:
            ax.axvspan(xs, xe, alpha=alp, color=gcol, zorder=0)

    # Labour periods — light grey
    for s, e in LABOUR:
        xs = max(s, int(yrs[0]))
        xe = min(e, 2025)
        if xs < xe:
            ax.axvspan(xs, xe, alpha=0.06, color="#7f8c8d", zorder=0)

    # Plot the series
    ax.plot(yrs, vals, "o-", color=col, lw=2.5, ms=7,
            zorder=6, clip_on=False)
    ax.fill_between(yrs, vals, ylim[0], alpha=0.10, color=col, zorder=1)

    # Trend line for Netanyahu II period
    mask = (yrs >= 2009) & (yrs <= 2024)
    if mask.sum() >= 2:
        z = np.polyfit(yrs[mask], vals[mask], 1)
        p = np.poly1d(z)
        xx = np.linspace(2009, 2024, 100)
        ax.plot(xx, p(xx), "--", color="#c0392b", lw=1.5, alpha=0.7,
                label=f"Netanyahu II–VI trend (slope {z[0]:+.3f}/yr)")

    # Trend line for Labour/pre-Netanyahu period (1996-2009 excluding Netanyahu I)
    mask2 = ((yrs >= 1999) & (yrs < 2001)) | ((yrs >= 2006) & (yrs < 2009))
    # Actually just show 1996-2009 full trend for context
    mask3 = (yrs >= 1996) & (yrs <= 2009)
    if mask3.sum() >= 2:
        z3 = np.polyfit(yrs[mask3], vals[mask3], 1)
        p3 = np.poly1d(z3)
        xx3 = np.linspace(1996, 2009, 100)
        ax.plot(xx3, p3(xx3), "--", color="#7f8c8d", lw=1.2, alpha=0.55,
                label=f"1996–2009 trend (slope {z3[0]:+.3f}/yr)")

    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_ylim(ylim)
    ax.legend(fontsize=8.5, loc="lower left", framealpha=0.85)
    ax.text(0.99, 0.04, note, transform=ax.transAxes, fontsize=7.5,
            ha="right", color="#7f8c8d", style="italic")

# ── TI-specific: mark splice + label key values ──────────────────────────
ax_ti.axvline(splice_year, color="#7f8c8d", lw=1.2, ls=":", alpha=0.8)
ax_ti.text(splice_year + 0.2, 83.5,
           "← Old (×10)    New →\nmethodology change",
           fontsize=7.5, color="#7f8c8d", va="top")

# Annotate Netanyahu I start (1996) — TI
ax_ti.annotate("1996: 77.1\n(Netanyahu I,\nhighest score)",
    xy=(1996, 77.1), xytext=(1997.5, 81),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.25", fc="#ffeaea", alpha=0.88, lw=0.5))

ax_ti.annotate("1998: 71.0\n(end of Netanyahu I)",
    xy=(1998, 71.0), xytext=(1999.5, 67),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.25", fc="#ffeaea", alpha=0.88, lw=0.5))

ax_ti.annotate("2006: 59.0\n(lowest pre-2009)",
    xy=(2006, 59.0), xytext=(2003, 57.5),
    fontsize=8, color="#7f8c8d",
    arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.85, lw=0.5))

ax_ti.annotate("2024: 64.0",
    xy=(2024, 64.0), xytext=(2020, 67.5),
    fontsize=8, color="#e67e22",
    arrowprops=dict(arrowstyle="->", color="#e67e22", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.85, lw=0.5))

# ── WB-specific: annotate key values ────────────────────────────────────
ax_wb.annotate("1996: 1.668\n(Netanyahu I,\nhighest ever)",
    xy=(1996, 1.668), xytext=(1998, 1.75),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.25", fc="#ffeaea", alpha=0.88, lw=0.5))

ax_wb.annotate("2009: 0.687\n(Netanyahu II starts;\nlowest recorded)",
    xy=(2009, 0.687), xytext=(2011, 0.58),
    fontsize=8, color="#c0392b",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.25", fc="#ffeaea", alpha=0.88, lw=0.5))

ax_wb.annotate("2016: 1.111\n(partial recovery)",
    xy=(2016, 1.111), xytext=(2017.5, 1.18),
    fontsize=8, color="#27ae60",
    arrowprops=dict(arrowstyle="->", color="#27ae60", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.25", fc="#e8f8f0", alpha=0.85, lw=0.5))

ax_wb.annotate("2024: 0.853",
    xy=(2024, 0.853), xytext=(2020, 0.72),
    fontsize=8, color="#27ae60",
    arrowprops=dict(arrowstyle="->", color="#27ae60", lw=0.8),
    bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.85, lw=0.5))

ax_wb.set_xlabel("Year", fontsize=11)
ax_wb.set_xlim(1994, 2026)

# Shared legend
leg_els = [
    mpatches.Patch(color="#c0392b", alpha=0.35, label="Netanyahu government"),
    mpatches.Patch(color="#1a6bb5", alpha=0.20, label="Other Likud/right-wing government"),
    mpatches.Patch(color="#7f8c8d", alpha=0.18, label="Labour / Kadima government"),
]
fig.legend(handles=leg_els, loc="lower center", ncol=3, fontsize=9.5,
           framealpha=0.88, bbox_to_anchor=(0.5, 0.0))

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig(f"{OUT}/fig16_nonvdem_corruption_stitched.png", bbox_inches="tight")
plt.close()
print("Saved fig16_nonvdem_corruption_stitched.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 17 — Single combined panel: both measures normalised to same scale
# ═══════════════════════════════════════════════════════════════════════════
# Normalise both to 0–1 so they can sit on the same axis
def norm01(arr):
    lo, hi = arr.min(), arr.max()
    return (arr - lo) / (hi - lo)

ti_norm = norm01(ti_vals)   # higher = cleaner
wb_norm = norm01(wb_vals)   # higher = cleaner

fig, ax = plt.subplots(figsize=(15, 7))
ax.set_title(
    "Israel: Corruption Deterioration — Normalised Comparison (1996–2024)\n"
    "Both measures scaled 0–1 (higher = cleaner / less corrupt)\n"
    "Red shading = Netanyahu governments",
    fontsize=13, fontweight="bold",
)

for s, e, lbl, alp, gcol in ALL_GOV:
    ax.axvspan(s, e, alpha=alp, color=gcol, zorder=0)
    ax.text((s+e)/2, 1.02, lbl, ha="center", va="bottom",
            fontsize=6.5, color="#1a3a6b" if gcol=="#1a6bb5" else "#7b0000",
            alpha=0.9, style="italic", clip_on=False)

for s, e in LABOUR:
    ax.axvspan(s, e, alpha=0.06, color="#7f8c8d", zorder=0)

ax.plot(ti_yrs, ti_norm, "o-", color="#e67e22", lw=2.4, ms=7,
        label="TI CPI (stitched, normalised)", zorder=6)
ax.plot(wb_yrs, wb_norm, "s-", color="#27ae60", lw=2.4, ms=7,
        label="World Bank Control of Corruption (normalised)", zorder=6)

# Shade between the two lines to show divergence / convergence
common_yrs = np.intersect1d(ti_yrs, wb_yrs)
ti_interp = np.interp(common_yrs, ti_yrs, ti_norm)
wb_interp = np.interp(common_yrs, wb_yrs, wb_norm)
ax.fill_between(common_yrs, ti_interp, wb_interp,
                alpha=0.10, color="#2c3e50", label="Gap between measures")

# Splice marker
ax.axvline(splice_year, color="#7f8c8d", lw=1.2, ls=":", alpha=0.7)
ax.text(splice_year + 0.15, 0.03, "TI methodology\nchange", fontsize=7.5,
        color="#7f8c8d", va="bottom")

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Normalised Score (0 = most corrupt observed,\n1 = least corrupt observed)", fontsize=10)
ax.set_ylim(-0.05, 1.12)
ax.set_xlim(1994, 2026)
ax.legend(loc="lower left", fontsize=9.5, framealpha=0.88)

# Netanyahu period mean annotations
for s, e, lbl in NETANYAHU:
    mask_t = (ti_yrs >= s) & (ti_yrs <= e)
    mask_w = (wb_yrs >= s) & (wb_yrs <= e)
    if mask_t.sum() > 0 and mask_w.sum() > 0:
        mid = (s + e) / 2
        avg_t = ti_norm[mask_t].mean()
        avg_w = wb_norm[mask_w].mean()
        ax.annotate(f"Mean:\nTI={avg_t:.2f}\nWB={avg_w:.2f}",
                    xy=(mid, min(avg_t, avg_w) - 0.07),
                    ha="center", fontsize=8, color="#7b0000",
                    bbox=dict(boxstyle="round,pad=0.3", fc="#ffeaea", alpha=0.85, lw=0.5))

plt.tight_layout()
plt.savefig(f"{OUT}/fig17_corruption_normalised_combined.png", bbox_inches="tight")
plt.close()
print("Saved fig17_corruption_normalised_combined.png")


# ── Print table ──────────────────────────────────────────────────────────
print()
print("=" * 72)
print(f"{'Year':<6} {'TI CPI (0-100)':>16} {'WB CCE':>10}  Government")
print("=" * 72)

ti_dict = dict(zip(ti_yrs.astype(int), ti_vals))
wb_dict = dict(zip(wb_yrs.astype(int), wb_vals))

def pm(y):
    if   1977 <= y < 1992: return "Likud (Begin/Shamir)"
    elif 1992 <= y < 1996: return "Labour (Rabin/Peres)"
    elif 1996 <= y < 1999: return "*** Netanyahu I ***"
    elif 1999 <= y < 2001: return "Labour (Barak)"
    elif 2001 <= y < 2006: return "Sharon"
    elif 2006 <= y < 2009: return "Kadima (Olmert)"
    elif 2009 <= y < 2021: return "*** Netanyahu II–IV ***"
    elif 2021 <= y < 2022: return "Bennett/Lapid"
    elif y >= 2022:        return "*** Netanyahu V–VI ***"
    return ""

all_yrs = sorted(set(list(ti_dict.keys()) + list(wb_dict.keys())))
for y in all_yrs:
    ti = f"{ti_dict[y]:.1f}" if y in ti_dict else "  N/A"
    # mark stitched values
    if y in ti_dict and y <= 2011:
        ti += " *"
    wb = f"{wb_dict[y]:.3f}" if y in wb_dict else "  N/A"
    print(f"{y:<6} {ti:>16} {wb:>10}  {pm(y)}")

print("=" * 72)
print("  * TI values 1996–2011 are from old methodology (0–10), rescaled ×10")
print(f"\nAll figures saved to: {OUT}/")
