"""Write every device config to backend/configs/<DEVICE>.txt.

Usage (from backend/): python -m app.export_configs [output_dir]
"""
import sys
from pathlib import Path

from .configgen import list_devices, render

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "configs"


def main(out: Path = DEFAULT_OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for device in list_devices():
        path = out / f"{device}.txt"
        path.write_text(render(device))
        print(f"wrote {path}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT)
