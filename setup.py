from pathlib import Path
import setuptools

from catimerge import __version__

info = Path(__file__).with_name("README.md").read_text(encoding = "utf8")

setuptools.setup(
    name              = "catimerge",
    url               = "https://github.com/obfusk/catimerge",
    description       = "merge two catima.zip exports",
    long_description  = info,
    long_description_content_type = "text/markdown",
    version           = __version__,
    author            = "FC Stegerman",
    author_email      = "flx@obfusk.net",
    license           = "AGPLv3+",
    classifiers       = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
      # "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    keywords          = "catima export merge",
    entry_points      = dict(console_scripts = ["catimerge = catimerge:main"]),
    packages          = ["catimerge"],
    package_data      = dict(catimerge = ["py.typed"]),
    python_requires   = ">=3.8",
)
