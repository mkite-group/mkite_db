import os
import sys
from pathlib import Path
from subprocess import call


def main():
    manage_py_path = Path(__file__).resolve().parent.parent / "manage.py"

    if not manage_py_path.is_file():
        print("Error: manage.py not found.")
        sys.exit(1)

    sys.argv.pop(0)  # Remove the script name from the arguments
    call([sys.executable, str(manage_py_path)] + sys.argv)


if __name__ == "__main__":
    main()
