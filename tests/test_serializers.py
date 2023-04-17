from pathlib import Path

import pytest

from deli import save, load, WrongSerializer

extra_args = {
    'file.csv': {'index': False}
}


def test_idempotency(subtests, tests_root, tmpdir):
    for file in sorted(list((tests_root / 'assets').rglob('*'))):
        if file.is_dir():
            continue

        with subtests.test(file=file.name):
            target = Path(tmpdir) / file.name
            save(load(file), target, **extra_args.get(file.name, {}))

            with file.open('rb') as expected, target.open('rb') as actual:
                assert actual.read() == expected.read(), file.name


def test_no_extension(tmpdir):
    # file with garbage
    file = Path(tmpdir, 'garbage')
    file.write_text('abc')
    with pytest.raises(WrongSerializer):
        load(file)

    # empty file
    file = Path(tmpdir, 'empty')
    file.touch()
    with pytest.raises(WrongSerializer):
        load(file)


def test_not_found_file():
    with pytest.raises(FileNotFoundError):
        load('/some/file.json')
