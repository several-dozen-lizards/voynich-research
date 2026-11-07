import os
from pathlib import Path
(Path(os.environ["TEMP"]) / "LARGE.bin").write_bytes(b"x" * 8192)
