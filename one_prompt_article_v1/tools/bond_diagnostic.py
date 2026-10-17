"""Optional visual troubleshooting helper; not part of the article run."""

from pathlib import Path

import matplotlib.pyplot as plt
import sqlite3
from matplotlib.colors import to_hex
from matplotlib.patches import Circle

from ase.data import covalent_radii
from ase.data.colors import jmol_colors
from ase.db.sqlite import SQLite3Database
from ase.io.pov import get_bondpairs


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "DASC_Bare_Catalysts_RPBE_D4.db"
OUTPUT_PATH = PACKAGE_ROOT / "diagnostics" / "bond_diagnostic.png"
STRUCTURE_QUERY = {
    "metal1": "Co",
    "metal2": "Co",
    "acid": "A2",
    "base": "B1",
    "bridge": "OO",
}


class ReadOnlySQLiteDatabase(SQLite3Database):
    """ASE database reader that cannot create or modify the source database."""

    def _connect(self):
        return sqlite3.connect(
            DATABASE_PATH.as_uri() + "?mode=ro",
            uri=True,
            timeout=20,
        )


def main():
    # Check first for a clear error; the read-only URI also prevents creation on races.
    if not DATABASE_PATH.is_file():
        raise SystemExit(
            f"Required project database does not exist; refusing to create it: {DATABASE_PATH}"
        )

    database = ReadOnlySQLiteDatabase(
        str(DATABASE_PATH),
        create_indices=False,
        use_lock_file=False,
    )
    row = next(database.select(**STRUCTURE_QUERY, limit=1), None)
    if row is None:
        raise SystemExit(f"No structure matched the diagnostic query in {DATABASE_PATH}")

    structure = row.toatoms()
    structure.set_pbc(False)
    structure.center(vacuum=3.0)

    colors = jmol_colors[structure.numbers].copy()
    radii = covalent_radii[structure.numbers] * 0.42
    bonds = sorted(
        {
            tuple(sorted((int(a), int(b))))
            for a, b, _ in get_bondpairs(structure, radius=1.0)
            if a != b
        }
    )

    xy = structure.positions[:, :2]
    lower = (xy - radii[:, None]).min(axis=0)
    upper = (xy + radii[:, None]).max(axis=0)
    span = upper - lower

    width = 1300
    height = round(width * span[1] / span[0])
    figure = plt.figure(
        figsize=(width / 100, height / 100), dpi=100, facecolor=(1, 1, 1, 0)
    )
    axes = figure.add_axes([0, 0, 1, 1])
    axes.set_xlim(lower[0], upper[0])
    axes.set_ylim(lower[1], upper[1])
    axes.set_aspect("equal")
    axes.axis("off")

    for a, b in bonds:
        axes.plot(
            [xy[a, 0], xy[b, 0]],
            [xy[a, 1], xy[b, 1]],
            color="#111111",
            linewidth=5,
            solid_capstyle="round",
            zorder=1,
        )
    for index, (x, y) in enumerate(xy):
        axes.add_patch(
            Circle(
                (x, y),
                radii[index],
                facecolor=to_hex(colors[index]),
                edgecolor="#111111",
                linewidth=1,
                zorder=2,
            )
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_PATH, dpi=100, transparent=True, pad_inches=0)
    plt.close(figure)
    print(f"Wrote {OUTPUT_PATH}; bonds={len(bonds)}, dimensions={width}x{height}, span={span}")


if __name__ == "__main__":
    main()
