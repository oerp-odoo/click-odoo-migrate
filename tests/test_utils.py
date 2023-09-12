import click
import pytest

from xodoo.utils import do_sorted, parse_path


def test_01_parse_mig_path_is_dir(path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN
    res = parse_path(str(path_mig_1))
    # THEN
    assert len(res) == 2
    assert path_mig_1 / "2022-02-19-partners-companies.py" in res
    assert path_mig_1 / "2022-02-20-titles.py" in res


def test_02_parse_mig_path_is_py_file(path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN
    res = parse_path(str(path_mig_1 / "2022-02-19-partners-companies.py"))
    # THEN
    assert len(res) == 1
    assert [path_mig_1 / "2022-02-19-partners-companies.py"] == res


def test_03_parse_mig_path_is_txt_file(path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN, THEN
    with pytest.raises(click.ClickException, match="File must end with .py extension."):
        parse_path(str(path_mig_1 / "info.txt"))


def test_04_parse_mig_path_not_exist(path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN, THEN
    with pytest.raises(click.ClickException, match=r"Path (.+) does not exist"):
        parse_path(str(path_mig_1 / "not-existing-path"))


def test_05_sort_by_sorted():
    # WHEN
    res = do_sorted(["1 x 2", "10 x 1", "1 x 1", "2 x 1"], "sorted")
    # THEN
    assert res == ["1 x 1", "1 x 2", "10 x 1", "2 x 1"]


def test_06_sort_by_natsorted():
    # WHEN
    res = do_sorted(["1 x 2", "10 x 1", "1 x 1", "2 x 1"], "natsorted")
    # THEN
    assert res == ["1 x 1", "1 x 2", "2 x 1", "10 x 1"]


def test_07_sort_by_unknown():
    with pytest.raises(ValueError):
        do_sorted(["1 x 2", "10 x 1", "1 x 1", "2 x 1"], "unknown")
