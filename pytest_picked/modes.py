import re
import subprocess  # nosec
from abc import ABC, abstractmethod


class Mode(ABC):
    def __init__(self, test_file_convention):
        self.test_file_convention = test_file_convention

    def affected_tests(self):
        raw_output = self.git_output()

        re_list = [
            item.replace(".", r"\.").replace("*", ".*")
            for item in self.test_file_convention
        ]
        re_string = r"(\/|^)" + r"|".join(re_list)

        folders, files = [], []
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
    def command(self):
        return ["git", "diff", "--name-status", "--relative", "master"]

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
        R and C include a percentage of how different the diffed file is, represented as 3 integers.
        The rest of the characters up until the 9th character are spaces.
        If the file was deleted it will have a D at the beginning of the line.
        If the file was renamed, it will have multiple spaces between the filenames and look like this:
        R100  school/migrations/from-school.csv     school/migrations/new-things-from-school.csv
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
