#!/usr/bin/env python3
"""Regenerate the value tables in README.md from gwp_reference.json.

The README publishes the numbers, so it must not be able to drift from the file
the tool actually uses. Everything between the markers is generated; edit the
reference, run this, commit both. CI fails if they disagree.

  python3 render_tables.py          # rewrite README.md in place
  python3 render_tables.py --check  # exit 1 if the README is out of date
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
REF = json.loads((HERE / "gwp_reference.json").read_text())
V, EX, BASES = REF["values"], REF["exclusions"], REF["bases"]
BEGIN, END = "<!-- BEGIN GENERATED TABLES -->", "<!-- END GENERATED TABLES -->"

# Common names, because nobody searches for "HFC_410A" — they search "R-410A".
LABEL = {
    "CO2": "Carbon dioxide (CO₂)", "CH4_fossil": "Methane, fossil (CH₄)",
    "CH4_biogenic": "Methane, non-fossil (CH₄)", "N2O": "Nitrous oxide (N₂O)",
    "SF6": "Sulphur hexafluoride (SF₆)", "NF3": "Nitrogen trifluoride (NF₃)",
    "SO2F2": "Sulphuryl fluoride (SO₂F₂)", "HC_290": "R-290 (propane)",
    "PFC_CF4": "PFC-14 (CF₄)", "PFC_C2F6": "PFC-116 (C₂F₆)",
    "PFC_C3F8": "PFC-218 (C₃F₈)", "PFC_C4F10": "PFC-31-10 (C₄F₁₀)",
    "PFC_C5F12": "PFC-41-12 (C₅F₁₂)", "PFC_C6F14": "PFC-51-14 (C₆F₁₄)",
    "PFC_c_C4F8": "PFC-318 (c-C₄F₈)",
}
BLENDS = {"HFC_404A", "HFC_407A", "HFC_407C", "HFC_407F", "HFC_410A", "HFC_422D",
          "HFC_448A", "HFC_449A", "HFC_450A", "HFC_452A", "HFC_454B", "HFC_507A",
          "HFC_513A"}


def name(k):
    if k in LABEL:
        return LABEL[k]
    if k in BLENDS:
        return f"R-{k.split('_')[1]}"
    if k.startswith("HFC_"):
        return f"HFC-{k[4:].replace('_', '-')}"
    if k.startswith("HFO_"):
        return f"HFO-{k[4:]}"
    return k.replace("_", "-")


def cell(gas, b):
    v = V.get(gas, {}).get(b)
    if v is None:
        return "—"
    out = f"{v:,.4g}" if v < 1 else f"{int(v):,}" if float(v).is_integer() else f"{v:,}"
    return out + " ‡" if b in EX.get(gas, []) else out


def table(keys, caption):
    head = " | ".join(REF["base_names"][b] for b in BASES)
    rows = [f"| {name(k)} | " + " | ".join(cell(k, b) for b in BASES) + " |"
            for k in sorted(keys, key=name)]
    return (f"**{caption}**\n\n| Gas | {head} |\n|---|---|---|---|\n"
            + "\n".join(rows) + "\n")


def build():
    main = ["CO2", "CH4_fossil", "CH4_biogenic", "N2O", "SF6", "NF3", "SO2F2"]
    blends = sorted(k for k in V if k in BLENDS)
    pfc = sorted(k for k in V if k.startswith("PFC"))
    rest = sorted(set(V) - set(main) - set(blends) - set(pfc))
    parts = [
        table(main, "The Kyoto basket"),
        table(rest, "Single-compound refrigerants and other fluorinated gases"),
        table(blends, "Refrigerant blends — re-derived at every report, which is where most errors live"),
        table(pfc, "Perfluorocarbons"),
        "‡ This tool will not judge a cell labelled with that report — see "
        "[what it will not judge](#what-will-it-refuse-to-judge).\n",
    ]
    return "\n".join(parts)


def main_():
    readme = HERE / "README.md"
    s = readme.read_text()
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), s, re.S)
    if not m:
        sys.exit(f"markers not found in README.md: {BEGIN} … {END}")
    new = f"{BEGIN}\n\n{build()}\n{END}"
    if "--check" in sys.argv:
        if m.group(0).strip() != new.strip():
            print("README tables are out of date — run: python3 render_tables.py")
            return 1
        print("README tables match gwp_reference.json")
        return 0
    readme.write_text(s[:m.start()] + new + s[m.end():])
    print(f"regenerated {len(V)} gases into README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main_())
