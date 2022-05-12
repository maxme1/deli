import json
import pickle
from pathlib import Path
from typing import Union
from gzip import GzipFile

__all__ = [
    'PathLike',
    'load', 'save',
    'load_json', 'save_json',
    'load_pickle', 'save_pickle',
    'load_numpy', 'save_numpy',
    'load_csv', 'save_csv',
    'load_text', 'save_text',
]

PathLike = Union[Path, str]


def load(path: PathLike, ext: str = None, **kwargs):
    """
    Load a file located at ``path``.
    ``kwargs`` are format-specific keyword arguments.
    The following extensions are supported:
        npy, tif, png, jpg, bmp, hdr, img, csv,
        dcm, nii, nii.gz, json, mhd, csv, txt, pickle, pkl, config
    """
    name = Path(path).name if ext is None else ext

    if name.endswith(('.npy', '.npy.gz')):
        if name.endswith('.gz'):
            kwargs['decompress'] = True
        return load_numpy(path, **kwargs)
    if name.endswith(('.csv', '.csv.gz')):
        return load_csv(path, **kwargs)
    if name.endswith(('.nii', '.nii.gz', '.hdr', '.img')):
        import nibabel
        return nibabel.load(str(path), **kwargs).get_fdata()
    if name.endswith('.dcm'):
        import pydicom
        return pydicom.dcmread(str(path), **kwargs)
    if name.endswith(('.png', '.jpg', '.tif', '.bmp')):
        from imageio import imread
        return imread(path, **kwargs)
    if name.endswith('.json'):
        return load_json(path, **kwargs)
    if name.endswith(('.pkl', '.pickle')):
        return load_pickle(path, **kwargs)
    if name.endswith('.txt'):
        return load_text(path)
    if name.endswith('.config'):
        import lazycon
        return lazycon.load(path, **kwargs)

    raise ValueError(f'Couldn\'t read file "{path}". Unknown extension.')


def save(value, path: PathLike, **kwargs):
    """
    Save ``value`` to a file located at ``path``.
    ``kwargs`` are format-specific keyword arguments.
    The following extensions are supported:
        npy, npy.gz, tif, png, jpg, bmp, hdr, img, csv
        nii, nii.gz, json, mhd, csv, txt, pickle, pkl
    """
    name = Path(path).name

    if name.endswith(('.npy', '.npy.gz')):
        if name.endswith('.npy.gz') and 'compression' not in kwargs:
            raise ValueError('If saving to gz need to specify a compression.')

        save_numpy(value, path, **kwargs)
    elif name.endswith(('.csv', '.csv.gz')):
        if name.endswith('.csv.gz') and 'compression' not in kwargs:
            raise ValueError('If saving to gz need to specify a compression.')

        save_csv(value, path, **kwargs)
    elif name.endswith(('.nii', '.nii.gz', '.hdr', '.img')):
        import nibabel
        nibabel.save(value, str(path), **kwargs)
    elif name.endswith('.dcm'):
        import pydicom
        pydicom.dcmwrite(str(path), value, **kwargs)
    elif name.endswith(('.png', '.jpg', '.tif', '.bmp')):
        from imageio import imsave
        imsave(path, value, **kwargs)
    elif name.endswith('.json'):
        save_json(value, path, **kwargs)
    elif name.endswith(('.pkl', '.pickle')):
        save_pickle(value, path, **kwargs)
    elif name.endswith('.txt'):
        save_text(value, path)

    else:
        raise ValueError(f'Couldn\'t write to file "{path}". Unknown extension.')


def load_json(path: PathLike):
    """Load the contents of a json file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(value, path: PathLike, *, indent: int = None):
    """Dump a json-serializable object to a json file."""
    with open(path, 'w') as f:
        json.dump(value, f, indent=indent)


def save_numpy(value, path: PathLike, *, allow_pickle: bool = True, fix_imports: bool = True, compression: int = None,
               timestamp: int = None):
    """A wrapper around ``np.save`` that matches the interface ``save(what, where)``."""
    import numpy as np

    if compression is not None:
        with GzipFile(path, 'wb', compresslevel=compression, mtime=timestamp) as file:
            return save_numpy(value, file, allow_pickle=allow_pickle, fix_imports=fix_imports)

    np.save(path, value, allow_pickle=allow_pickle, fix_imports=fix_imports)


def load_numpy(path: PathLike, *, allow_pickle: bool = False, fix_imports: bool = True, decompress: bool = False):
    """A wrapper around ``np.load``"""
    import numpy as np

    if decompress:
        with GzipFile(path, 'rb') as file:
            return load_numpy(file, allow_pickle=allow_pickle, fix_imports=fix_imports)

    return np.load(path, allow_pickle=allow_pickle, fix_imports=fix_imports)


def save_pickle(value, path: PathLike):
    """Pickle a ``value`` to ``path``."""
    with open(path, 'wb') as file:
        pickle.dump(value, file)


def load_pickle(path: PathLike):
    """Load a pickled value from ``path``."""
    with open(path, 'rb') as file:
        return pickle.load(file)


def save_text(value: str, path: PathLike):
    with open(path, mode='w') as file:
        file.write(value)


def load_text(path: PathLike):
    with open(path, mode='r') as file:
        return file.read()


def save_csv(value, path: PathLike, *, compression: int = None, **kwargs):
    if compression is not None:
        kwargs['compression'] = {
            'method': 'gzip',
            'compresslevel': compression,
        }

    value.to_csv(path, **kwargs)


def load_csv(path: PathLike, **kwargs):
    import pandas as pd
    return pd.read_csv(path, **kwargs)
