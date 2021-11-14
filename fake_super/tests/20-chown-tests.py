import errno

from mock import patch
from nose.tools import raises

import fake_super


@patch('fake_super.os')
def test_chown1(mock_os):
    fake_super.chown('/file/name', {'owner': 123, 'group': 456})
    mock_os.lchown.assert_called_with('/file/name', 123, 456)


@patch('fake_super.os')
@raises(SystemExit)
def test_chown2(mock_os):
    mock_os.lchown.side_effect = OSError(errno.EPERM, "Permission denied")
    fake_super.chown('/file/name', {'owner': 123, 'group': 456})


@patch('fake_super.os')
@raises(SystemExit)
def test_chown3(mock_os):
    mock_os.lchown.side_effect = OSError(errno.EPERM, "Permission denied")
    fake_super.chown('/file/name', {'owner': 123, 'group': 456}, True)
    mock_os.unlink.assert_called_with('/file/name')
