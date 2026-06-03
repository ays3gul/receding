#!/usr/bin/env python3
"""
compare_results.py
==================
Reads result JSONs from RH-NBV and GradientNBV and produces:
  1. Burusa Table II-style comparison table (printed + saved as .txt)
  2. Coverage progression figure
  3. Trajectory distance figure
  4. Ray-tracing calls figure
  5. F1-score figure

Usage:
    python compare_results.py --rh   results_rh_nbv_easy.json \
                               --grad results_gradient_nbv_easy.json \
                               --out  results/comparison_easy

    # Or run without args to auto-detect JSONs in current directory:
    python compare_results.py
"""

import json
import argparse
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ---------------------------------------------------------------------------
# Styling — consistent with Burusa et al. paper aesthetic
# ---------------------------------------------------------------------------
STYLE = {
    "RH-NBV":      {"color": "#2196F3", "marker": "o", "ls": "-",  "lw": 2.0},
    "GradientNBV": {"color": "#F44336", "marker": "s", "ls": "--", "lw": 2.0},
}

plt.rcParams.update({
    "font.family":  "DejaVu Sans",
    "font.size":    11,
    "axes.grid":    True,
    "grid.alpha":   0.35,
    "figure.dpi":   150,
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load(path):
    with open(path) as f:
        return json.load(f)


def iter_axis(data):
    """0-based iteration indices matching the arrays in the JSON."""
    return list(range(len(data["coverages"])))


def pad_or_trim(arr, length):
    """Make array exactly `length` long (pad with last value or trim)."""
    arr = list(arr)
    if len(arr) < length:
        arr += [arr[-1]] * (length - len(arr))
    return arr[:length]


def pick_col_indices(n_iters, max_cols=7):
    """Pick evenly-spaced column indices for the summary table."""
    if n_iters <= 5:
        return list(range(n_iters + 1))
    step = n_iters // (max_cols - 1)
    cols = sorted(set([0] + list(range(step, n_iters, step)) + [n_iters]))
    return cols[:max_cols]


# ---------------------------------------------------------------------------
# Table printer
# ---------------------------------------------------------------------------

def print_comparison_table(rh, grad, out_prefix):
    occ    = rh.get("occlusion", "unknown")
    n      = max(rh["num_iters"], grad["num_iters"])
    cols   = pick_col_indices(n)

    col_w  = 13   # width per method column pair
    lbl_w  = 42
    n_cols = len(cols)
    sep    = "=" * (lbl_w + col_w * n_cols + 2)
    dash   = "-" * (lbl_w + col_w * n_cols + 2)

    def hdr():
        h = f"  {'# Viewpoints':<{lbl_w}}"
        for i in cols:
            h += f"{i:>{col_w}}"
        return h

    def row_float(label, rh_vals, grad_vals, fmt=".1f"):
        rh_v   = pad_or_trim(rh_vals,   n + 1)
        grad_v = pad_or_trim(grad_vals, n + 1)
        r = f"  {label:<{lbl_w}}"
        for i in cols:
            cell = f"{rh_v[i]:{col_w}{fmt}}"
            r += cell
        r += "\n"
        r += f"  {'':>{lbl_w}}"   # second line for GradientNBV
        for i in cols:
            cell = f"{grad_v[i]:{col_w}{fmt}}"
            r += cell
        return r

    def row_int(label, rh_vals, grad_vals):
        rh_v   = pad_or_trim(rh_vals,   n + 1)
        grad_v = pad_or_trim(grad_vals, n + 1)
        r = f"  {label:<{lbl_w}}"
        for i in cols:
            r += f"{int(rh_v[i]):{col_w}d}"
        r += "\n"
        r += f"  {'':>{lbl_w}}"
        for i in cols:
            r += f"{int(grad_v[i]):{col_w}d}"
        return r

    # --- build lines -------------------------------------------------------
    lines = []
    lines.append(sep)
    lines.append(f"  COMPARISON TABLE  |  Occlusion: {occ}  |  {n} iterations")
    lines.append(f"  Row 1 = RH-NBV  |  Row 2 = GradientNBV")
    lines.append(sep)
    lines.append(hdr())
    lines.append(dash)

    # Coverage
    lines.append(row_float(
        "ROI coverage (%) ↑",
        rh["coverages"],
        grad["coverages"],
    ))
    lines.append(dash)

    # F1
    rh_f1s   = [v * 100 for v in rh["f1_scores"]]
    grad_f1s = [v * 100 for v in grad["f1_scores"]]
    lines.append(row_float("F1-score 3D reconstruction (%) ↑", rh_f1s, grad_f1s))
    lines.append(dash)

    # Ray-tracing calls
    lines.append(row_int(
        "Ray-tracing calls (#) ↓",
        rh["ray_tracing_calls"],
        grad["ray_tracing_calls"],
    ))
    lines.append(dash)

    # Trajectory distance
    lines.append(row_float(
        "Trajectory distance (m) ↓",
        rh["distances"],
        grad["distances"],
        fmt=".3f",
    ))
    lines.append(dash)

    # Sigma (if available)
    rh_sigma   = rh.get("sigma_series")
    grad_sigma = grad.get("sigma_series")
    if rh_sigma and grad_sigma:
        rh_sig_cm   = [v * 100 for v in rh_sigma]
        grad_sig_cm = [v * 100 for v in grad_sigma]
        lines.append(row_float(
            "sigma 3D node pos (m×10⁻²) ↓",
            rh_sig_cm,
            grad_sig_cm,
            fmt=".2f",
        ))
        lines.append(dash)

    lines.append(sep)

    # --- summary block -----------------------------------------------------
    lines.append("")
    lines.append(f"  SUMMARY METRICS               {'RH-NBV':>12}  {'GradientNBV':>14}")
    lines.append(dash)

    def sumrow(label, rh_val, grad_val, fmt=".2f"):
        return (f"  {label:<30} {rh_val:>12{fmt}}  {grad_val:>14{fmt}}")

    lines.append(sumrow("Final ROI coverage (%)",
                        rh["final_coverage"], grad["final_coverage"]))
    lines.append(sumrow("Final F1-score (%)",
                        rh["final_f1"] * 100, grad["final_f1"] * 100))
    lines.append(sumrow("Final recall (%)",
                        rh["recalls"][-1] * 100, grad["recalls"][-1] * 100))
    lines.append(sumrow("Final precision (%)",
                        rh["precisions"][-1] * 100, grad["precisions"][-1] * 100))
    lines.append(sumrow("Coverage AUC",
                        rh["coverage_auc"], grad["coverage_auc"]))
    lines.append(sumrow("Total ray-tracing calls",
                        rh["total_ray_calls"], grad["total_ray_calls"], fmt=".0f"))
    lines.append(sumrow("Final trajectory dist (m)",
                        rh["final_distance"], grad["final_distance"]))
    lines.append(sumrow("Total computation time (s)",
                        rh["total_time"], grad["total_time"]))
    lines.append(sumrow("Coverage efficiency (%/m)",
                        rh["coverage_efficiency"], grad["coverage_efficiency"]))
    lines.append(sumrow("Stagnation count",
                        rh["stagnation_count"], grad["stagnation_count"], fmt=".0f"))

    if rh.get("hausdorff_distance") and grad.get("hausdorff_distance"):
        lines.append(sumrow("Hausdorff distance (m)",
                            rh["hausdorff_distance"], grad["hausdorff_distance"], fmt=".6f"))
        lines.append(sumrow("Chamfer distance (m)",
                            rh["chamfer_distance"], grad["chamfer_distance"], fmt=".6f"))

    lines.append(dash)

    table_str = "\n".join(lines)
    print(f"\n{table_str}\n")

    # Save txt
    txt_path = f"{out_prefix}_table.txt"
    with open(txt_path, "w") as f:
        f.write(table_str)
    print(f"  Table saved -> {txt_path}")


# ---------------------------------------------------------------------------
# Figure helpers
# ---------------------------------------------------------------------------

def _iters(data):
    return list(range(len(data["coverages"])))


def save_fig(fig, path):
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Figure saved -> {path}")


def plot_coverage(rh, grad, out_prefix, occ):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    iters_rh   = _iters(rh)
    iters_grad = _iters(grad)

    ax.plot(iters_rh,   rh["coverages"],   label="RH-NBV",      **STYLE["RH-NBV"])
    ax.plot(iters_grad, grad["coverages"], label="GradientNBV", **STYLE["GradientNBV"])

    ax.set_xlabel("# Viewpoints")
    ax.set_ylabel("ROI coverage (%)")
    ax.set_title(f"ROI Coverage Progression — {occ} occlusion")
    ax.legend()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    save_fig(fig, f"{out_prefix}_coverage.png")


def plot_f1(rh, grad, out_prefix, occ):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    rh_f1s   = [v * 100 for v in rh["f1_scores"]]
    grad_f1s = [v * 100 for v in grad["f1_scores"]]

    ax.plot(_iters(rh),   rh_f1s,   label="RH-NBV",      **STYLE["RH-NBV"])
    ax.plot(_iters(grad), grad_f1s, label="GradientNBV", **STYLE["GradientNBV"])

    ax.set_xlabel("# Viewpoints")
    ax.set_ylabel("F1-score (%)")
    ax.set_title(f"F1-score Progression — {occ} occlusion")
    ax.legend()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    save_fig(fig, f"{out_prefix}_f1.png")


def plot_trajectory(rh, grad, out_prefix, occ):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(_iters(rh),   rh["distances"],   label="RH-NBV",      **STYLE["RH-NBV"])
    ax.plot(_iters(grad), grad["distances"], label="GradientNBV", **STYLE["GradientNBV"])

    ax.set_xlabel("# Viewpoints")
    ax.set_ylabel("Cumulative trajectory distance (m)")
    ax.set_title(f"Trajectory Distance — {occ} occlusion")
    ax.legend()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    save_fig(fig, f"{out_prefix}_trajectory.png")


def plot_ray_calls(rh, grad, out_prefix, occ):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(_iters(rh),   rh["ray_tracing_calls"],   label="RH-NBV",      **STYLE["RH-NBV"])
    ax.plot(_iters(grad), grad["ray_tracing_calls"], label="GradientNBV", **STYLE["GradientNBV"])

    ax.set_xlabel("# Viewpoints")
    ax.set_ylabel("Cumulative ray-tracing calls (#)")
    ax.set_title(f"Ray-tracing Calls — {occ} occlusion")
    ax.legend()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    save_fig(fig, f"{out_prefix}_ray_calls.png")


def plot_4panel(rh, grad, out_prefix, occ):
    """Single figure with 4 subplots — thesis-ready."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(f"RH-NBV vs GradientNBV — {occ} occlusion", fontsize=13, fontweight="bold")

    rh_f1s   = [v * 100 for v in rh["f1_scores"]]
    grad_f1s = [v * 100 for v in grad["f1_scores"]]

    datasets = [
        (axes[0, 0], rh["coverages"],          grad["coverages"],          "ROI coverage (%)",                     "↑"),
        (axes[0, 1], rh_f1s,                   grad_f1s,                   "F1-score (%)",                         "↑"),
        (axes[1, 0], rh["distances"],           grad["distances"],          "Cumulative trajectory distance (m)",    "↓"),
        (axes[1, 1], rh["ray_tracing_calls"],   grad["ray_tracing_calls"], "Cumulative ray-tracing calls (#)",      "↓"),
    ]

    for ax, rh_data, grad_data, ylabel, arrow in datasets:
        ax.plot(_iters(rh),   rh_data,   label="RH-NBV",      **STYLE["RH-NBV"])
        ax.plot(_iters(grad), grad_data, label="GradientNBV", **STYLE["GradientNBV"])
        ax.set_xlabel("# Viewpoints")
        ax.set_ylabel(f"{ylabel} {arrow}")
        ax.legend(fontsize=9)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.tight_layout()
    save_fig(fig, f"{out_prefix}_4panel.png")


# ---------------------------------------------------------------------------
# Auto-detect JSON files
# ---------------------------------------------------------------------------

def auto_find(tag):
    """Find *rh_nbv* or *gradient* json in current dir."""
    for f in os.listdir("."):
        if f.endswith(".json") and tag in f.lower():
            return f
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rh",   default=None, help="RH-NBV result JSON")
    parser.add_argument("--grad", default=None, help="GradientNBV result JSON")
    parser.add_argument("--out",  default="results/comparison", help="Output prefix")
    args = parser.parse_args()

    rh_path   = args.rh   or auto_find("rh_nbv")
    grad_path = args.grad or auto_find("gradient")

    if not rh_path or not os.path.exists(rh_path):
        sys.exit(f"ERROR: RH-NBV JSON not found. Pass --rh <path>")
    if not grad_path or not os.path.exists(grad_path):
        sys.exit(f"ERROR: GradientNBV JSON not found. Pass --grad <path>")

    print(f"  RH-NBV JSON   : {rh_path}")
    print(f"  GradientNBV   : {grad_path}")

    rh   = load(rh_path)
    grad = load(grad_path)
    occ  = rh.get("occlusion", "unknown")

    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)

    print_comparison_table(rh, grad, args.out)
    plot_coverage(rh, grad, args.out, occ)
    plot_f1(rh, grad, args.out, occ)
    plot_trajectory(rh, grad, args.out, occ)
    plot_ray_calls(rh, grad, args.out, occ)
    plot_4panel(rh, grad, args.out, occ)

    print("\nDone. All outputs in:", os.path.dirname(args.out) or ".")
