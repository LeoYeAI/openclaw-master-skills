"""Allow running palaia as `python3 -m palaia`."""

import sys

from palaia.cli import main

if __name__ == "__main__":
    sys.exit(main())
