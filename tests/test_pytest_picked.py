from unittest.mock import patch


def test_shows_affected_tests(testdir):
    result = testdir.runpytest("--picked")

    assert "Changed test files..." in result.stdout.str()
    assert "Changed test folders..." in result.stdout.str()


def test_help_message(testdir):
    result = testdir.runpytest("--help")

    result.stdout.fnmatch_lines(
        ["picked:", "*--picked*Run the tests related to the changed files"]
    )


def test_filter_items_according_with_git_status(testdir, tmpdir):
    with patch("modes.subprocess.run") as subprocess_mock:
        output = b" M test_flows.py\n M test_serializers.py\n A tests/\n"
        subprocess_mock.return_value.stdout = output

        result = testdir.runpytest("--picked")
        testdir.makepyfile(
            ".py",
            test_flows="""
            def test_sth():
                assert True
            """,
            test_serializers="""
            def test_sth():
                assert True
            """,
        )
        tmpdir.mkdir("tests")
        result.stdout.fnmatch_lines(
            [
                "Changed test files... 2. "
                + "['test_flows.py', 'test_serializers.py']",
                "Changed test folders... 1. ['tests/']",
            ]
        )


def test_return_nothing_if_does_not_have_changed_test_files(testdir):
    with patch("modes.subprocess.run") as subprocess_mock:
        subprocess_mock.return_value.stdout = b""

        result = testdir.runpytest("--picked")

        result.stdout.fnmatch_lines(["Changed test files... 0. []"])


def test_return_error_if_not_git_repository(testdir):
    o = b"fatal: Not a git repository (or any of the parent directories): .git"
    with patch("modes.subprocess.run") as subprocess_mock:

        subprocess_mock.return_value.stdout = o

        result = testdir.runpytest("--picked")

        result.stdout.fnmatch_lines(["Changed test files... 0. []"])


def test_dont_call_the_plugin_if_dont_find_it_as_option(testdir):
    result = testdir.runpytest()

    assert "Changed test files..." not in result.stdout.str()


def test_filter_file_when_is_either_modified_and_not_staged(testdir):
    with patch("modes.subprocess.run") as subprocess_mock:
        output = b"MM test_picked.py\nM  tests/test_pytest_picked.py"
        subprocess_mock.return_value.stdout = output

        result = testdir.runpytest("--picked")
        testdir.makepyfile(
            ".py",
            test_flows="""
            def test_sth():
                assert True
            """,
            test_serializers="""
            def test_sth():
                assert True
            """,
        )
        result.stdout.fnmatch_lines(
            [
                "Changed test files... 2. "
                + "['test_picked.py', 'tests/test_pytest_picked.py']",
                "Changed test folders... 0. []",
            ]
        )


def test_handle_with_white_spaces(testdir):
    with patch("modes.subprocess.run") as subprocess_mock:
        output = (
            b" M school/tests/test_flows.py\n"
            + b"A  school/tests/test_serializers.py\n M sales/tasks.py"
        )
        subprocess_mock.return_value.stdout = output

        result = testdir.runpytest("--picked")
        testdir.makepyfile(
            ".py",
            test_flows="""
            def test_sth():
                assert True
            """,
            test_serializers="""
            def test_sth():
                assert True
            """,
        )
        result.stdout.fnmatch_lines(
            [
                "Changed test files... 2. "
                + "['school/tests/test_flows.py', "
                + "'school/tests/test_serializers.py']",
                "Changed test folders... 0. []",
            ]
        )


def test_should_match_with_the_begin_of_path(testdir, tmpdir, tmpdir_factory):
    with patch("modes.subprocess.run") as subprocess_mock:
        output = b" A tests/\n"
        subprocess_mock.return_value.stdout = output

        result = testdir.runpytest("--picked")
        tmpdir.mkdir("tests")
        tmpdir.mkdir("othertests")

        result.stdout.fnmatch_lines(
            ["Changed test files... 0. []", "Changed test folders... 1. ['tests/']"]
        )


def test_should_accept_branch_as_mode(testdir, tmpdir):
    with patch("modes.subprocess.run") as subprocess_mock:
        output = b"test_flows.py\ntest_serializers.py\n"
        subprocess_mock.return_value.stdout = output

        result = testdir.runpytest("--picked", "--mode=branch")
        testdir.makepyfile(
            ".py",
            test_flows="""
            def test_sth():
                assert True
            """,
            test_serializers="""
            def test_sth():
                assert True
            """,
        )
        tmpdir.mkdir("tests")
        result.stdout.fnmatch_lines(
            [
                "Changed test files... 2. "
                + "['test_flows.py', 'test_serializers.py']",
                "Changed test folders... 0. []",
            ]
        )
