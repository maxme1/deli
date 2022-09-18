"""random data generation"""

import io
import json
import random

import numpy as np
import pytest
import requests  # type: ignore
from PIL import Image  # type: ignore


@pytest.fixture(name="np3d")
def fake_np3d_generator() -> np.ndarray:
    content = requests.get("https://loremflickr.com/320/240").content
    image = Image.open(io.BytesIO(content))
    return np.array(image)


@pytest.fixture(name="np2d")
def fake_np2d_generator(np3d) -> np.ndarray:
    return np3d.mean(2).astype(np3d.dtype)


@pytest.fixture(name="dictionary")
def fake_dictionary() -> dict:
    idx = random.randint(0, 500)
    url = f"https://jsonplaceholder.typicode.com/comments/{idx}"
    content = requests.get(url).content
    return json.loads(content)
