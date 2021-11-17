from fake_super import statfmt


def assertEqual(a, b):
    if type(a) != type(b):
        raise AssertionError(
            "Assertion failed: Type mismatch %r (%s) != %r (%s)"
            % (a, type(a), b, type(b)))
    elif a != b:
        raise AssertionError(
            "Assertion failed: Value mismatch: %r (%s) != %r (%s)"
            % (a, type(a), b, type(b)))


def test_statfmt1():
    stat = {
        'mode': 0o100444, 'type': 'reg', 'perms': 0o0444,
        'major': 0, 'minor': 0, 'owner': 0, 'group': 0
    }
    assertEqual(statfmt(stat), "regular file, permissions 0444, owner 0:0")


def test_statfmt2():
    stat = {
        'mode': 0o107444, 'type': 'reg', 'perms': 0o7444,
        'major': 9, 'minor': 8, 'owner': 7, 'group': 6
    }
    assertEqual(statfmt(stat), "regular file, permissions 7444, owner 7:6")


def test_statfmt3():
    stat = {
        'mode': 0o020444, 'type': 'chr', 'perms': 0o0444,
        'major': 1, 'minor': 2, 'owner': 3, 'group': 4
    }
    assertEqual(statfmt(stat),
                "character device (1,2), permissions 0444, owner 3:4")


def test_statfmt4():
    stat = {
        'mode': 0o060444, 'type': 'blk', 'perms': 0o0444,
        'major': 1, 'minor': 2, 'owner': 3, 'group': 4
    }
    assertEqual(statfmt(stat),
                "block device (1,2), permissions 0444, owner 3:4")


def test_statfmt5():
    stat = {
        'mode': 0o040444, 'type': 'dir', 'perms': 0o0444,
        'major': 1, 'minor': 2, 'owner': 3, 'group': 4
    }
    assertEqual(statfmt(stat), "directory, permissions 0444, owner 3:4")


def test_statfmt_mismatch():
    stat = {
        'mode': 0o123456, 'type': 'chr', 'perms': 0o0444,
        'major': 1, 'minor': 2, 'owner': 3, 'group': 4
    }
    assertEqual(statfmt(stat),
                "character device (1,2), permissions 0444, owner 3:4")
