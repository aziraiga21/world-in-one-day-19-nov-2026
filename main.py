import os
from pathlib import Path
from shutil import copyfile

source = Path(__file__).resolve().with_name("entry.png")
destination = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output")) / "entry.png"
destination.parent.mkdir(parents=True, exist_ok=True)
if not destination.exists() or not destination.samefile(source):
    copyfile(source, destination)
