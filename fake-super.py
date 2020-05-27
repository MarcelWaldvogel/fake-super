#!/usr/bin/python3
# Usage: fake-super [--restore] <files…>
import argparse
import errno
import os
import stat
import sys
import xattr


class FormatError(ValueError):
    """Abstract base class"""
    pass


class StatFormatError(ValueError):
    """Format of user.rsync.%stat wrong"""
    def __init__(self, message):
        self.message = message


ftypes = { 
    stat.S_IFSOCK: 'sck',
    stat.S_IFLNK: 'lnk',
    stat.S_IFREG: 'reg',
    stat.S_IFBLK: 'blk',
    stat.S_IFDIR: 'dir',
    stat.S_IFCHR: 'chr',
    stat.S_IFIFO: 'fif',
    stat.S_IFDOOR: 'dor',
    stat.S_IFPORT: 'prt',
    stat.S_IFWHT: 'wht'
}
fdesc = {
    'sck': "socket",
    'lnk': "symbolic link",
    'reg': "regular file",
    'blk': "block device ({major},{minor})",
    'dir': "directory",
    'chr': "character device ({major},{minor})",
    'fif': "fifo",
    'dor': "door",
    'prt': "port",
    'wht': "whiteout entry"
}


def unstat(s):
    attrs = {}
    s = s.decode('ascii', errors='namereplace')

    # Parts
    parts = s.split(' ')
    if len(parts) != 3:
        raise StatFormatError("three parts required")
    if len(parts[0]) != 6:
        raise StatFormatError("six-digit mode required")

    # Part 0: Mode (type, permissions)
    try:
        mode = attrs['mode'] = int(parts[0], 8)
    except ValueError:
        raise StatFormatError("octal mode required")
    try:
        attrs['type'] = ftypes[stat.S_IFMT(mode)]
    except KeyError:
        raise StatFormatError("unknown file type")
    attrs['perms'] = stat.S_IMODE(mode)

    # Part 1: Major,minor
    dev = parts[1].split(',')
    if len(dev) != 2:
        raise StatFormatError("device id as 'major,minor' required")
    try:
        attrs['major'] = int(dev[0])
        attrs['minor'] = int(dev[1])
    except ValueError:
        raise StatFormatError("numeric major,minor device ids required")
    if attrs['type'] not in ('blk', 'chr'):
        if attrs['major'] != 0 or attrs['minor'] != 0:
            raise("major,minor device ids given for non-device")

    # Part 2: User:group
    ug = parts[2].split(':')
    if len(ug) != 2:
        raise StatFormatError("ownership as 'owner:group' required")
    try:
        attrs['owner'] = int(ug[0])
        attrs['group'] = int(ug[1])
    except ValueError:
        raise StatFormatError("numeric user:group ids required")

    return attrs


def statfmt(stat):
    """Format status"""
    return (fdesc[stat['type']]
            + ", permissions {perms:04o}, owner {owner}:{group}").format(**stat)


def chown(fn, stat):
    try:
        os.chown(fn, stat['owner'], stat['group'])
    except OSError as e:
        sys.exit("%s: chown: %s" % (fn, e.strerror))


def restore(fn, stat):
    """Restore attributes"""
    t = stat['type']
    if t in ('chr', 'blk', 'fif'):
        try:
            os.mknod(fn, stat['mode'],
                device=os.makedev(stat['major'], stat['minor']))
        except OSError as e:
            sys.exit("%s: mknod: %s" % (fn, e.strerror))
        chown(fn, stat)
    elif t == 'reg':
        # chown(2) resets setuid bits etc. in many settings, so it goes first
        chown(fn, stat)
        try:
            os.chmod(fn, stat['perms'])
        except OSError as e:
            sys.exit("%s: chmod: %s" % (fn, e.strerror))
    else:
        sys.exit("%s: Don't know how to create %s", fn, statfmt(stat))


def main():
    parser = argparse.ArgumentParser(
        description="""Handle permissions stored by `rsync --fake-super`""")
    parser.add_argument('--restore',
            action='store_true',
            help="""Restore rights""")
    parser.add_argument('--quiet', '-q',
            action='store_true',
            help="""Be quiet: Do not output current status""")
    parser.add_argument('files',
            nargs='+',
            help="""List of files""")
    args = parser.parse_args()

    retval = 0
    for fn in args.files:
        try:
            attr = xattr.getxattr(fn, 'user.rsync.%stat')
        except OSError as e:
            if e.errno == errno.ENODATA: # No such attribute
                sys.stderr.write("%s: Missing `user.rsync.%%stat` attribute, skipping\n" % fn)
                retval = 1
            else:
                sys.exit("%s: %s" % (fn, e.strerror))
        else:
            try:
                stat = unstat(attr)
            except StatFormatError as e:
                sys.exit("%s: Illegal stat info" % (fn, e.message))
            else:
                if not args.quiet:
                    print("%s: %s" % (fn, statfmt(stat)))
                if args.restore:
                    restore(fn, stat)
    # If there was an error in a list of files, mention it here to avoid confusion
    if retval == 1 and len(args.files) > 1:
        sys.exit("*** Some errors occured")
    sys.exit(retval)


if __name__ == "__main__":
    main()
