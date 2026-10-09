"""Unit tests for csv_summary.cli."""

from csv_summary.cli import main


def test_main_valid_file_happy_path(tmp_path, capsys):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n1\n2\n", encoding="utf-8")

    exit_code = main([str(csv_file)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Total rows: 2" in captured.out


def test_main_missing_file_returns_1(tmp_path, capsys):
    missing = tmp_path / "missing.csv"

    exit_code = main([str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error:" in captured.err


def test_main_header_only_returns_0(tmp_path, capsys):
    csv_file = tmp_path / "header_only.csv"
    csv_file.write_text("a,b\n", encoding="utf-8")

    exit_code = main([str(csv_file)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No data rows found" in captured.out


def test_main_wrong_arg_count_exits_2():
    try:
        main([])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected SystemExit for missing argument")
