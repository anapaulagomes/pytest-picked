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

    tw = _pytest.config.create_terminal_writer(config)
    tw.line()
    tw.line(f"Afected test files... {len(picked_files)}. {picked_files}")
    tw.line(f"Afected test folders... {len(picked_folders)}. {picked_folders}")

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


def _afected_tests():
    REGEX_FILES = r"\S+.(.*.py)"  # r'(\S+.test_\S+.py)'
    REGEX_FOLDERS = r"\S+.(.*\/)\n"
    raw_output = _get_git_status()
    files = re.findall(REGEX_FILES, raw_output)
    folders = re.findall(REGEX_FOLDERS, raw_output)
    files = [file for file in files if "test" in file]
    folders = [folder for folder in folders if "test" in folder]
    return files, folders


def _get_git_status():
    output = subprocess.run(["git", "status", "--short"], stdout=subprocess.PIPE)
    return output.stdout.decode("utf-8")


# TODO branch changed files git diff --name-only
