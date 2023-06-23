#!/usr/bin/python3
# encoding: utf-8
# SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

r"""
Merge two catima.zip exports.
"""

import csv
import io
import re
import zipfile

from dataclasses import dataclass, field, fields
from typing import Dict, List, TextIO, Tuple

__version__ = "0.0.1"
IMAGE_REGEX_V2 = re.compile(r"(card_)(\d+)(_(?:front|back|icon)\.png)")


class Error(Exception):
    """Base class for errors."""


@dataclass
class Export:
    """Export."""

    @property
    def version(self) -> int:
        raise NotImplementedError


@dataclass
class ExportV2(Export):
    """V2 export."""

    groups_keys: List[str] = field(default_factory=list)
    groups: List[List[str]] = field(default_factory=list)
    cards_keys: List[str] = field(default_factory=list)
    cards: List[List[str]] = field(default_factory=list)
    card_groups_keys: List[str] = field(default_factory=list)
    card_groups: List[List[str]] = field(default_factory=list)
    image_files: List[str] = field(default_factory=list)

    @property
    def version(self) -> int:
        return 2


def catimerge(first_zip: str, second_zip: str, output_zip: str, *,
              verbose: bool = False) -> None:
    """Merge two catima .zip exports."""
    if verbose:
        print(f"Merging {first_zip!r} and {second_zip!r} into {output_zip!r}...")
    with zipfile.ZipFile(first_zip) as zf1:
        with zipfile.ZipFile(second_zip) as zf2:
            if verbose:
                print("Parsing...")
            merge(parse(zf1), parse(zf2), zf1, zf2, output_zip, verbose=verbose)


def merge(e1: Export, e2: Export, zf1: zipfile.ZipFile, zf2: zipfile.ZipFile,
          output_zip: str, *, verbose: bool = False) -> None:
    """Merge two exports."""
    if isinstance(e1, ExportV2) and isinstance(e2, ExportV2):
        merge_v2(e1, e2, zf1, zf2, output_zip, verbose=verbose)
    elif e1.version == e2.version:
        raise Error(f"Unsupported version: {e1.version}")
    else:
        raise Error(f"Incompatible versions: {e1.version} and {e2.version}")


def merge_v2(e1: ExportV2, e2: ExportV2, zf1: zipfile.ZipFile, zf2: zipfile.ZipFile,
             output_zip: str, *, verbose: bool = False) -> None:
    """Merge two V2 exports."""
    if verbose:
        print("Version: 2")
        print(f"ZIP #1 has {len(e1.groups):3d} group(s), "
              f"{len(e1.cards):3d} card(s), "
              f"{len(e1.card_groups):3d} card group(s), "
              f"{len(e1.image_files):3d} image file(s)")
        print(f"ZIP #2 has {len(e2.groups):3d} group(s), "
              f"{len(e2.cards):3d} card(s), "
              f"{len(e2.card_groups):3d} card group(s), "
              f"{len(e2.image_files):3d} image file(s)")
        print("Merging...")
    image_map: Dict[str, Tuple[zipfile.ZipFile, str]] = {}
    e_out = ExportV2()
    for f in fields(ExportV2):
        if f.name.endswith("_keys"):
            if getattr(e1, f.name) != getattr(e2, f.name):
                raise Error(f"Mismatched {f.name}")
            setattr(e_out, f.name, getattr(e1, f.name))
    e_out.groups = [[g] for g in sorted(set(g[0] for g in e1.groups + e2.groups))]
    e1_max_id = _merge_cards_v2(e1, e2, e_out)
    _merge_card_groups_v2(e1, e2, e_out, e1_max_id)
    for filename in e1.image_files:
        image_map[filename] = (zf1, filename)
    for filename in e2.image_files:
        new_filename = _rename_file_v2(filename, e1_max_id)
        image_map[new_filename] = (zf2, filename)
    csv_data = unparse_v2(e_out)
    if verbose:
        print(f"Output has {len(e_out.groups):3d} group(s), "
              f"{len(e_out.cards):3d} card(s), "
              f"{len(e_out.card_groups):3d} card group(s), "
              f"{len(image_map):3d} image file(s)")
    print("Writing...")
    with zipfile.ZipFile(output_zip, "w") as zf_out:
        zf_out.writestr("catima.csv", csv_data)
        for name, (zf, old_name) in image_map.items():
            zf_out.writestr(name, zf.read(old_name))


def _merge_cards_v2(e1: ExportV2, e2: ExportV2, e_out: ExportV2) -> int:
    e1_max_id = 0
    cards_id_idx = e1.cards_keys.index("_id")
    for card in e1.cards:
        card_id = int(card[cards_id_idx])
        if card_id < 1:
            raise Error("ID < 1")
        e1_max_id = max(e1_max_id, card_id)
        e_out.cards.append(card)
    for card in e2.cards:
        card_id = int(card[cards_id_idx])
        if card_id < 1:
            raise Error("ID < 1")
        new_card = card[:]
        new_card[cards_id_idx] = str(card_id + e1_max_id)
        e_out.cards.append(new_card)
    return e1_max_id


def _merge_card_groups_v2(e1: ExportV2, e2: ExportV2, e_out: ExportV2,
                          e1_max_id: int) -> None:
    e_out.card_groups = e1.card_groups[:]
    card_groups_cardid_idx = e1.card_groups_keys.index("cardId")
    for card_group in e2.card_groups:
        card_id = int(card_group[card_groups_cardid_idx])
        new_card_group = card_group[:]
        new_card_group[card_groups_cardid_idx] = str(card_id + e1_max_id)
        e_out.card_groups.append(new_card_group)


def _rename_file_v2(filename: str, e1_max_id: int) -> str:
    if m := IMAGE_REGEX_V2.fullmatch(filename):
        pre, card_id, suf = m.groups()
        return f"{pre}{int(card_id) + e1_max_id}{suf}"
    raise Error(f"Unexpected file name format in import: {filename!r}")


def parse(zf: zipfile.ZipFile) -> Export:
    """Parse catima.csv and list PNGs."""
    export = None
    image_files = []
    for info in zf.infolist():
        if info.filename == "catima.csv":
            fh = io.StringIO(zf.read(info).decode())
            version = fh.readline().strip()
            fh.readline()
            if version == "2":
                export = parse_v2(fh)
            else:
                raise Error(f"Unexpected version in import: {version}")
        elif info.filename.endswith(".png"):
            image_files.append(info.filename)
        else:
            raise Error(f"Unexpected file in import: {info.filename!r}")
    if export is None:
        raise Error("No catima.csv in import")
    export.image_files = image_files
    return export


# FIXME: handle malformatted files
def parse_v2(fh: TextIO) -> ExportV2:
    """Parse V2 catima.csv (after version + blank line)."""
    export = ExportV2()
    header = None
    keys = [export.groups_keys, export.cards_keys, export.card_groups_keys]
    records = [export.groups, export.cards, export.card_groups]
    reader = csv.reader(fh)
    for row in reader:
        if header is None:
            header = row
            keys[0].extend(header)
        elif row:
            records[0].append(row)
        else:
            header = None
            keys = keys[1:]
            records = records[1:]
    return export


def unparse_v2(export: ExportV2) -> str:
    """Turn V2 export into a catima.csv (str)."""
    fh = io.StringIO(newline="")
    fh.write("2\n")
    keys = [export.groups_keys, export.cards_keys, export.card_groups_keys]
    records = [export.groups, export.cards, export.card_groups]
    for ks, rs in zip(keys, records):
        fh.write("\n")
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(ks)
        for r in rs:
            writer.writerow(r)
    return fh.getvalue()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="catimerge")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("first_zip", metavar="FIRST_ZIP")
    parser.add_argument("second_zip", metavar="SECOND_ZIP")
    parser.add_argument("output_zip", metavar="OUTPUT_ZIP")
    args = parser.parse_args()
    catimerge(args.first_zip, args.second_zip, args.output_zip,
              verbose=args.verbose)


if __name__ == "__main__":
    main()

# vim: set tw=80 sw=4 sts=4 et fdm=marker :
