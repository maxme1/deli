import runpy
from pathlib import Path

from setuptools import setup, find_packages  # type: ignore

NAME = 'deli'
DESCRIPTION = 'Smart serialization and deserialization for (almost) any python object'
LICENSE = 'MIT'
URL = 'https://github.com/maxme1/deli'

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3 :: Only',
    'Operating System :: OS Independent',
]
KEYWORDS = ['serialization']

ROOT = Path(__file__).resolve().parent

VERSION = runpy.run_path(str(ROOT / NAME / '__version__.py'))['__version__']

with open(ROOT / 'README.md', 'r', encoding='utf-8') as file:
    LONG_DESCRIPTION = file.read()

with open(ROOT / 'requirements.txt', 'r', encoding='utf-8') as file:
    REQUIREMENTS = file.read().splitlines()

DOWNLOAD_URL = f'{URL}/archive/v{VERSION}.tar.gz'

setup(
    name=NAME,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license=LICENSE,
    version=VERSION,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=find_packages(include=(NAME,)),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require={
        'all': [
            'pandas',
            'pydicom',
            'nibabel',
            'numpy',
            'imageio>=2.0.0',
        ]
    },
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    python_requires='>=3.6',
)
