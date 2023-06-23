<!-- SPDX-FileCopyrightText: 2023 FC Stegerman <flx@obfusk.net> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

[![GitHub Release](https://img.shields.io/github/release/obfusk/catimerge.svg?logo=github)](https://github.com/obfusk/catimerge/releases)
[![PyPI Version](https://img.shields.io/pypi/v/catimerge.svg)](https://pypi.python.org/pypi/catimerge)
[![Python Versions](https://img.shields.io/pypi/pyversions/catimerge.svg)](https://pypi.python.org/pypi/catimerge)
[![CI](https://github.com/obfusk/catimerge/workflows/CI/badge.svg)](https://github.com/obfusk/catimerge/actions?query=workflow%3ACI)
[![AGPLv3+](https://img.shields.io/badge/license-AGPLv3+-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

<!--
<a href="https://repology.org/project/catimerge/versions">
  <img src="https://repology.org/badge/vertical-allrepos/catimerge.svg?header="
    alt="Packaging status" align="right" />
</a>

<a href="https://repology.org/project/python:catimerge/versions">
  <img src="https://repology.org/badge/vertical-allrepos/python:catimerge.svg?header="
    alt="Packaging status" align="right" />
</a>
-->

# catimerge

Merge two [Catima](https://catima.app) `.zip` exports.

```sh
$ catimerge -v catima1.zip catima2.zip out.zip
Merging 'catima1.zip' and 'catima2.zip' into 'out.zip'...
Parsing...
Version: 2
ZIP #1 has   1 group(s),   9 card(s),   2 card group(s),   5 image file(s)
ZIP #2 has   2 group(s),   5 card(s),   3 card group(s),   3 image file(s)
Merging...
Output has   3 group(s),  14 card(s),   5 card group(s),   8 image file(s)
Writing...
```

NB: does not support password-protected exports.

## Installing

### Using pip

```bash
$ pip install catimerge
```

NB: depending on your system you may need to use e.g. `pip3 --user`
instead of just `pip`.

### From git

NB: this installs the latest development version, not the latest
release.

```bash
$ git clone https://github.com/obfusk/catimerge.git
$ cd catimerge
$ pip install -e .
```

NB: you may need to add e.g. `~/.local/bin` to your `$PATH` in order
to run `catimerge`.

To update to the latest development version:

```bash
$ cd catimerge
$ git pull --rebase
```

## Dependencies

* Python >= 3.8.

## License

[![AGPLv3+](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.html)

<!-- vim: set tw=70 sw=2 sts=2 et fdm=marker : -->
