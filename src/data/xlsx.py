"""Minimal .xlsx reader (stdlib only: an .xlsx file is a zip of XML parts), so no openpyxl dependency."""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _col_index(ref: str) -> int:
    """'C12' -> 2 (zero-based column)."""
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path: Path) -> dict[str, list[list[str]]]:
    """All sheets as {sheet name: rows of cell strings}; empty cells are ''."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        # Shared strings: most text cells point into this table.
        shared = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        # Sheet names in workbook order, mapped to their XML parts through the relationships file.
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rels}
        rid = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        out = {}
        for sh in wb.find("m:sheets", NS):
            part = target[sh.get(rid)].lstrip("/")
            part = part if part.startswith("xl/") else "xl/" + part
            rows = []
            for row in ET.fromstring(z.read(part)).iter(f"{{{NS['m']}}}row"):
                cells = {}
                for c in row.findall("m:c", NS):
                    t, v = c.get("t"), c.find("m:v", NS)
                    if t == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
                    else:
                        val = v.text if v is not None and v.text else ""
                    cells[_col_index(c.get("r"))] = val
                rows.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
            out[sh.get("name")] = rows
    return out
