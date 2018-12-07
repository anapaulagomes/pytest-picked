from fnmatch import fnmatch
import _pytest

from .modes import Branch, Unstaged


def pytest_addoption(parser):
    group = parser.getgroup("picked")
    group.addoption(
        "--picked",
        action="store",
        dest="picked",
        choices=("only", "first"),
        nargs="?",
        const="only",
        help=(
            "Run the tests related to the changed files either on their own, "
            "or first"
        ),
    )
    group.addoption(
        "--mode",
        action="store",
        dest="picked_mode",
        default="unstaged",
        required=False,
        help="Options: unstaged, branch",
    )


def _get_affected_paths(config):
    picked_mode = config.getoption("picked_mode")
    test_file_convention = config._getini(  # pylint: disable=W0212
        "python_files"
    )

    modes = {
        "branch": Branch(test_file_convention),
        "unstaged": Unstaged(test_file_convention),
    }
    try:
        mode = modes[picked_mode]
    except KeyError:
        error = "Invalid mode. Options: `{}`.".format(", ".join(modes.keys()))
        _write(config, [error])
        config.args = []
        raise ValueError(error)
    else:
        return mode.affected_tests()


def pytest_configure(config):
    picked_type = config.getoption("picked")
    if not picked_type or picked_type != "only":
        return

    picked_files, picked_folders = _get_affected_paths(config)
    config.args = picked_files + picked_folders
    _display_affected_tests(config, picked_files, picked_folders)


def pytest_collection_modifyitems(session, config, items):
    picked_type = config.getoption("picked")
    if not picked_type or picked_type != "first":
        return

    affected_files, affected_folders = _get_affected_paths(config)
    match_paths = affected_files + affected_folders
    # only reorder if there was anything matched
    if match_paths:
        run_first = []
        run_later = []
        for item in items:
            item_path = item.location[0]
            if any(fnmatch(item_path, m) for m in match_paths):
                run_first.append(item)
            else:
                run_later.append(item)
        items[:] = run_first + run_later


def _display_affected_tests(config, files, folders):
    message = "Changed test {}... {}. {}"
    files_msg = message.format("files", len(files), files)
    folders_msg = message.format("folders", len(folders), folders)
    _write(config, [files_msg, folders_msg])


def _write(config, message):
    writer = _pytest.config.create_terminal_writer(config)
    writer.line()

    for line in message:
        writer.line(line)
