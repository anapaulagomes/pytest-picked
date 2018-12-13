try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest
from pytest_picked.modes import Branch, Unstaged


class TestUnstaged:
    def test_should_return_git_status_command(self):
        mode = Unstaged([])
        command = mode.command()

        assert isinstance(command, list)
        assert mode.command() == ["git", "status", "--short"]

    @pytest.mark.parametrize(
        "line,expected_line",
        [
            (" D tests/migrations/auto.py", None),
            (
                "R  tests/from-school.csv -> test_new_things.py",
                "test_new_things.py",
            ),
            (
                "R  tests/from-school.csv -> tests/test_new_things.py",
                "tests/test_new_things.py",
            ),
            (" M test.py", "test.py"),
            ("AD test.py", None),
            ("?? api/", "api/"),
        ],
    )
    def test_parser_should_ignore_no_paths_characteres(
        self, line, expected_line
    ):
        mode = Unstaged([])
        parsed_line = mode.parser(line)

        assert parsed_line == expected_line

    def test_should_list_unstaged_changed_files_as_affected_tests(self):
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

        with patch("pytest_picked.modes.subprocess.check_output") as subprocess_mock:
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


class TestBranch:
    def test_should_return_command_that_list_all_changed_files(self):
        mode = Branch([])
        command = mode.command()

        assert isinstance(command, list)
        assert mode.command() == ["git", "diff", "--name-only", "master"]

    def test_parser_should_return_the_candidate_itself(self):
        mode = Branch([])
        line = "tests/test_pytest_picked.py\n"
        parsed_line = mode.parser(line)

        assert parsed_line == line

    def test_should_list_branch_changed_files_as_affected_tests(self):
        raw_output = (
            b"pytest_picked.py\n"
            + b"tests/test_pytest_picked.py\n"
            + b"tests/test_other_module.py"
        )
        test_file_convention = ["test_*.py", "*_test.py"]

        with patch("pytest_picked.modes.subprocess.check_output") as subprocess_mock:
            subprocess_mock.return_value.stdout = raw_output
            mode = Branch(test_file_convention)
            files, folders = mode.affected_tests()

        expected_files = [
            "tests/test_pytest_picked.py",
            "tests/test_other_module.py",
        ]
        expected_folders = []

        assert files == expected_files
        assert folders == expected_folders
