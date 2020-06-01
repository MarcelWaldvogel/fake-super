import errno
from pathlib import Path
import stat

from mock import patch, call
from nose.tools import raises

import fake_super


def assertSimilar(a, b):
    if a != b:
        raise AssertionError("Assertion failed:"
                             " Value mismatch: %r (%s) != %r (%s)"
                             % (a, type(a), b, type(b)))


@patch('fake_super.secrets')
@patch('fake_super.os.rename')
@patch('fake_super.os.mknod')
@patch('fake_super.os.chown')
def test_restore_chr(mock_chown, mock_mknod, mock_rename, mock_secrets):
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
    mock_mknod.assert_called_with(Path('.name.999999'),
                                  stat.S_IFCHR | 0o444, device=0xa14)
    mock_chown.assert_called_with(Path('.name.999999'), 123, 456)
    mock_rename.assert_called_with(Path('.name.999999'),
                                   'name')


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
                      call.chown('/file/name', 123, 456),
                      call.chmod('/file/name', 0o4444)
                  ])


@patch('fake_super.os')
@raises(KeyError)
def test_restore_key(mock_os):
    fake_super.restore('/file/name',
                       {
                           'type': 'reg',
                           'mode': 0o4444,
                           'owner': 123,
                           'group': 456
                       })


@patch('fake_super.os')
@raises(SystemExit)
def test_restore_fail(mock_os):
    mock_os.chown.side_effect = OSError(errno.EPERM, "Permission denied")
    fake_super.restore('/file/name',
                       {
                           'type': 'reg',
                           'perms': 0o4444,
                           'owner': 123,
                           'group': 456
                       })
