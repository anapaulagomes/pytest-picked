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
            if file_or_folder.endswith("/"):
                folders.append(file_or_folder)
            elif re.search(re_string, file_or_folder):
                files.append(file_or_folder)
        return files, folders

    def git_output(self):
        output = subprocess.run(self.command(), stdout=subprocess.PIPE)
        return output.stdout.decode("utf-8")

    def print_command(self):
        return " ".join(self.command())

    def __str__(self):
        return (
            f"Mode: {self.__class__.__name__}\nCommand: {self.print_command()} Parser rule: {self.parser.__doc__}"
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
        return ["git", "diff", "--name-only", "master"]

    def parser(self, candidate):
        """The candidate itself."""
        return candidate


class Unstaged(Mode):

    def command(self):
        return ["git", "status", "--short"]

    def parser(self, candidate):
        """Discard the first 3 characters."""
        start_path_index = 3
        rename_indicator = "-> "

        if rename_indicator in candidate:
            indicator_index = candidate.find(rename_indicator)
            start_path_index = indicator_index + len(rename_indicator)
        return candidate[start_path_index:]
