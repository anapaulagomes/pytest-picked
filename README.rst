===============
pytest-picked
===============

.. image:: https://github.com/anapaulagomes/pytest-picked/workflows/Tests/badge.svg
    :target: https://github.com/anapaulagomes/pytest-picked/actions?query=workflow%3ATests
    :alt: See Test Status on Github Actions

.. image:: https://github.com/anapaulagomes/pytest-picked/workflows/Publish%20to%20Test%20PyPi/badge.svg
    :target: https://test.pypi.org/project/pytest-picked/
    :alt: See Package Status on Test PyPI

.. image:: https://github.com/anapaulagomes/pytest-picked/workflows/Publish%20to%20PyPI/badge.svg
    :target: https://pypi.org/project/pytest-picked/
    :alt: See Package Status on PyPI

.. image:: https://img.shields.io/conda/vn/conda-forge/pytest-picked.svg
    :target: https://anaconda.org/conda-forge/pytest-picked
    :alt: Conda forge package

.. image:: https://img.shields.io/pypi/pyversions/pytest-picked.svg
    :target: https://pypi.org/project/pytest-picked
    :alt: Supported Python versions

Run the tests related to the unstaged files or the current branch (according to Git)

---

.. image:: demo.gif
    :height: 400px
    :alt: Demo

Let's say you have the following output from ``git status``:

::

  $ git status

  On branch master
  Your branch is ahead of 'origin/master' by 1 commit.
    (use "git push" to publish your local commits)

  Untracked files:
    (use "git add <file>..." to include in what will be committed)

    api.py
    tests/api/
    tests/test_board.py

  nothing added to commit but untracked files present (use "git add" to track)


Running ``pytest --picked``, the plugin will run all tests that come from this output.

::

  $ pytest --picked

  ============================= test session starts =============================
  platform darwin -- Python 3.6.4, pytest-3.6.0, py-1.5.3, pluggy-0.6.0
  rootdir: /Users/ana.gomes/personal-workspace/grandma, inifile:
  plugins: picked-0.1.0, mock-1.10.0, flask-0.10.0, deadfixtures-2.0.1
  collecting 34 items
  Changed test files... 1. ['tests/test_board.py']
  Changed test folders... 1. ['tests/api/']
  collected 34 items

  tests/test_board.py .                                                      [ 50%]
  tests/api/test_new.py .                                                    [100%]

  =========================== 2 passed in 0.07 seconds ===========================

All tests will be run from files and folders which are modified but not yet committed.
No more copy and paste!


Usage
-----

::

  $ pytest --picked

  $ pytest --picked=first

  $ pytest --picked --mode=branch

  $ pytest --picked --mode=unstaged  # default

  $ pytest --picked --mode=branch --parent-branch=main # if your parent branch differs from "master"


Features
--------

Using ``git status``, this plugin allows you to:

* Run only tests from modified test files
* Run tests from modified test files first, followed by all unmodified tests

Installation
------------

You can install ``pytest-picked`` via `pip`_ from `PyPI`_::

    $ pip install pytest-picked


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-picked" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/anapaulagomes/pytest-picked/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pytest-picked/
.. _`PyPI`: https://pypi.org/project/pytest-picked/
