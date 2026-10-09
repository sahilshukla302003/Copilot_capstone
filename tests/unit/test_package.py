"""Smoke test confirming the csv_summary package is importable."""


def test_import_package() -> None:
    import csv_summary

    assert csv_summary.__version__
