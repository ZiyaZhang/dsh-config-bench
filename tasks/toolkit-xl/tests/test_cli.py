import os
import subprocess
import sys

import toolkit


# Every test starts `python -m toolkit ...` in a child process whose working
# directory is the directory that contains the toolkit package.


# --- text ---------------------------------------------------------------


def test_cli_text_prints_table_of_contents():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "text"],
        input="Install\nUsage\n",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 0
    assert proc.stdout == (
        "| # | Title   | Anchor   |\n"
        "|---|---------|----------|\n"
        "| 1 | Install | #install |\n"
        "| 2 | Usage   | #usage   |\n"
    )


def test_cli_text_last_line_without_newline_is_a_title():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "text"],
        input="One\nTwo",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 0
    assert proc.stdout == (
        "| # | Title | Anchor |\n"
        "|---|-------|--------|\n"
        "| 1 | One   | #one   |\n"
        "| 2 | Two   | #two   |\n"
    )


# --- data ---------------------------------------------------------------


def test_cli_data_csv_prints_one_json_line_per_match():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "data", "csv", "$[*].name"],
        input="name,age\nann,3\nbob,5\n",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 0
    assert proc.stdout == '"ann"\n"bob"\n'


def test_cli_data_ini_section_is_printed_as_json_object():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "data", "ini", "$.b"],
        input="[b]\nz = 1\na = two\n",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 0
    assert proc.stdout == '{"a": "two", "z": 1}\n'


def test_cli_data_malformed_path_is_a_handled_error():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "data", "csv", "$["],
        input="name,age\nann,3\n",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert proc.stderr.startswith("error: ")
    assert len(proc.stderr.splitlines()) == 1


# --- calc ---------------------------------------------------------------


def test_cli_calc_prints_whole_result_without_decimal_point():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "calc", "2 * 3 + 1"],
        input="",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 0
    assert proc.stdout == "7\n"


def test_cli_calc_strips_trailing_zeros():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "calc", "10 / 4"],
        input="",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 0
    assert proc.stdout == "2.5\n"


def test_cli_calc_division_by_zero_is_a_handled_error():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "calc", "1 / 0"],
        input="",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert proc.stderr.startswith("error: ")
    assert len(proc.stderr.splitlines()) == 1


def test_cli_calc_assignment_without_equals_sign_is_a_handled_error():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "calc", "x + 1", "x"],
        input="",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert proc.stderr.startswith("error: ")
    assert len(proc.stderr.splitlines()) == 1


def test_cli_calc_without_expression_is_a_usage_error():
    root = os.path.dirname(os.path.dirname(os.path.abspath(toolkit.__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "calc"],
        input="",
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
    )
    assert proc.returncode == 2
    assert proc.stdout == ""


# --- no or unknown subcommand -------------------------------------------


