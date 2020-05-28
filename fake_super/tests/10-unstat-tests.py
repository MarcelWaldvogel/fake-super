from fake_super import unstat

def assertEqual(a, b):
    if type(a) != type(b):
        raise AssertionError(
            "Assertion failed: Type mismatch %r (%s) != %r (%s)"
            % (a, type(a), b, type(b)))
    elif a != b:
        raise AssertionError(
            "Assertion failed: Value mismatch: %r (%s) != %r (%s)"
            % (a, type(a), b, type(b)))

def test_unstat1():
    assertEqual(unstat(b'100444 0,0 0:0'),
            {'mode': 0o100444, 'type': 'reg', 'perms': 0o0444,
                'major': 0, 'minor': 0,
                'owner': 0, 'group': 0})
