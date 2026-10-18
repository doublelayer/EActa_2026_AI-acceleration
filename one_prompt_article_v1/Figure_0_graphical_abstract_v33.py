"""Generate Figure 0."""

from __future__ import annotations

import os
from pathlib import Path
from contextlib import contextmanager
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from tempfile import TemporaryDirectory

# Some WSL Conda installations bundle a SQLite library older than the system
# ASE database module expects. Restart once with the system SQLite preloaded.
SYSTEM_SQLITE = "/lib/x86_64-linux-gnu/libsqlite3.so.0"
if ("LD_PRELOAD" not in os.environ and Path(SYSTEM_SQLITE).exists()
        and "miniconda" in sys.executable.lower()):
    environment = os.environ.copy()
    environment["LD_PRELOAD"] = SYSTEM_SQLITE
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).absolute().parent / ".matplotlib_cache"))
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import to_rgba
from matplotlib.patches import Polygon, Rectangle
import numpy as np
import pandas as pd
from PIL import Image
from ase.db import connect
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
from ase.io import write
from ase.io.pov import get_bondpairs


HERE = Path(__file__).absolute().parent
ROOT = HERE.parent
BASE = HERE / "Figure_0_graphical_abstract_v33"
WIDTH_CM, HEIGHT_CM, DPI = 13.28, 5.31, 600
INK = "#172B3A"
GREEN = "#50D050"
MUTED = "#60717C"
JMOL_COLORS = {
    "Cr": "#8A99C7", "Mn": "#9C7AC7", "Fe": "#E06633",
    "Co": "#F090A0", "Ni": "#50D050", "Cu": "#C88033",
}
FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
)
for _font in FONT_CANDIDATES:
    if _font.exists():
        font_manager.fontManager.addfont(str(_font))
FONT = "Liberation Sans" if all(p.exists() for p in FONT_CANDIDATES) else "DejaVu Sans"



DOUBLE_BOND_RADIUS = 0.06
DOUBLE_BOND_OFFSET = 0.11
SINGLE_BOND_RADIUS = 0.10
IMINE_MAX_LENGTH = 1.34
ATOM_LINE = re.compile(r"^atom\(<([^>]*)>.*?,\s*(\w+)\)")


@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def molecule_bonds(structure):
    """Use the Figure 1 ASE/Povray bond-pair convention; omit Co-Co bonds."""
    metals = {i for i, atom in enumerate(structure) if atom.symbol == "Co"}
    return sorted({tuple(sorted((int(a), int(b))))
                   for a, b, _ in get_bondpairs(structure, radius=1.0)
                   if a != b and not (a in metals and b in metals)})


def kekule_double_bonds(structure, bonds):
    doubles = {(a, b) for a, b in bonds
               if {structure[a].symbol, structure[b].symbol} == {"C", "N"}
               and structure.get_distance(a, b) < IMINE_MAX_LENGTH}
    used = {i for pair in doubles for i in pair}
    adjacency = {}
    for a, b in bonds:
        if structure[a].symbol == structure[b].symbol == "C":
            adjacency.setdefault(a, set()).add(b)
            adjacency.setdefault(b, set()).add(a)
    rings = {}

    def walk(path):
        if len(path) == 6:
            if path[0] in adjacency[path[-1]]:
                rings.setdefault(frozenset(path), tuple(path))
            return
        for neighbour in adjacency[path[-1]]:
            if neighbour not in path:
                walk(path + [neighbour])

    for start in adjacency:
        walk([start])
    for ring in rings.values():
        for first in (0, 1):
            option = [tuple(sorted((ring[i], ring[(i + 1) % 6])))
                      for i in range(first, 6, 2)]
            if not any(index in used for pair in option for index in pair):
                doubles.update(option)
                used.update(index for pair in option for index in pair)
                break
        else:
            raise ValueError(f"Could not assign aromatic bonds to ring {ring}.")
    return doubles


def add_bonds_to_pov(pov_path, colors, bonds, doubles):
    text = pov_path.read_text()
    positions, finish = [], None
    for line in text.splitlines():
        match = ATOM_LINE.match(line.strip())
        if match:
            positions.append([float(value) for value in match.group(1).split(",")])
            finish = match.group(2)
    if len(positions) != len(colors) or finish is None:
        raise ValueError("ASE POV-Ray atom coordinates could not be parsed.")
    positions = np.asarray(positions)
    _, _, axes = np.linalg.svd(positions - positions.mean(axis=0))
    plane_normal = axes[2]

    def cylinder(start, end, radius, color):
        return (f"cylinder {{<{start[0]:.4f},{start[1]:.4f},{start[2]:.4f}>, "
                f"<{end[0]:.4f},{end[1]:.4f},{end[2]:.4f}>, {radius:.4f} "
                f"texture {{pigment {{rgb <{color[0]:.3f},{color[1]:.3f},{color[2]:.3f}>}} "
                f"finish {{{finish}}}}}}}\n")

    lines = []
    for a, b in bonds:
        start, end = positions[a], positions[b]
        middle = (start + end) / 2
        if (a, b) in doubles:
            side = np.cross(end - start, plane_normal)
            side /= np.linalg.norm(side)
            side *= DOUBLE_BOND_OFFSET
            for offset in (side, -side):
                lines.append(cylinder(start + offset, middle + offset,
                                      DOUBLE_BOND_RADIUS, colors[a]))
                lines.append(cylinder(middle + offset, end + offset,
                                      DOUBLE_BOND_RADIUS, colors[b]))
        else:
            lines.append(cylinder(start, middle, SINGLE_BOND_RADIUS, colors[a]))
            lines.append(cylinder(middle, end, SINGLE_BOND_RADIUS, colors[b]))
    pov_path.write_text(text + "\n" + "".join(lines))


def render_povray_molecule(molecule):
    """Render the actual rotated ASE geometry with POV-Ray and project-style bonds."""
    if shutil.which("povray") is None:
        raise RuntimeError("POV-Ray is required for this graphical abstract but was not found.")
    structure = molecule.copy()
    structure.set_pbc(False)
    structure.center(vacuum=3.0)
    colors = jmol_colors[structure.numbers].copy()
    radii = covalent_radii[structure.numbers] * 0.42
    bonds = molecule_bonds(structure)
    doubles = kekule_double_bonds(structure, bonds)
    with TemporaryDirectory(prefix="ga_v8_pov_", dir=HERE) as temp_dir:
        temp = Path(temp_dir)
        with working_directory(temp):
            renderer = write(
                "catalyst.pov", structure, format="pov", rotation="0x,0y,0z",
                colors=colors, radii=radii, show_unit_cell=0,
                povray_settings={
                    "canvas_width": 1500, "transparent": True,
                    "camera_type": "orthographic", "bondatoms": [],
                    "area_light": [(2.0, 3.0, 40.0), "White", 0.7, 0.7, 3, 3],
                },
            )
            add_bonds_to_pov(temp / "catalyst.pov", colors, bonds, doubles)
            renderer.render()
        rendered = Image.open(temp / "catalyst.png").convert("RGBA")
        alpha = rendered.getchannel("A")
        bounds = alpha.getbbox()
        if bounds:
            rendered = rendered.crop(bounds)
        return rendered.copy()



def draw_volcano(fig, frame):
    # Preserve the square plot footprint used in Figure 3; integer ticks remain.
    ax = fig.add_axes([0.370, 0.13, 0.260, 0.65])
    x = frame["G_OH"].to_numpy()
    eta = frame["overpotential"].to_numpy()
    metals = frame["metal"].astype(str).to_numpy()
    for metal, color in JMOL_COLORS.items():
        selected = metals == metal
        if not selected.any():
            continue
        ax.scatter(x[selected], eta[selected], s=2.8, marker="D",
                   facecolors=[to_rgba(color, 0.42)],
                   edgecolors="none", linewidths=0,
                   rasterized=True, zorder=2)

    xmin, xmax = float(np.nanmin(x)), float(np.nanmax(x))
    pad = 0.08 * (xmax - xmin)
    xline = np.linspace(xmin - pad, xmax + pad, 350)
    # Reproduce the two volcano envelopes used in Figure 3 v15.
    fit_o = np.polyfit(frame["G_OH"], frame["G_O"], 1)
    fit_ooh = np.polyfit(frame["G_OH"], frame["G_OOH"], 1)
    y_o = np.polyval(fit_o, xline)
    y_ooh = np.polyval(fit_ooh, xline)
    steps = np.column_stack([4.92 - y_ooh, y_ooh - y_o, y_o - xline, xline])
    eta_fit = 1.23 - steps.min(axis=1)
    ideal_eta = 1.23 - np.minimum(xline, 4.92 - (xline + 2.46))
    ax.plot(xline, ideal_eta, color="#65717A", linewidth=0.8, linestyle=":", zorder=1)
    ax.plot(xline, eta_fit, color="#263B48", linewidth=0.8, zorder=1)
    ax.scatter([1.23], [0], marker="*", s=27, color="#D19A00",
               edgecolor="#6C5100", linewidth=0.8, zorder=4)
    ymax = max(float(np.nanmax(eta)), float(np.nanmax(eta_fit)), float(np.nanmax(ideal_eta)))
    top = np.ceil(ymax)
    ax.set_xlim(xline[0], xline[-1])
    ax.set_ylim(top, -0.11)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks(np.arange(0, top + 0.01, 1.0))
    ax.set_box_aspect(1)
    ax.set_xlabel("OH free energy / eV", fontsize=5.1, labelpad=1)
    ax.set_ylabel("overpotential / V", fontsize=5.1, labelpad=1)
    ax.tick_params(labelsize=5, length=2, width=0.8, pad=1)
    for spine in ax.spines.values():
        spine.set_color("#26343C")
        spine.set_linewidth(0.8)
    ax.grid(False)
    ax.set_facecolor("white")
    return ax




def complete_structure(kind):
    """Keep the optimized Co–Co/O-bridge/B1 adsorbate with every hydrogen."""
    database = ROOT / f"databases/3d_B1B2_ch2_{kind}_rpbe_d4.db"
    suffix = "OOH" if kind == "OOHz" else kind
    name = f"KMC_Co_Co_A2_B1_NNNNOO_q2_{suffix}_metal1"
    with connect(database) as db:
        rows = list(db.select(name=name))
    if len(rows) != 1:
        raise ValueError(f"Expected one optimized {kind} structure; found {len(rows)}")
    row = rows[0]
    if any(row.get(k) != v for k, v in
           {"metal1": "Co", "metal2": "Co", "base": "B1", "bridge": "OO"}.items()):
        raise ValueError("The selected structure is not Co–Co/O-bridge/B1.")
    atoms = row.toatoms()
    expected = ["O", "H"] if kind == "OH" else ["O", "O", "H"]
    if atoms.get_chemical_symbols()[-len(expected):] != expected:
        raise ValueError("The selected adsorbate atom sequence is unexpected.")
    atoms.center()
    atoms.rotate(228, "x", rotate_cell=True)
    atoms.rotate(215.264, "y", rotate_cell=True)
    atoms.rotate(30, "z", rotate_cell=True)
    return atoms


def prediction_data():
    """Load catalyst roles and ML predictions from the workspace input CSV."""
    database_path = ROOT / "DASC_Bare_Catalysts_RPBE_D4.db"
    predictions_path = ROOT / "figure4" / "predictions.csv"
    predictions = pd.read_csv(predictions_path)
    payload = predictions_path.read_bytes()

    roles = []
    with connect(str(database_path.resolve())) as database:
        for row in database.select():
            roles.append({
                "name": row.name,
                "O_model_role": row.get("O_model_role"),
                "OH_model_role": row.get("OH_model_role"),
                "OOH_model_role": row.get("OOH_model_role"),
            })
    roles = pd.DataFrame(roles)
    prediction_names = set(roles.loc[
        roles[["O_model_role", "OH_model_role", "OOH_model_role"]]
        .eq("prediction").all(axis=1), "name"
    ])

    keys = ["name", "ads_site"]
    if predictions.duplicated(keys + ["target"]).any():
        raise ValueError("Duplicate prediction rows were found in the supplied table.")
    predictions["predicted_eV"] = pd.to_numeric(predictions["predicted_eV"], errors="raise")
    frame = predictions.pivot(index=keys, columns="target", values="predicted_eV").reset_index()
    if frame[["G_OH", "G_O", "G_OOH"]].isna().any().any():
        raise ValueError("Each catalyst center must have O, OH, and OOH predictions.")
    if set(frame["name"]) != prediction_names:
        raise ValueError("Prediction-table names differ from the ASE database model roles.")

    parts = frame["name"].str.split("_", expand=True)
    frame["metal1"], frame["metal2"] = parts[1], parts[2]
    frame["metal"] = np.where(frame["ads_site"].eq("metal1"), frame["metal1"], frame["metal2"])
    frame["retained"] = frame["G_OH"].ge(0.00) & frame["G_O"].le(4.92)
    for species, correction in {"OH": 0.05, "O": 0.05, "OOH": 0.10}.items():
        frame[f"G_{species}"] = frame[f"G_{species}"] + correction
    steps = np.column_stack([
        4.92 - frame["G_OOH"],
        frame["G_OOH"] - frame["G_O"],
        frame["G_O"] - frame["G_OH"],
        frame["G_OH"],
    ])
    frame["overpotential"] = 1.23 - steps.min(axis=1)
    data = frame.loc[frame["retained"]].copy()
    provenance = {
        "prediction_source": str(predictions_path.relative_to(ROOT)),
        "predictions_sha256": hashlib.sha256(payload).hexdigest(),
        "retained_points": int(len(data)),
        "retained_structures": int(data["name"].nunique()),
    }
    (HERE / "Figure_0_graphical_abstract_v33_provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(provenance))
    return data


def draw_labels(stage):
    for x, action, count in ((2.0, "DFT calculations", "88 catalysts"),
                             (6.64, "ML screening", "1,260 catalysts"),
                             (11.27, "LLM writing", "1 article")):
        stage.text(x, 4.89, action, ha="center", va="center", fontsize=9.1,
                   fontweight="bold", color=INK, fontfamily=FONT)
        count_y = 4.42 if count == "1 article" else 4.53
        stage.text(x, count_y, count, ha="center", va="center", fontsize=8.0,
                   color=GREEN, fontfamily=FONT)


def make_figure():
    from matplotlib.patches import Rectangle
    figure = plt.figure(figsize=(WIDTH_CM / 2.54, HEIGHT_CM / 2.54),
                        dpi=DPI, facecolor="white")
    stage = figure.add_axes([0, 0, 1, 1], facecolor="white")
    stage.set_xlim(0, WIDTH_CM)
    stage.set_ylim(0, HEIGHT_CM)
    stage.axis("off")
    draw_labels(stage)

    # Natural proportions and common centerlines for all three visual stages.
    molecule_left = 2.0 / WIDTH_CM - 0.265 / 2
    for kind, bottom in (("OH", 0.495), ("OOHz", 0.155)):
        image = render_povray_molecule(complete_structure(kind))
        axis = figure.add_axes([molecule_left, bottom, 0.265, 0.300])
        axis.imshow(image, interpolation="lanczos")
        # Use a common molecular scale for both structures.
        old_width = 1428 if kind == "OH" else 1430
        axis.images[0].set_extent((-0.5, old_width - 0.5, 1039.5, -0.5))
        axis.set_xlim(-0.5, old_width - 0.5)
        axis.set_ylim(1039.5, -0.5)
        axis.set_aspect("equal")
        axis.axis("off")

    volcano = draw_volcano(figure, prediction_data())
    volcano.set_position([0.4095, 0.155, 0.181, 0.640])
    volcano.set_box_aspect(1.414)
    volcano.grid(False)
    for line in volcano.lines:
        line.set_linewidth(0.8)
    for spine in volcano.spines.values():
        spine.set_linewidth(0.8)

    page_path = HERE / "reference_EActa_open_article_2020_page1.png"
    page = Image.open(page_path).convert("RGB")
    border_width, border_height, bottom = 0.181, 0.640, 0.155
    left = 11.27 / WIDTH_CM - border_width / 2
    stage.add_patch(Rectangle((left * WIDTH_CM, bottom * HEIGHT_CM),
                              border_width * WIDTH_CM, border_height * HEIGHT_CM,
                              facecolor="white", edgecolor="#56636B",
                              linewidth=0.8, zorder=5))
    inner_width = border_width - 0.010
    inner_height = inner_width * WIDTH_CM / HEIGHT_CM / (page.width / page.height)
    page_axis = figure.add_axes([left + (border_width-inner_width)/2,
                                 bottom + (border_height-inner_height)/2,
                                 inner_width, inner_height], zorder=6)
    page_axis.imshow(page, interpolation="lanczos")
    page_axis.set_aspect("equal")
    page_axis.axis("off")
    # Match arrow, plot-frame, and page-border line widths.
    for x in (4.235, 9.02):
        y = 2.52
        shaft_half_height = 0.075
        head_half_height = 0.19
        half_length = 0.34
        head_length = 0.20
        shoulder = x + half_length - head_length
        arrow = Polygon(
            [(x - half_length, y - shaft_half_height),
             (shoulder, y - shaft_half_height),
             (shoulder, y - head_half_height),
             (x + half_length, y),
             (shoulder, y + head_half_height),
             (shoulder, y + shaft_half_height),
             (x - half_length, y + shaft_half_height)],
            closed=True, facecolor=to_rgba(GREEN, 0.5), edgecolor=GREEN,
            linewidth=0.8, joinstyle="round", zorder=4,
        )
        stage.add_patch(arrow)
    return figure


def main():
    outputs = [BASE.with_suffix(ext) for ext in (".svg", ".pdf", ".png", ".tif")]
    preview = HERE / "Figure_0_graphical_abstract_v33_preview.png"
    if any(path.exists() for path in outputs + [preview]):
        raise FileExistsError("TOC v33 output already exists; increment the version.")
    figure = make_figure()
    for ext in (".svg", ".pdf", ".png"):
        figure.savefig(BASE.with_suffix(ext), dpi=DPI, facecolor="white")
    rgb = Image.open(BASE.with_suffix(".png")).convert("RGB")
    if rgb.size != (3137, 1254):
        raise ValueError(f"Unexpected image dimensions: {rgb.size}")
    rgb.save(BASE.with_suffix(".png"), dpi=(DPI, DPI), optimize=True)
    rgb.save(BASE.with_suffix(".tif"), dpi=(DPI, DPI), compression="tiff_lzw")
    rgb.resize((500, 200), Image.Resampling.LANCZOS).save(preview)
    plt.close(figure)


if __name__ == "__main__":
    main()
