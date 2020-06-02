# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
this project adheres to [Semantic Versioning](https://semver.org/), and
[Gitmoji](https://gitmoji.carloscuesta.me/).


# 0.1.0 - [Unreleased]
## Added
- Support for `--quiet` and `--restore`
- Added security considerations section to [`README.md`](./README.md)
- Adopted Gitmoji
- Added static analysis and unit tests with CI
- Added `LICENSE.md` (MIT License)

## Fixed
- Fixed static analysis complaints
- Fixed error messages
- Devices and named pipes are created with temporary names first
  (the underlying `mknod` system call does not replace the existing dummy file,
  the one which has the `user.rsync.%stat` attribute stored)

## Changed
- Moved VERSION to version.py (for coverage output regex)
