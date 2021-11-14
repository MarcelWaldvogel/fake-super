#!/usr/bin/python3
# Usage: fake-super [--restore] <files…>
import argparse
import errno
import os
from pathlib import Path
import secrets
import stat
import sys

from fake_super.version import VERSION


class FormatError(ValueError):
    """Abstract base class"""


class StatFormatError(ValueError):
    """Format of user.rsync.%stat wrong"""


ftypes = {
    stat.S_IFSOCK: 'sck',
    stat.S_IFLNK: 'lnk',
    stat.S_IFREG: 'reg',
    stat.S_IFBLK: 'blk',
    stat.S_IFDIR: 'dir',
    stat.S_IFCHR: 'chr',
    stat.S_IFIFO: 'fif',
    stat.S_IFDOOR: 'dor',  # type: ignore
    stat.S_IFPORT: 'prt',  # type: ignore
    stat.S_IFWHT: 'wht'    # type: ignore
}
fdesc = {
    'sck': "socket",
    'lnk': "symbolic link",
    'reg': "regular file",
    'blk': "block device ({major},{minor})",
    'dir': "directory",
    'chr': "character device ({major},{minor})",
    'fif': "fifo (aka named pipe)",
    'dor': "door",
    'prt': "port",
    'wht': "whiteout entry"
}


def unstat(s):
    attrs = {}
    # Decoding errors here will raise problems later
    s = s.decode('ascii', errors='namereplace')

    # Parts
    parts = s.split(' ')
    if len(parts) != 3:
        raise StatFormatError("three parts required", s)
    if len(parts[0]) != 6:
        raise StatFormatError("six-digit mode required", s)

    # Part 0: Mode (type, permissions)
    if parts[0].lower().startswith('0o'):
        raise StatFormatError("plain octal mode required", s)
    try:
        mode = attrs['mode'] = int(parts[0], 8)
    except ValueError:
        raise StatFormatError("octal mode required", s)
    try:
        attrs['type'] = ftypes[stat.S_IFMT(mode)]
    except KeyError:
        raise StatFormatError("unknown file type", s)
    attrs['perms'] = stat.S_IMODE(mode)

    # Part 1: Major,minor
    dev = parts[1].split(',')
    if len(dev) != 2:
        raise StatFormatError("device id as 'major,minor' required", s)
    try:
        attrs['major'] = int(dev[0])
        attrs['minor'] = int(dev[1])
    except ValueError:
        raise StatFormatError("numeric major,minor device ids required", s)
    if attrs['type'] not in ('blk', 'chr'):
        if attrs['major'] != 0 or attrs['minor'] != 0:
            raise(StatFormatError(
                "major,minor device ids given for non-device", s))

    # Part 2: User:group
    ug = parts[2].split(':')
    if len(ug) != 2:
        raise StatFormatError("ownership as 'owner:group' required", s)
    try:
        attrs['owner'] = int(ug[0])
        attrs['group'] = int(ug[1])
    except ValueError:
        raise StatFormatError("numeric user:group ids required", s)

    return attrs


def statfmt(stat):
    """Format status"""
    return (fdesc[stat['type']]
            + ", permissions {perms:04o}, owner {owner}:{group}"
            ).format(**stat)


def chown(fn, stat, delete_on_error=False):
    try:
        os.lchown(fn, stat['owner'], stat['group'])
    except OSError as e:
        if delete_on_error:
            os.unlink(fn)
        sys.exit("%s: chown: %s" % (fn, e.strerror))


def mktempfn(fn):
    """Return a path object temporary filename in the same directory as `fn`.

    For very long input file names, the resulting file name my exceed the
    maximum length allowed by the OS. This is considered to be unlikely here,
    where only names of character and block devices or FIFOs (named pipes)
    are used as input, which are (a) rare and (b) commonly very short."""
    dirname = os.path.dirname(fn)
    basename = os.path.basename(fn)
    ext = secrets.token_urlsafe(6)  # 36 bits as URL-safe Base64
    return Path(dirname, '.' + basename + '.' + ext)


def restore(fn, stat):
    """Restore attributes"""
    t = stat['type']
    if t in ('chr', 'blk', 'fif'):
        temp_fn = mktempfn(fn)
        try:
            os.mknod(temp_fn, stat['mode'],
                     device=os.makedev(stat['major'], stat['minor']))
        except OSError as e:
            sys.exit("%s (for %s): mknod: %s" % (temp_fn, fn, e.strerror))
        chown(temp_fn, stat, delete_on_error=True)
        try:
            os.rename(temp_fn, fn)
        except OSError as e:
            sys.exit("rename(%s, %s): %s" % (temp_fn, fn, e.strerror))
    elif t == 'lnk':
        try:
            with open(fn, 'r') as link:
                dest = link.read()
        except OSError as e:
            sys.exit("%s: open/read: %s" % (fn, e.strerror))
        temp_fn = mktempfn(fn)
        try:
            os.symlink(temp_fn, dest)
        except OSError as e:
            sys.exit("%s (for %s): mknod: %s" % (temp_fn, fn, e.strerror))
        chown(temp_fn, stat, delete_on_error=True)
        try:
            os.rename(temp_fn, fn)
        except OSError as e:
            sys.exit("rename(%s, %s): %s" % (temp_fn, fn, e.strerror))
    elif t == 'reg':
        # chown(2) resets setuid bits etc. in many settings, so it goes first
        chown(fn, stat)
        try:
            os.chmod(fn, stat['perms'])
        except OSError as e:
            sys.exit("%s: chmod: %s" % (fn, e.strerror))
    else:
        sys.exit("%s: Don't know how to create %s" % (fn, statfmt(stat)))


def main(sysargv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="""Handle permissions stored by `rsync --fake-super`""")
    parser.add_argument('--version',
                        action='version',
                        version=VERSION)
    parser.add_argument('--restore',
                        action='store_true',
                        help="""Restore rights""")
    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        help="""Be quiet: Do not output current status""")
    parser.add_argument('files',
                        nargs='+',
                        help="""List of files""")
    args = parser.parse_args(sysargv)

    retval = 0
    for fn in args.files:
        try:
            attr = os.getxattr(fn, 'user.rsync.%stat')
        except OSError as e:
            if e.errno == errno.ENODATA:  # No such attribute
                sys.stderr.write("%s: Missing `user.rsync.%%stat` attribute,"
                                 " skipping\n" % fn)
                retval = 1
            else:
                sys.exit("%s: %s" % (fn, e.strerror))
        else:
            try:
                stat = unstat(attr)
            except StatFormatError as e:
                sys.exit("%s: Illegal stat info (%r)" % (fn, e.args))
            else:
                if not args.quiet:
                    print("%s: %s" % (fn, statfmt(stat)))
                if args.restore:
                    restore(fn, stat)
    # If there was an error in a list of files,
    # mention it here to avoid confusion
    if retval == 1 and len(args.files) > 1:
        sys.exit("*** Some errors occured")
    return retval


if __name__ == "__main__":
    main()
