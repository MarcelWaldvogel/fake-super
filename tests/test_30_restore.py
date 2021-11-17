import errno
from pathlib import Path
import stat

from mock import patch, call, mock_open
from pytest import raises

import fake_super


def assertSimilar(a, b):
    if a != b:
        raise AssertionError("Assertion failed:"
                             " Value mismatch: %r (%s) != %r (%s)"
                             % (a, type(a), b, type(b)))


@patch('fake_super.secrets')
@patch('fake_super.os.rename')
@patch('fake_super.os.mknod')
@patch('fake_super.os.lchown')
def test_restore_chr(mock_lchown, mock_mknod, mock_rename, mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    fake_super.restore('name',
                       {
                           'type': 'chr',
                           'mode': stat.S_IFCHR | 0o444,
                           'major': 10,
                           'minor': 20,
                           'owner': 123,
                           'group': 456
                       })
    mock_mknod.assert_called_with(
        Path('.name.999999'), stat.S_IFCHR | 0o444, device=0xa14)
    mock_lchown.assert_called_with(Path('.name.999999'), 123, 456)
    mock_rename.assert_called_with(Path('.name.999999'), 'name')


@patch('fake_super.secrets')
@patch('fake_super.os')
def test_restore_chr2(mock_os, mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    mock_os.mknod.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'mknod: Permission denied'):
        fake_super.restore('name',
                           {
                               'type': 'chr',
                               'mode': stat.S_IFCHR | 0o444,
                               'major': 10,
                               'minor': 20,
                               'owner': 123,
                               'group': 456
                           })


@patch('fake_super.secrets')
@patch('fake_super.os')
def test_restore_chr3(mock_os, mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    mock_os.rename.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'rename.*: Permission denied'):
        fake_super.restore('name',
                           {
                               'type': 'chr',
                               'mode': stat.S_IFCHR | 0o444,
                               'major': 10,
                               'minor': 20,
                               'owner': 123,
                               'group': 456
                           })


@patch('fake_super.secrets')
@patch('fake_super.os.rename')
@patch('fake_super.os.symlink')
@patch('fake_super.os.lchown')
@patch('builtins.open', new_callable=mock_open, read_data='../some/path')
def test_restore_lnk(mock_file, mock_lchown, mock_symlink, mock_rename,
                     mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    fake_super.restore('name',
                       {
                           'type': 'lnk',
                           'mode': stat.S_IFCHR | 0o444,
                           'major': 10,
                           'minor': 20,
                           'owner': 123,
                           'group': 456
                       })
    mock_file.assert_called_with('name', 'r')
    mock_symlink.assert_called_with('../some/path', Path('.name.999999'))
    mock_lchown.assert_called_with(Path('.name.999999'), 123, 456)
    mock_rename.assert_called_with(Path('.name.999999'), 'name')


@patch('fake_super.secrets')
@patch('fake_super.os')
@patch('builtins.open', new_callable=mock_open, read_data='../some/path')
def test_restore_lnk2(mock_file, mock_os, mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    mock_os.symlink.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'symlink: Permission denied'):
        fake_super.restore('name',
                           {
                               'type': 'lnk',
                               'mode': stat.S_IFLNK | 0o444,
                               'major': 0,
                               'minor': 0,
                               'owner': 123,
                               'group': 456
                           })


@patch('fake_super.secrets')
@patch('fake_super.os')
@patch('builtins.open')
def test_restore_lnk3(mock_file, mock_os, mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    mock_file.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'name: open/read: Permission denied'):
        fake_super.restore('name',
                           {
                               'type': 'lnk',
                               'mode': stat.S_IFLNK | 0o444,
                               'major': 0,
                               'minor': 0,
                               'owner': 123,
                               'group': 456
                           })


@patch('fake_super.secrets')
@patch('fake_super.os')
@patch('builtins.open', new_callable=mock_open, read_data='../some/path')
def test_restore_lnk4(mock_file, mock_os, mock_secrets):
    mock_secrets.token_urlsafe.return_value = '999999'
    mock_os.rename.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'rename.*: Permission denied'):
        fake_super.restore('name',
                           {
                               'type': 'lnk',
                               'mode': stat.S_IFLNK | 0o444,
                               'major': 0,
                               'minor': 0,
                               'owner': 123,
                               'group': 456
                           })
    mock_file.assert_called_with('name', 'r')
    # The PosixPath argument is mangled by pytest
    assert mock_os.symlink.call_args.args[0] == '../some/path'
    assert mock_os.lchown.call_args.args[1:] == (123, 456)


@patch('fake_super.os')
def test_restore_reg(mock_os):
    fake_super.restore('/file/name',
                       {
                           'type': 'reg',
                           'perms': 0o4444,
                           'owner': 123,
                           'group': 456
                       })
    assertSimilar(mock_os.mock_calls,
                  [
                      call.lchown('/file/name', 123, 456),
                      call.chmod('/file/name', 0o4444)
                  ])


@patch('fake_super.os')
def test_restore_reg2(mock_os):
    mock_os.chmod.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'^/dir/name: chmod: Permission denied'):
        fake_super.restore('/dir/name',
                           {
                               'type': 'dir',
                               'perms': 0o4444,
                               'owner': 123,
                               'group': 456
                           })


def test_restore_unknown():
    with raises(SystemExit,
                match=r"^/file/name: Don't know how to create whiteout entry"):
        fake_super.restore('/file/name',
                           {
                               'type': 'wht',
                               'perms': 0o4444,
                               'owner': 123,
                               'group': 456
                           })


@patch('fake_super.os')
def test_restore_key(mock_os):
    with raises(KeyError, match=r"^'perms'$"):
        fake_super.restore('/file/name',
                           {
                               'type': 'reg',
                               'mode': 0o4444,
                               'owner': 123,
                               'group': 456
                           })


@patch('fake_super.os')
def test_restore_fail(mock_os):
    mock_os.lchown.side_effect = OSError(errno.EPERM, "Permission denied")
    with raises(SystemExit, match=r'^/file/name: chown: Permission denied'):
        fake_super.restore('/file/name',
                           {
                               'type': 'reg',
                               'perms': 0o4444,
                               'owner': 123,
                               'group': 456
                           })
