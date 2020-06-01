import errno

from mock import patch, call
from nose.tools import raises

import fake_super


def assertSimilar(a, b):
    """Helpful-output version of `assert a == b`"""
    if a != b:
        raise AssertionError("Assertion failed:"
                             " Value mismatch: %r (%s) != %r (%s)"
                             % (a, type(a), b, type(b)))


@raises(SystemExit)
def test_empty():
    fake_super.main()


@raises(SystemExit)
def test_help():
    fake_super.main(['--help'])


@patch('builtins.print')
@patch('fake_super.xattr')
def test_query(mock_xattr, mock_print):
    mock_xattr.getxattr.return_value = b'100644 0,0 1000:1000'
    fake_super.main(['README.md'])
    expected = 'README.md: regular file, permissions 0644, owner 1000:1000'
    assertSimilar(mock_print.mock_calls, [call(expected)])


@patch('fake_super.os')
@patch('fake_super.xattr')
def test_restore(mock_xattr, mock_os):
    mock_xattr.getxattr.return_value = b'010644 0,0 3:4'
    mock_os.makedev.return_value = 0
    fake_super.main(['--quiet', '--restore', '/dev/something'])
    expected = [call.makedev(0, 0),
                call.mknod('/dev/something', 0o10644, device=0),
                call.chown('/dev/something', 3, 4)]
    assertSimilar(mock_os.mock_calls, expected)


@patch('fake_super.xattr')
def test_noattr(mock_xattr):
    mock_xattr.getxattr.side_effect = OSError(errno.ENODATA,
                                              "No such attribute")
    retval = fake_super.main(['--quiet', '--restore', '/dev/something'])
    assertSimilar(retval, 1)


@patch('fake_super.xattr')
@raises(SystemExit)
def test_nofile(mock_xattr):
    mock_xattr.getxattr.side_effect = OSError(errno.ENOENT,
                                              "No such file or directory")
    fake_super.main(['--quiet', '--restore', '/dev/something'])
