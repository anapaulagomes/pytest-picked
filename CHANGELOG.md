# Changelog

## [Unreleased]

## [0.4.3] - 2020-03-20
### Fixed
- Fix delete indicator for unstagged mode (#75)
- Use `git diff name-status` for branch mode (#72)

## [0.4.1] - 2019-03-07
### Modified
- Support relative paths

## [0.4.0] - 2018-12-07
### Added
- Added --picked=first mode, which will run all tests, but with any changed tests queued first

## [0.3.2] - 2018-11-25
### Added
- Add pyup support

## [0.3.0] - 2018-08-09
### Added
- Option to run tests modified in the current branch

## [0.2.0] - 2018-07-13
### Added
- Filter tests according with pytest file convention
- Only collects the tests from `git status`
- LambdaLint with Pylint and Bandit and Black in Tox

## [0.1.0] - 2018-05-24
### Added
- Run the tests according with changed files

[Unreleased]: https://github.com/anapaulagomes/pytest-picked/compare/v0.4.3...HEAD
[0.4.3]: https://github.com/anapaulagomes/pytest-picked/compare/v0.4.1...v0.4.3
[0.4.1]: https://github.com/anapaulagomes/pytest-picked/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/anapaulagomes/pytest-picked/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/anapaulagomes/pytest-picked/compare/v0.3.0...v0.3.2
[0.3.0]: https://github.com/anapaulagomes/pytest-picked/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anapaulagomes/pytest-picked/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/anapaulagomes/pytest-picked/compare/a5d86647c511ea56d0d4c42b416b2d7bac8111f6...v0.1.0
