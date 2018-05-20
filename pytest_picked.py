import re
import subprocess
import _pytest.config


def pytest_addoption(parser):
    group = parser.getgroup("picked")
    group.addoption(
        "--picked",
        action="store_true",
        dest="picked",
        help="Run the tests related to the changed files",
    )


def pytest_collection_modifyitems(session, items, config):
    picked_plugin = config.getoption("picked")
    if not picked_plugin:
        return

    picked_files, picked_folders = _afected_tests()
    _display_afected_tests(config, picked_files, picked_folders)

    to_be_tested = []
    for index, item in enumerate(items):
        if item.location[0] in picked_files:
            to_be_tested.append(item)
        else:
            for test in picked_folders:
                if test in item.location[0]:
                    to_be_tested.append(item)
                    break
    items[:] = to_be_tested


def _display_afected_tests(config, files, folders):
    tw = _pytest.config.create_terminal_writer(config)
    tw.line()
    message = "Changed test {}... {}. {}"
    files_msg = message.format("files", len(files), files)
    folders_msg = message.format("folders", len(folders), folders)
    tw.line(files_msg)
    tw.line(folders_msg)


def _afected_tests():
    REGEX_FILES = r"\S+.(.*.py)"  # r'(\S+.test_\S+.py)'
    REGEX_FOLDERS = r"\S+.(.*\/)\n"
    raw_output = _get_git_status()
    files = re.findall(REGEX_FILES, raw_output)
    folders = re.findall(REGEX_FOLDERS, raw_output)
    files = [file.strip() for file in files if "test" in file]
    folders = [folder.strip() for folder in folders if "test" in folder]
    return files, folders


def _get_git_status():
    command = ["git", "status", "--short"]
    output = subprocess.run(command, stdout=subprocess.PIPE)
    return output.stdout.decode("utf-8")


# TODO branch changed files git diff --name-only
