
from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent

sys.path.insert(0, str(PROJECT_DIR))

from main import main

if __name__ == "__main__":
    raise SystemExit(main())
