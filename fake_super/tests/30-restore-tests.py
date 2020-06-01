import errno
import os
import stat

from mock import patch, call
from nose.tools import raises

import fake_super


def assertSimilar(a, b):
    if a != b:
        raise AssertionError("Assertion failed:"
                             " Value mismatch: %r (%s) != %r (%s)"
                             % (a, type(a), b, type(b)))


@patch('fake_super.os')
def test_restore_chr(mock_os):
    mock_os.makedev.return_value = os.makedev(10, 20)
    fake_super.restore('/file/name',
                       {
                           'type': 'chr',
                           'mode': stat.S_IFCHR | 0o444,
                           'major': 10,
                           'minor': 20,
                           'owner': 123,
                           'group': 456
                       })
    assertSimilar(mock_os.mock_calls,
                  [
                      call.makedev(10, 20),
                      call.mknod('/file/name',
                                 stat.S_IFCHR | 0o444, device=0xa14),
                      call.chown('/file/name', 123, 456)
                  ])


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
