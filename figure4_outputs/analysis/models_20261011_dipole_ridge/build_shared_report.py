#!/usr/bin/env python3
"""Publish readable descriptor definitions and fully expanded prediction equations."""
import csv
import html
import json
from pathlib import Path

import numpy as np

from descriptor_catalog import definitions_for

HERE = Path(__file__).resolve().parent
OUT = HERE / "shared_descriptor_search"
TARGETS = ("G_OH", "G_O", "G_OOH")
FAMILY_NAMES = {"ridge": "Linear ridge regression", "pls": "Partial least squares regression",
                "quadratic_ridge": "Additive quadratic ridge regression", "ols": "Ordinary least squares"}


def read(name):
    with (OUT / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def equation(target, model):
    name = {"G_OH": "OH", "G_O": "O", "G_OOH": "OOH"}[target]
    pieces = [f"{model['raw_intercept']:+.10g}"]
    for index, coefficient in enumerate(model["raw_linear_coefficients"], 1):
        pieces.append(f"{coefficient:+.10g}\\,x_{{{index}}}")
    if model["family"] == "quadratic_ridge":
        for index, coefficient in enumerate(model["raw_quadratic_coefficients"], 1):
            pieces.append(f"{coefficient:+.10g}\\,x_{{{index}}}^2")
    chunks = [" ".join(pieces[i:i + 4]) for i in range(0, len(pieces), 4)]
    return "$$\n\\begin{aligned}\n\\widehat G_{\\mathrm{" + name + "}}={}& " + chunks[0] + "\n" + "\n".join(
        "\\\\ & " + chunk for chunk in chunks[1:]) + "\n\\end{aligned}\n$$"


def plain_equation(target, model):
    pieces = [f"{model['raw_intercept']:+.10g}"]
    pieces += [f"{value:+.10g} * x{i}" for i, value in enumerate(model["raw_linear_coefficients"], 1)]
    if model["family"] == "quadratic_ridge":
        pieces += [f"{value:+.10g} * x{i}^2" for i, value in enumerate(model["raw_quadratic_coefficients"], 1)]
    return "```text\n" + target + "_predicted = " + pieces[0] + "\n" + "\n".join(
        "    " + " ".join(pieces[i:i + 3]) for i in range(1, len(pieces), 3)) + "\n```"


def scatter_svg(rows, target, kind):
    observed = np.asarray([float(r["observed_eV"]) for r in rows])
    predicted = np.asarray([float(r["predicted_eV"]) for r in rows])
    low = float(min(observed.min(), predicted.min()))
    high = float(max(observed.max(), predicted.max()))
    margin = max((high - low) * 0.07, 0.05)
    low -= margin; high += margin
    width, height, start, end = 760, 650, 85, 565

    def point(x, y):
        return start + (float(x) - low) / (high - low) * (end - start), end - (float(y) - low) / (high - low) * (end - start)

    content = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="325" y="35" text-anchor="middle" font-family="Arial" font-size="19">{target}: {kind}</text>',
        f'<line x1="{start}" y1="{end}" x2="{end}" y2="{start}" stroke="#666" stroke-dasharray="6 5"/>',
        f'<path d="M{start},{start} V{end} H{end}" fill="none" stroke="#222"/>']
    for tick in np.linspace(low, high, 6):
        px, py = point(tick, tick)
        content += [f'<text x="{px:.2f}" y="587" text-anchor="middle" font-family="Arial" font-size="12">{tick:.2f}</text>',
                    f'<text x="75" y="{py + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.2f}</text>']
    for row, x, y in zip(rows, observed, predicted):
        px, py = point(x, y)
        label = html.escape(f"{row['name']} {row['ads_site']}: observed={x:.6g}, predicted={y:.6g}")
        content.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3.8" fill="#1769aa" opacity="0.65"><title>{label}</title></circle>')
    errors = predicted - observed
    r2 = 1 - np.sum(errors ** 2) / np.sum((observed - observed.mean()) ** 2)
    rmse = np.sqrt(np.mean(errors ** 2))
    content += ['<text x="325" y="625" text-anchor="middle" font-family="Arial" font-size="15">Observed energy (eV)</text>',
        '<text x="20" y="325" transform="rotate(-90 20 325)" text-anchor="middle" font-family="Arial" font-size="15">Predicted energy (eV)</text>',
        f'<text x="325" y="62" text-anchor="middle" font-family="Arial" font-size="13">Pooled R2={r2:.3f}; RMSE={rmse:.3f} eV; {len(rows)} predictions</text>', '</svg>']
    return "\n".join(content)


def build_report():
    from build_current_report import build_report as publish_current
    publish_current()


if __name__ == "__main__":
    build_report()
