#!/usr/bin/env python3
"""Run from the cloned repository without installing a package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'src'))
from marketing_ai_skills.black_friday.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
