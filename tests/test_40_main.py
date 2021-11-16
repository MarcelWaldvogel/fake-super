from pathlib import Path
import errno

from mock import patch, call
from pytest import raises

import fake_super


def assertSimilar(a, b):
    """Helpful-output version of `assert a == b`"""
    if a != b:
        raise AssertionError("Assertion failed:"
                             " Value mismatch: %r (%s) != %r (%s)"
                             % (a, type(a), b, type(b)))


def test_empty():
    # Also outputs "error: the following arguments are required: files"
    with raises(SystemExit, match=r'2'):
        fake_super.main()


def test_help():
    # Also outputs
    # "usage: nosetests3 [-h] [--version] [--restore] [--quiet]
    #     files [files ...]"
    with raises(SystemExit, match=r'0'):
        fake_super.main(['--help'])


@patch('builtins.print')
@patch('fake_super.os.getxattr')
def test_query(mock_getxattr, mock_print):
    mock_getxattr.return_value = b'100644 0,0 1000:1000'
    fake_super.main(['README.md'])
    expected = 'README.md: regular file, permissions 0644, owner 1000:1000'
    assertSimilar(mock_print.mock_calls, [call(expected)])


@patch('fake_super.secrets')
@patch('fake_super.os.rename')
@patch('fake_super.os.mknod')
@patch('fake_super.os.lchown')
@patch('fake_super.os.getxattr')
def test_restore(mock_getxattr, mock_lchown, mock_mknod, mock_rename,
                 mock_secrets):
    mock_getxattr.return_value = b'010644 0,0 3:4'
    mock_secrets.token_urlsafe.return_value = '999999'
    fake_super.main(['--quiet', '--restore', '/dev/something1'])
    mock_mknod.assert_called_with(Path('/dev/.something1.999999'),
                                  0o10644, device=0)
    mock_lchown.assert_called_with(Path('/dev/.something1.999999'), 3, 4)
    mock_rename.assert_called_with(Path('/dev/.something1.999999'),
                                   '/dev/something1')


@patch('fake_super.os.getxattr')
def test_noattr(mock_getxattr):
    # also outputs
    # "dev/something2: Missing `user.rsync.%stat` attribute, skipping"
    mock_getxattr.side_effect = OSError(errno.ENODATA,
                                        "No such attribute")
    retval = fake_super.main(['--quiet', '--restore', '/dev/something2'])
    assertSimilar(retval, 1)


@patch('fake_super.os.getxattr')
def test_noattr2(mock_getxattr):
    # also outputs
    # "dev/something5: Missing `user.rsync.%stat` attribute, skipping"
    # "dev/something5: Missing `user.rsync.%stat` attribute, skipping"
    mock_getxattr.side_effect = OSError(errno.ENODATA,
                                        "No such attribute")
    with raises(SystemExit, match=r'Some errors occured'):
        fake_super.main(
            ['--quiet', '--restore', '/dev/something5', '/dev/something6'])


@patch('fake_super.os.getxattr')
def test_nofile(mock_getxattr):
    mock_getxattr.side_effect = OSError(
        errno.ENOENT, "No such file or directory")
    with raises(SystemExit,
                match=r'^/dev/something3: No such file or directory'):
        fake_super.main(['--quiet', '--restore', '/dev/something3'])


@patch('fake_super.os.getxattr')
def test_bad_xattr(mock_getxattr):
    mock_getxattr.return_value = b'1 2 3'
    with raises(SystemExit, match=r'^/dev/something4: Illegal stat info'):
        fake_super.main(['--quiet', '--restore', '/dev/something4'])
