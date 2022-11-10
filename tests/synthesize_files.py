import pickle
from pathlib import Path

import numpy as np

try:
    from imageio.v3 import imread, imwrite
except ImportError:
    from imageio import imread, imwrite

root = Path(__file__).resolve().parent / 'assets/synthetic'
root.mkdir(exist_ok=True)

image = np.random.randint(0, 256, size=(10, 10, 4), dtype=np.uint8)
imwrite(root / 'file.png', image)
with open(root / 'file.pkl', 'wb') as file:
    pickle.dump(image, file)
