#!/usr/bin/env python3
"""Generate SVG scatter plots of judge score vs total tokens from eval results."""

import json
import glob
import os

RAW_DIR = "/Users/hugopeck/conductor/workspaces/archeia/phoenix/evals/results/raw"
OUT_DIR = "/Users/hugopeck/conductor/workspaces/archeia/phoenix/evals/results/reports"

COLORS = {
    "ask_complex": "#2563eb",
    "plan_complex": "#7c3aed",
    "implement_simple": "#059669",
    "implement_moderate": "#d97706",
    "implement_complex": "#dc2626",
}

CANVAS_W, CANVAS_H = 720, 450
MARGIN = {"left": 60, "right": 20, "top": 30, "bottom": 50}
PLOT_W = CANVAS_W - MARGIN["left"] - MARGIN["right"]
PLOT_H = CANVAS_H - MARGIN["top"] - MARGIN["bottom"]


def load_data():
    """Load all trial-1.json files and return list of dicts."""
    rows = []
    for path in glob.glob(os.path.join(RAW_DIR, "*", "*", "*", "trial-1.json")):
        with open(path) as f:
            d = json.load(f)
        if d.get("status") != "completed":
            continue
        score = d.get("judge", {}).get("total_score")
        tokens = d.get("metrics", {}).get("total_tokens")
        if score is None or tokens is None:
            continue
        rows.append({
            "repo_id": d["repo_id"],
            "category": d["task"]["category"],
            "score": score,
            "tokens": tokens,
        })
    return rows


def make_svg(rows, title, out_path):
    """Generate an SVG scatter plot and write to out_path."""
    if not rows:
        return

    tokens_vals = [r["tokens"] for r in rows]
    score_vals = [r["score"] for r in rows]

    x_min, x_max = 0, max(tokens_vals) * 1.05
    y_min, y_max = 0, 100

    def sx(v):
        return MARGIN["left"] + (v - x_min) / (x_max - x_min) * PLOT_W

    def sy(v):
        return MARGIN["top"] + PLOT_H - (v - y_min) / (y_max - y_min) * PLOT_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}"'
        f' viewBox="0 0 {CANVAS_W} {CANVAS_H}" style="background:#fff">'
    )
    parts.append(
        '<style>'
        'text { font-family: system-ui, -apple-system, sans-serif; fill: #333; }'
        '.axis-label { font-size: 12px; }'
        '.tick-label { font-size: 10px; fill: #666; }'
        '.title { font-size: 14px; font-weight: 600; }'
        '.legend-text { font-size: 10px; }'
        '</style>'
    )

    # Title
    parts.append(
        f'<text x="{CANVAS_W / 2}" y="{MARGIN["top"] - 10}" text-anchor="middle" class="title">{title}</text>'
    )

    # Grid lines and tick labels — Y axis (score 0-100, step 20)
    for yv in range(0, 101, 20):
        y = sy(yv)
        parts.append(
            f'<line x1="{MARGIN["left"]}" y1="{y}" x2="{MARGIN["left"] + PLOT_W}" y2="{y}"'
            f' stroke="#e0e0e0" stroke-dasharray="4,3" />'
        )
        parts.append(
            f'<text x="{MARGIN["left"] - 8}" y="{y + 3}" text-anchor="end" class="tick-label">{yv}</text>'
        )

    # Grid lines and tick labels — X axis (tokens)
    nice_step = _nice_step(x_max)
    xv = 0
    while xv <= x_max:
        x = sx(xv)
        parts.append(
            f'<line x1="{x}" y1="{MARGIN["top"]}" x2="{x}" y2="{MARGIN["top"] + PLOT_H}"'
            f' stroke="#e0e0e0" stroke-dasharray="4,3" />'
        )
        label = f"{int(xv / 1000)}k" if xv >= 1000 else str(int(xv))
        parts.append(
            f'<text x="{x}" y="{MARGIN["top"] + PLOT_H + 16}" text-anchor="middle" class="tick-label">{label}</text>'
        )
        xv += nice_step

    # Axis borders
    parts.append(
        f'<rect x="{MARGIN["left"]}" y="{MARGIN["top"]}" width="{PLOT_W}" height="{PLOT_H}"'
        f' fill="none" stroke="#ccc" />'
    )

    # Axis labels
    parts.append(
        f'<text x="{MARGIN["left"] + PLOT_W / 2}" y="{CANVAS_H - 5}" text-anchor="middle" class="axis-label">Total Tokens</text>'
    )
    parts.append(
        f'<text x="14" y="{MARGIN["top"] + PLOT_H / 2}" text-anchor="middle"'
        f' transform="rotate(-90,14,{MARGIN["top"] + PLOT_H / 2})" class="axis-label">Judge Score</text>'
    )

    # Data points
    for r in rows:
        cx, cy = sx(r["tokens"]), sy(r["score"])
        col = COLORS.get(r["category"], "#999")
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{col}" opacity="0.7" />'
        )

    # Legend
    legend_x = MARGIN["left"] + PLOT_W - 155
    legend_y = MARGIN["top"] + 10
    parts.append(
        f'<rect x="{legend_x - 6}" y="{legend_y - 4}" width="160" height="{len(COLORS) * 18 + 8}"'
        f' fill="white" stroke="#ccc" rx="3" />'
    )
    for i, (cat, col) in enumerate(COLORS.items()):
        cy = legend_y + i * 18 + 10
        parts.append(f'<circle cx="{legend_x + 6}" cy="{cy}" r="5" fill="{col}" opacity="0.7" />')
        label = cat.replace("_", " ")
        parts.append(f'<text x="{legend_x + 18}" y="{cy + 4}" class="legend-text">{label}</text>')

    parts.append("</svg>")

    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {out_path}  ({len(rows)} points)")


def _nice_step(max_val):
    """Pick a nice round step for the x axis."""
    rough = max_val / 6
    mag = 10 ** int(len(str(int(rough))) - 1)
    for s in [1, 2, 5, 10, 20, 50]:
        step = s * mag
        if step >= rough:
            return step
    return mag * 10


if __name__ == "__main__":
    data = load_data()
    print(f"Loaded {len(data)} completed cells")

    # Plot 1: all repos
    make_svg(data, "Judge Score vs Total Tokens (All Repos)", os.path.join(OUT_DIR, "score-vs-tokens-all.svg"))

    # Plot 2: exclude arq
    filtered = [r for r in data if r["repo_id"] != "arq"]
    make_svg(filtered, "Judge Score vs Total Tokens (Excluding arq)", os.path.join(OUT_DIR, "score-vs-tokens-medium-large.svg"))
