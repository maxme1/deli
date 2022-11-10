from pathlib import Path

from deli import save, load

extra_args = {
    'file.csv': {'index': False}
}


def test_idempotency(subtests, tests_root, tmpdir):
    for file in (tests_root / 'assets').rglob('*'):
        if file.is_dir():
            continue

        with subtests.test(file=file.name):
            target = Path(tmpdir) / file.name
            save(load(file), target, **extra_args.get(file.name, {}))

            with file.open('rb') as expected, target.open('rb') as actual:
                assert actual.read() == expected.read()
