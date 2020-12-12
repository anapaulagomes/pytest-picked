import re
import subprocess  # nosec
from abc import ABC, abstractmethod


class Mode(ABC):
    def __init__(self, test_conventions, only_modified_tests=False):
        self.test_conventions = test_conventions
        self.only_modified_tests = only_modified_tests

    def only_tests(self, raw_output, re_list):
        test_file_regex = r"(\/|^)" + r"|".join(re_list)
        test_regex = ""
        class_regex = ""
        for item in self.test_conventions["function"]:
            test_regex = (
                test_regex + r"(?<=def\s).*{0}.*.[\w](?=\(|/:)".format(item) + r"|"
            )
        else:
            test_regex = test_regex[:-1]

        for item in self.test_conventions["class"]:
            class_regex = (
                class_regex + r"(?<=class\s).*{0}.*.[\w](?=\(|\:)".format(item) + r"|"
            )
        else:
            class_regex = class_regex[:-1]
        tests = []
        last_file_name = None
        file_dict = {}
        class_name = ""
        was_it_class = False
        for candidate in raw_output.splitlines():
            file_or_test = self.parser(candidate)
            if file_or_test:
                if re.search(test_file_regex, file_or_test):
                    last_file_name = file_or_test
                    if last_file_name not in file_dict.keys():
                        file_dict[last_file_name] = []
                        was_it_class = False
                if re.search(class_regex, file_or_test):
                    match = re.findall(class_regex, file_or_test)
                    class_name = match[0]
                    file_dict[last_file_name].append(class_name)
                    was_it_class = True

                elif re.search(test_regex, file_or_test):
                    if not was_it_class:
                        match = re.findall(test_regex, file_or_test)
                        test_name = match[0]
                        file_dict[last_file_name].append(class_name + "::" + test_name)
            class_name = ""
        for file_name in file_dict.keys():
            for test_name in file_dict[file_name]:
                tests.append(
                    file_name + "::" + test_name
                ) if "::" not in test_name else tests.append(file_name + test_name)

        return list(dict.fromkeys(tests)), []

    def affected_tests(self):
        raw_output = self.git_output()
        re_list = [
            item.replace(".", r"\.").replace("*", ".*")
            for item in self.test_conventions["file"]
        ]
        re_string = r"(\/|^)" + r"|".join(re_list)
        folders, files = [], []
        if self.only_modified_tests:
            return self.only_tests(raw_output, re_list)
        else:
            for candidate in raw_output.splitlines():
                file_or_folder = self.parser(candidate)
                if file_or_folder:
                    if file_or_folder.endswith("/"):
                        folders.append(file_or_folder)
                    elif re.search(re_string, file_or_folder):
                        files.append(file_or_folder)
        return files, folders

    def git_output(self):
        output = subprocess.run(self.command(), stdout=subprocess.PIPE)  # nosec
        return output.stdout.decode("utf-8").expandtabs()

    def print_command(self):
        return " ".join(self.command())

    def __str__(self):
        return "Mode: {}\nCommand: {} Parser rule: {}".format(
            self.__class__.__name__, self.print_command(), self.parser.__doc__
        )

    @property
    @abstractmethod
    def command(self):
        pass

    @abstractmethod
    def parser(self, candidate):
        pass


class Branch(Mode):
    def __init__(self, test_file_convention, parent_branch="master"):
        super().__init__(test_file_convention)
        self.parent_branch = parent_branch

    def command(self):
        return ["git", "diff", "--name-status", "--relative", self.parent_branch]

    def parser(self, candidate):
        """
        Discard the first 8 characters.

        Parse affected tests from Branch command.
        The command output would look like this:
        D       .pyup.yml
        M       pytest_picked/modes.py
        M       requirements.txt
        M       requirements_test.txt
        M       tests/test_modes.py
        R098    tests/test_pytest_picked.py     tests/test_pytest_picked.py
        The first two digits are M, A, D, R, C, U, ? or !
        R and C include a percentage of how different the diffed file is,
        represented as 3 integers.
        The rest of the characters up until the 9th character are spaces.
        If the file was deleted it will have a D at the beginning of the line.
        If the file was renamed, it will have multiple spaces between the filenames
        and look like this:
        R100  school/from-school.csv     school/new-things-from-school.csv
        The number of spaces are dependent on the length of the filenames.
        Reference:
        https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---name-status
        """
        start_path_index = 8
        rename_regex = r"^R\d+.*\s+(.*)"
        delete_indicator = "D       "
        deleted_and_renamed_indicator = "AD      "

        if candidate.startswith(delete_indicator):
            return
        if candidate.startswith(deleted_and_renamed_indicator):
            return
        rename_matching = re.match(rename_regex, candidate)
        if rename_matching:
            return rename_matching.group(1)
        return candidate[start_path_index:]


class Unstaged(Mode):
    def command(self):
        return ["git", "status", "--short"]

    def parser(self, candidate):
        """
        Discard the first 3 characters.

        Parse affected tests from Unstaged command.
        The command output would look like this:
        A  setup.py
        U tests/test_pytest_picked.py
        ?? .pylintrc
        D  tests/migrations/auto.py
        The first two digits are M, A, D, R, C, U, ? or !
        The third is a white-space and the left is the path of
        the file.
        If the file was deleted it will have a D at the beginning
        of the line. If the file was renamed, it will look like this:
        R  school/migrations/from-school.csv -> new-things-from-school.csv
        Reference:
        https://git-scm.com/docs/git-status#git-status---short
        """
        start_path_index = 3
        rename_indicator = "-> "
        delete_indicator = "D  "
        deleted_and_renamed_indicator = "AD "

        if candidate.startswith(delete_indicator):
            return
        if candidate.startswith(deleted_and_renamed_indicator):
            return
        if rename_indicator in candidate:
            indicator_index = candidate.find(rename_indicator)
            start_path_index = indicator_index + len(rename_indicator)
        return candidate[start_path_index:]


class OnlyChanged(Mode):
    def command(self):
        return ["git", "diff"]

    def parser(self, candidate):
        """
        Discard the first 6 characters in case of file name.

        Parse the modified file using the file indicator '+++ b/'
        Parse affected tests from using regex 'def' and '@@'
        The command output would look like this:
        diff --git a/tests/migrations/auto.py b/tests/migrations/auto.py
        index 2ce07c4..ebd406e 100644
        --- a/tests/migrations/auto.py
        +++ b/tests/migrations/auto.py
        @@ -181,6 +181,7 @@ def test_positive_migration(session, ad_data):

        Reference:
        https://git-scm.com/docs/git-diff#git-diff
        """
        start_path_index = 6
        file_indicator = "+++ b/"
        modified_test_indicator = "@@ "
        new_test_indicator = "+"

        if candidate.startswith(file_indicator):
            return candidate[start_path_index:]
        if candidate.startswith(modified_test_indicator):
            return candidate
        if candidate.startswith(new_test_indicator):
            return candidate
