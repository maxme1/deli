from os import PathLike
from typing import Any

from .helpers import ExtensionMatch, NoBuffer
from .packaged import Gzip
from ..serializer import REGISTRY, Hint


class Nifty(ExtensionMatch, NoBuffer):
    extensions = '.nii', '.nii.gz'

    def _match_value(self, value):
        return isinstance(value, Nifti1Image)

    def load_path(self, source: PathLike, hint: Hint, params: dict) -> Any:
        return nibabel.load(source, **params)

    def save_path(self, value: Any, destination: PathLike, hint: Hint, params: dict) -> Hint:
        nibabel.save(value, destination, **params)
        if not hint.endswith(self.extensions):
            return '.nii'
        return hint


# TODO:
# load from buffer
# nii = nibabel.FileHolder(fileobj=buffer)
# return Nifti1Image.from_file_map({'header': nii, 'image': nii})

# save to buffer
# buffer.write(value.to_bytes())
# with  Opener(BytesIO()) as bio:
#     # file_map = value.make_file_map({'image': bio, 'header': bio})
#     file_map = {'image': nibabel.FileHolder(fileobj=bio), 'header': nibabel.FileHolder(fileobj=bio)}
#     print(file_map)
#     value.to_file_map(file_map)
#     buffer.write(bio.getvalue())


try:
    import nibabel
    from nibabel import Nifti1Image

    REGISTRY.append(Nifty())
    REGISTRY.append(Gzip(Nifty()))

except ImportError:
    pass
