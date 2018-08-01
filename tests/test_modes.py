from unittest.mock import patch

from modes import Branch, Unstaged


def test_check_parser():
    test_file_convention = ["test_*.py", "*_test.py"]
    raw_output = (
        b"R  school/migrations/from-school.csv -> test_new_things.py\n"
        + b"D  school/migrations/0032_auto_20180515_1308.py\n"
        + b"?? Pipfile\n"
        + b"!! school/tests/test_rescue_students.py\n"
        + b"C  tests/\n"
        + b" M .pre-commit-config.yaml\n"
        + b" M picked.py\n"
        + b"A  setup.py\n"
        + b" U tests/test_pytest_picked.py\n"
        + b"?? random/tests/\n"
        + b" M intestine.py\n"
        + b"?? api/\n"
        + b" M tests_new/intestine.py\n"
    )

    with patch("modes.subprocess.run") as subprocess_mock:
        subprocess_mock.return_value.stdout = raw_output
        mode = Unstaged(test_file_convention)
        files, folders = mode.affected_tests()

    expected_files = [
        "test_new_things.py",
        "school/tests/test_rescue_students.py",
        "tests/test_pytest_picked.py",
    ]
    expected_folders = ["tests/", "random/tests/", "api/"]

    assert files == expected_files
    assert folders == expected_folders


def test_should_parse_branch_changed_files():
    raw_output = (
        b"pytest_picked.py\n"
        + b"tests/test_pytest_picked.py\n"
        + b"tests/test_other_module.py"
    )
    test_file_convention = ["test_*.py", "*_test.py"]

    with patch("modes.subprocess.run") as subprocess_mock:
        subprocess_mock.return_value.stdout = raw_output
        mode = Branch(test_file_convention)
        files, folders = mode.affected_tests()

    expected_files = ["tests/test_pytest_picked.py", "tests/test_other_module.py"]
    expected_folders = []

    assert files == expected_files
    assert folders == expected_folders
