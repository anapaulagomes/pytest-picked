import re
import subprocess  # nosec

import _pytest


def pytest_addoption(parser):
    group = parser.getgroup("picked")
    group.addoption(
        "--picked",
        action="store_true",
        dest="picked",
        help="Run the tests related to the changed files",
    )
    group.addoption(
        "--mode",
        action="store",
        dest="picked_mode",
        default="unstaged",
        required=False,
        help="Options: unstaged, branch",
    )


def pytest_configure(config):
    picked_plugin = config.getoption("picked")
    if not picked_plugin:
        return

    picked_mode = config.getoption("picked_mode")
    raw_output = _get_git_status(picked_mode)

    test_file_convention = config._getini("python_files")  # pylint: disable=W0212

    picked_files, picked_folders = _affected_tests(
        raw_output, test_file_convention, mode=picked_mode
    )
    config.args = picked_files + picked_folders

    _display_affected_tests(config, picked_files, picked_folders)


def _display_affected_tests(config, files, folders):
    writer = _pytest.config.create_terminal_writer(config)
    writer.line()
    message = "Changed test {}... {}. {}"
    files_msg = message.format("files", len(files), files)
    folders_msg = message.format("folders", len(folders), folders)
    writer.line(files_msg)
    writer.line(folders_msg)


def _affected_tests(raw_output, test_file_convention, mode="unstaged"):
    """
    Parse affected tests from `git status --short`.

    The command output would look like this:
    A  setup.py
     U tests/test_pytest_picked.py
    ?? .pylintrc

    The first two digits are M, A, D, R, C, U, ? or !
    The third is a white-space and the left is the path of
    the file.
    If the file was renamed, it will look like this:
    R  school/migrations/from-school.csv -> new-things-from-school.csv

    Reference:
    https://git-scm.com/docs/git-status#git-status---short
    """
    re_list = [
        item.replace(".", r"\.").replace("*", ".*") for item in test_file_convention
    ]
    re_string = r"(\/|^)" + r"|".join(re_list)

    folders, files = [], []
    for candidate in raw_output.splitlines():
        if mode == "unstaged":
            file_or_folder = _extract_file_or_folder(candidate)
        else:
            file_or_folder = candidate

        if file_or_folder.endswith("/"):
            folders.append(file_or_folder)
        elif re.search(re_string, file_or_folder):
            files.append(file_or_folder)
    return files, folders


def _extract_file_or_folder(candidate):
    start_path_index = 3
    rename_indicator = "-> "

    if rename_indicator in candidate:
        indicator_index = candidate.find(rename_indicator)
        start_path_index = indicator_index + len(rename_indicator)
    return candidate[start_path_index:]


def _get_git_status(mode="unstaged"):
    if mode == "unstaged":
        command = ["git", "status", "--short"]
    else:
        command = ["git", "diff", "--name-only", "master"]
    output = subprocess.run(command, stdout=subprocess.PIPE)
    return output.stdout.decode("utf-8")
