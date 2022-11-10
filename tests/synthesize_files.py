from pathlib import Path

import numpy as np
from imageio.v3 import imwrite

root = Path(__file__).resolve().parent / 'assets/synthetic'
root.mkdir(exist_ok=True)

imwrite(root / 'file.png', np.random.randint(0, 256, size=(10, 10, 4), dtype=np.uint8))
