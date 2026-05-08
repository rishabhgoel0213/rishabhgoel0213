#!/usr/bin/env python3
"""Small dependency-free page-count check for generated PDFs."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: check-pdf-pages.py <pdf> <expected-pages>")

    pdf = Path(sys.argv[1])
    expected = int(sys.argv[2])
    data = pdf.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page\b", data))

    if pages != expected:
        raise SystemExit(f"{pdf} has {pages} pages, expected {expected}")

    print(f"{pdf} has {pages} page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
