from pathlib import Path
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


@patch('fake_super.secrets')
@patch('fake_super.os.rename')
@patch('fake_super.os.mknod')
@patch('fake_super.os.chown')
@patch('fake_super.xattr')
def test_restore(mock_xattr, mock_chown, mock_mknod, mock_rename,
                 mock_secrets):
    mock_xattr.getxattr.return_value = b'010644 0,0 3:4'
    mock_secrets.token_urlsafe.return_value = '999999'
    fake_super.main(['--quiet', '--restore', '/dev/something'])
    mock_mknod.assert_called_with(Path('/dev/.something.999999'),
                                  0o10644, device=0)
    mock_chown.assert_called_with(Path('/dev/.something.999999'), 3, 4)
    mock_rename.assert_called_with(Path('/dev/.something.999999'),
                                   '/dev/something')


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
