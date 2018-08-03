import _pytest

from .modes import Branch, Unstaged


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
    test_file_convention = config._getini(  # pylint: disable=W0212
        "python_files"
    )

    modes = {
        "branch": Branch(test_file_convention),
        "unstaged": Unstaged(test_file_convention),
    }
    mode = modes.get(picked_mode, "unstaged")

    picked_files, picked_folders = mode.affected_tests()

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
