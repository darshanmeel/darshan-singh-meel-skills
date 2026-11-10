"""Run selected cells of a Jupyter notebook, read-only only. Outputs are saved into the notebook.

Usage: python run_cells.py <notebook.ipynb> <cell numbers, 1-based, e.g. 1 4 5>
Refuses the whole run if any chosen cell contains anything but SELECT / SHOW / DESCRIBE / EXPLAIN.
Code cells tagged 'setup' (connection, imports) before them are run first — and checked the same way.
"""
import re
import sys

import nbformat
from nbclient import NotebookClient

BLOCKED = re.compile(
    r"\b(insert|update|delete|merge|copy\s+into|truncate|create|alter|drop|undrop|grant|revoke"
    r"|call|execute\s+immediate|use\s+(role|warehouse|database|schema|catalog)|put|remove|unload|refresh"
    r"|optimize|vacuum|restore)\b"
    r"|\.write\b|saveAsTable|insertInto|to_sql\(|\bdbt\s+(run|build|seed|snapshot)"
    r"|^\s*[!%](sh|bash)?",
    re.IGNORECASE | re.MULTILINE,
)


def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(--|#).*$", "", src, flags=re.M)


def main(path, wanted):
    nb = nbformat.read(path, as_version=4)
    to_run = sorted(set(wanted) | {i for i in setup_cells(nb) if i < max(wanted)})
    for n in to_run:
        cell = nb.cells[n - 1]
        if cell.cell_type != "code":
            sys.exit(f"cell {n} is not a code cell")
        hit = BLOCKED.search(strip_comments(cell.source))
        if hit:
            sys.exit(f"REFUSED: cell {n} contains '{hit.group(0).strip()}' — only SELECT/SHOW/DESCRIBE/EXPLAIN may run. "
                     "Move it to the changes or prerequisite_ddl notebook for the user to run.")
    client = NotebookClient(nb, timeout=600, allow_errors=True)
    with client.setup_kernel():
        for n in to_run:
            client.execute_cell(nb.cells[n - 1], n - 1)
    nbformat.write(nb, path)
    print(f"ran cells {sorted(wanted)}; outputs saved to {path}")


def setup_cells(nb):
    """Code cells tagged 'setup' (connection, imports) are run before the requested cells."""
    return {i for i, c in enumerate(nb.cells, 1) if "setup" in c.get("metadata", {}).get("tags", [])}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], [int(x) for x in sys.argv[2:]])
