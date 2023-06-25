#!/usr/bin/python3
# encoding: utf-8
# SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

r"""
Merge two catima.zip exports.

$ catimerge --help
usage: catimerge [-h] [-v] [--version] FIRST_ZIP SECOND_ZIP OUTPUT_ZIP

positional arguments:
  FIRST_ZIP
  SECOND_ZIP
  OUTPUT_ZIP

options:
  -h, --help     show this help message and exit
  -v, --verbose
  --version      show program's version number and exit
$ catimerge -v catima1.zip catima2.zip out.zip
Merging 'catima1.zip' and 'catima2.zip' into 'out.zip'...
Parsing...
Version: 2
ZIP #1 has   1 group(s),   9 card(s),   2 card group(s),   5 image file(s)
ZIP #2 has   2 group(s),   5 card(s),   3 card group(s),   3 image file(s)
Merging...
Output has   3 group(s),  14 card(s),   5 card group(s),   8 image file(s)
Writing...
"""

import csv
import io
import re
import zipfile

from dataclasses import dataclass, field, fields
from typing import Dict, List, Optional, TextIO, Tuple

__version__ = "0.1.1"
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
    r"""
    Merge two V2 exports.

    >>> import os, tempfile
    >>> zf1 = zipfile.ZipFile("test/catima1.zip")
    >>> zf2 = zipfile.ZipFile("test/catima2.zip")
    >>> for info in zf1.infolist():
    ...     print(f"{info.CRC:08x} {info.filename}")
    c21ab654 catima.csv
    3ba1ef60 card_2_icon.png
    aad741e5 card_1_front.png
    33d945fd card_1_icon.png
    >>> for info in zf2.infolist():
    ...     print(f"{info.CRC:08x} {info.filename}")
    3d100805 catima.csv
    225e333a card_1_icon.png
    d869a610 card_2_front.png
    >>> e1 = parse(zf1)
    >>> e2 = parse(zf2)
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     out = os.path.join(tmpdir, "out.zip")
    ...     merge(e1, e2, zf1, zf2, out, verbose=True)
    ...     zfo = zipfile.ZipFile(out)
    ...     for info in zfo.infolist():
    ...         print(f"{info.CRC:08x} {info.filename}")
    ...     r = parse(zfo)
    ...     r.groups_keys
    ...     r.cards_keys
    ...     r.card_groups_keys
    ...     r.groups
    ...     for c in r.cards: print(c)
    ...     r.card_groups
    ...     r.image_files
    Version: 2
    ZIP #1 has   2 group(s),   4 card(s),   3 card group(s),   3 image file(s)
    ZIP #2 has   2 group(s),   2 card(s),   2 card group(s),   2 image file(s)
    Merging...
    Output has   3 group(s),   6 card(s),   5 card group(s),   5 image file(s)
    Writing...
    9c69bd23 catima.csv
    3ba1ef60 card_2_icon.png
    aad741e5 card_1_front.png
    33d945fd card_1_icon.png
    225e333a card_5_icon.png
    d869a610 card_6_front.png
    ['_id']
    ['_id', 'store', 'note', 'validfrom', 'expiry', 'balance', 'balancetype', 'cardid', 'barcodeid', 'barcodetype', 'headercolor', 'starstatus', 'lastused', 'archive']
    ['cardId', 'groupId']
    [['"two\''], ['one'], ['three']]
    ['2', 'bar', '', '', '', '0', '', ' bar " ', '', 'CODE_128', '-2092896', '0', '1687700491', '0']
    ['3', 'baz', '', '', '', '0', '', '12345678901234567890', '', 'DATA_MATRIX', '-14642227', '0', '1687700517', '0']
    ['1', 'foo', '', '', '', '5', 'JPY', 'foo', '', 'AZTEC', '-2092896', '0', '1687700411', '0']
    ['4', 'qux', '', '', '', '0', '', 'foo\nbar\nbaz\nhttps://example.com', '', 'QR_CODE', '-14642227', '0', '1687700622', '0']
    ['5', 'baz', '', '', '', '0', '', 'foo\nbar\nbaz"', '', 'PDF_417', '-2092896', '0', '1687702090', '0']
    ['6', 'quux', 'this\nis\na\n"note"\n\nhttps://catima.app', '', '1710370800000', '0', '', '123456789012', '', 'UPC_A', '-416706', '0', '1687700899', '0']
    [['2', '"two\''], ['3', '"two\''], ['1', 'one'], ['5', 'one'], ['5', 'three']]
    ['card_2_icon.png', 'card_1_front.png', 'card_1_icon.png', 'card_5_icon.png', 'card_6_front.png']

    """
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
    r"""
    Parse V2 catima.csv (after version + blank line).

    >>> zf = zipfile.ZipFile("test/catima1.zip")
    >>> r = parse(zf)
    >>> r.groups_keys
    ['_id']
    >>> r.cards_keys
    ['_id', 'store', 'note', 'validfrom', 'expiry', 'balance', 'balancetype', 'cardid', 'barcodeid', 'barcodetype', 'headercolor', 'starstatus', 'lastused', 'archive']
    >>> r.card_groups_keys
    ['cardId', 'groupId']
    >>> r.groups
    [['one'], ['"two\'']]
    >>> for c in r.cards: print(c)
    ['2', 'bar', '', '', '', '0', '', ' bar " ', '', 'CODE_128', '-2092896', '0', '1687700491', '0']
    ['3', 'baz', '', '', '', '0', '', '12345678901234567890', '', 'DATA_MATRIX', '-14642227', '0', '1687700517', '0']
    ['1', 'foo', '', '', '', '5', 'JPY', 'foo', '', 'AZTEC', '-2092896', '0', '1687700411', '0']
    ['4', 'qux', '', '', '', '0', '', 'foo\nbar\nbaz\nhttps://example.com', '', 'QR_CODE', '-14642227', '0', '1687700622', '0']
    >>> r.card_groups
    [['2', '"two\''], ['3', '"two\''], ['1', 'one']]
    >>> r.image_files
    ['card_2_icon.png', 'card_1_front.png', 'card_1_icon.png']

    >>> zf = zipfile.ZipFile("test/catima2.zip")
    >>> r = parse(zf)
    >>> r.groups_keys
    ['_id']
    >>> r.cards_keys
    ['_id', 'store', 'note', 'validfrom', 'expiry', 'balance', 'balancetype', 'cardid', 'barcodeid', 'barcodetype', 'headercolor', 'starstatus', 'lastused', 'archive']
    >>> r.card_groups_keys
    ['cardId', 'groupId']
    >>> r.groups
    [['one'], ['three']]
    >>> for c in r.cards: print(c)
    ['1', 'baz', '', '', '', '0', '', 'foo\nbar\nbaz"', '', 'PDF_417', '-2092896', '0', '1687702090', '0']
    ['2', 'quux', 'this\nis\na\n"note"\n\nhttps://catima.app', '', '1710370800000', '0', '', '123456789012', '', 'UPC_A', '-416706', '0', '1687700899', '0']
    >>> r.card_groups
    [['1', 'one'], ['1', 'three']]
    >>> r.image_files
    ['card_1_icon.png', 'card_2_front.png']

    """
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
            if len(row) != len(header):
                raise Error("Mismatched row size")
            records[0].append(row)
        else:
            if len(keys) < 2:
                raise Error("Too many sections")
            header = None
            keys = keys[1:]
            records = records[1:]
    if len(keys) > 1:
        raise Error("Too few sections")
    return export


def unparse_v2(export: ExportV2) -> str:
    r"""
    Turn V2 export into a catima.csv (str).

    >>> zf = zipfile.ZipFile("test/catima1.zip")
    >>> s = unparse_v2(parse(zf)).encode()
    >>> s == zf.read("catima.csv")
    True

    >>> zf = zipfile.ZipFile("test/catima2.zip")
    >>> s = unparse_v2(parse(zf)).encode()
    >>> s == zf.read("catima.csv")
    True

    """
    fh = io.StringIO(newline="")
    fh.write("2\r\n")
    keys = [export.groups_keys, export.cards_keys, export.card_groups_keys]
    records = [export.groups, export.cards, export.card_groups]
    for ks, rs in zip(keys, records):
        fh.write("\r\n")
        writer = csv.writer(fh, lineterminator="\r\n")
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


def gui() -> None:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    def select_file(i: int, lbl: ttk.Label, what: str, save: bool = False) -> None:
        title = f"Select {what}"
        filetypes = [("ZIP files", "*.zip")]
        if save:
            file = filedialog.asksaveasfilename(title=title, filetypes=filetypes)
        else:
            file = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if file:
            files[i] = file
            lbl.config(text=file)
            if all(files):
                btn_merge.config(state=tk.NORMAL)

    def on_open1() -> None:
        select_file(0, lbl_file1, "ZIP #1")

    def on_open2() -> None:
        select_file(1, lbl_file2, "ZIP #2")

    def on_open3() -> None:
        select_file(2, lbl_file3, "output ZIP", save=True)

    def on_merge() -> None:
        try:
            first_zip, second_zip, output_zip = files
            assert first_zip and second_zip and output_zip
            catimerge(first_zip, second_zip, output_zip)
        except (Error, zipfile.BadZipFile) as e:
            messagebox.showerror(title="catimerge", message=f"Error: {e}")
        else:
            messagebox.showinfo(title="catimerge", message="Saved")

    files: List[Optional[str]] = [None, None, None]
    nofile = "(no file selected)"
    win = tk.Tk()
    win.title("catimerge")
    btn_open1 = ttk.Button(win, text="Select ZIP #1", command=on_open1)
    lbl_file1 = ttk.Label(win, text=nofile)
    btn_open2 = ttk.Button(win, text="Select ZIP #2", command=on_open2)
    lbl_file2 = ttk.Label(win, text=nofile)
    btn_open3 = ttk.Button(win, text="Select output ZIP", command=on_open3)
    lbl_file3 = ttk.Label(win, text=nofile)
    btn_merge = ttk.Button(win, text="Merge", command=on_merge)
    btn_merge.config(state=tk.DISABLED)
    for w in [btn_open1, lbl_file1, btn_open2, lbl_file2, btn_open3, lbl_file3, btn_merge]:
        w.pack(padx=5, pady=5)
    win.minsize(400, 250)
    win.update()
    win.mainloop()


if __name__ == "__main__":
    main()

# vim: set tw=80 sw=4 sts=4 et fdm=marker :
