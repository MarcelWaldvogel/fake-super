from nose.tools import raises

from fake_super import unstat, StatFormatError


def assertEqual(a, b):
    if type(a) != type(b):
        raise AssertionError(
            "Assertion failed: Type mismatch %r (%s) != %r (%s)"
            % (a, type(a), b, type(b)))
    elif a != b:
        raise AssertionError(
            "Assertion failed: Value mismatch: %r (%s) != %r (%s)"
            % (a, type(a), b, type(b)))


def test_unstat1_positive1():
    assertEqual(unstat(b'100444 0,0 0:0'), {
                'mode': 0o100444, 'type': 'reg', 'perms': 0o0444,
                'major': 0, 'minor': 0,
                'owner': 0, 'group': 0
                })


def test_unstat1_positive2():
    assertEqual(unstat(b'060123 4,5 6:7'), {
                'mode': 0o060123, 'type': 'blk', 'perms': 0o0123,
                'major': 4, 'minor': 5,
                'owner': 6, 'group': 7
                })


@raises(StatFormatError)
def test_unstat1_length():
    unstat(b'000 0,0 0:0')


@raises(StatFormatError)
def test_unstat1_illegal_number1():
    unstat(b'000009 0,0 0:0')


@raises(StatFormatError)
def test_unstat1_illegal_number2():
    unstat(b'0x0000 0,0 0:0')


@raises(StatFormatError)
def test_unstat1_illegal_number3():
    unstat(b'0o0000 0,0 0:0')


@raises(StatFormatError)
def test_unstat1_illegal_type():
    unstat(b'030000 0,0 0:0')


@raises(StatFormatError)
def test_unstat2_illegal_major():
    unstat(b'040444 1,0 0:0')


@raises(StatFormatError)
def test_unstat2_illegal_major_num():
    unstat(b'060444 X,0 0:0')


@raises(StatFormatError)
def test_unstat3_illegal_minor():
    unstat(b'040444 0,1 0:0')


@raises(StatFormatError)
def test_unstat4_2parts():
    unstat(b'040444 0,1')


@raises(StatFormatError)
def test_unstat5_4parts():
    unstat(b'040444 0,1 0:0 0')


@raises(StatFormatError)
def test_unstat5_newline():
    unstat(b'040444 0,1 0:0\n')


@raises(StatFormatError)
def test_unstat6_major_minor_rev():
    unstat(b'020444 0,1,2 0:0')


@raises(StatFormatError)
def test_unstat7_user_group_other():
    unstat(b'020444 0,1 0:0:0')


@raises(StatFormatError)
def test_unstat8_decimal():
    unstat(b'020444 0,1 0.0:0')
