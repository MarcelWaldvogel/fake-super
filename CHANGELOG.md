# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), this
project adheres to [Semantic Versioning](https://semver.org/), and
[Gitmoji](https://gitmoji.carloscuesta.me/).

# 0.2.1 - 2021-11-17

## Added

- `project_urls` and `README.md` are now packaged

## Fixed

## Changed

# 0.2.0 - 2021-11-17

## Added

- Restore directory permissions
- Logo
- Support Python 3.10, PyPy 7.3.7 in (Python 3.7 and 3.8 mode)
- Tests in VSCode/VSCodium

## Fixed

- Newlines (and other characters) at end of the string (and individual number
  fields) are now recognized and complained about.
- `rsync` does not always use full 6 digits for the mode
- Symlink creation now works

## Changed

- Switch build/test/CI to `setup.cfg`, `tox`, `pytest`
- Exceptions raised by `unstat()` now also return strings, not tuples
- Homepage

# 0.1.1 - 2021-11-14

## Added

- More unit tests (discovering the bugs fixed below)

## Fixed

- Recognize more illegal formats
- Do not access uninitialized variables in error handlers
- Correctly format error messages

## Changed

- No longer requires `xattr` package

# 0.1.0 - 2021-11-13

## Added

- Support for symlinks
- Support for `--quiet` and `--restore`
- Added security considerations section to [`README.md`](./README.md)
- Adopted Gitmoji
- Added static analysis and unit tests with CI
- Added `LICENSE.md` (MIT License)

## Fixed

- Fixed static analysis complaints
- Fixed error messages
- Devices, links, and named pipes are created with temporary names first (the
  underlying `mknod` and `symlink` system calls do not replace the existing
  dummy file, the one which has the `user.rsync.%stat` attribute stored)

## Changed

- Moved VERSION to version.py (for coverage output regex)
- Version numbers of non-tagged versions now end in `.postX`, where `X` is the
  number of commits since the tag (unless overridden by `FORCE_VERSION`
  environment variable).
