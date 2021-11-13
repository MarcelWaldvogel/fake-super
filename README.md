# Fake-super — A tool to save/restore `rsync --fake-super` attributes

[![pipeline status](https://gitlab.com/MarcelWaldvogel/fake-super/badges/main/pipeline.svg)](https://gitlab.com/MarcelWaldvogel/fake-super/-/commits/main)
[![coverage report](https://gitlab.com/MarcelWaldvogel/fake-super/badges/main/coverage.svg)](https://gitlab.com/MarcelWaldvogel/fake-super/-/commits/main)

[`--fake-super`](https://download.samba.org/pub/rsync/rsync.html) is one of the
coolest options of the [`rsync`](https://rsync.samba.org/) remote file
synchronization tool. It is especially useful when sending system-level backups
to a remote backup server, on which the backup client should not have system
(`root`) permission, but

* permissions (including setuid/setgid bits),
* information about owners and groups,
* access control lists (ACLs), or
* special files, i.e.
  - symbolic links,
  - character/block devices,
  - Unix domain sockets, and
  - FIFOs/named pipes

on the origin system should be accurately preserved. Such a backup setup is
especially useful when trying to prevent against the backup being tampered or
destroyed maliciously, such as an intruder or ransomware.

When restoring back to the origin system, everything is fine. However, if —
e.g. in the case of disaster recovery — the backup system is to be used as a
replacement for the origin system, all the above information are lacking.

`fake-super` allows you to restore the attributes from the `user.rsync.*`
extended attributes, where `rsync --fake-super` stores the information, back to
the real information.

## Extended attribute format

### `user.rsync.%stat`

A single line (without EOL) with the following space-separated fields:

* **mode** (octal) as specified in
  [`inode(7)`](http://manpages.ubuntu.com/manpages/focal/man7/inode.7.html)
* **device** information as a comma-separated tuple of major, minor IDs. Block
  and character devices are differentiated by the `S_IFMT` bits in the mode
  above.
* **ownership** information as a colon-separated tuple of numeric user and
  group IDs.

An example for a plain file with mode `rw-rw-r--`:
```
100664 0,0 1000:1000
^^ S_IFMT information (S_IFREG, regular file)
  ^ Setuid/setgid/sticky bits
   ^^^ regular permission bits
       ^^^ Device ID (0, not used for regular files)
           ^^^ UID/GID of the original file (user/group 1000)
```

`/dev/null` from Linux would be annotated as follows:
```
060666 1,3 0:0
^^ S_IFBLK, block device
   ^^^ R/W for everyone
       ^^^ Device ID 1,3
           ^^^ Belonging to root
```

# Security considerations

1. Using this program grants the unprivileged creator of the original files
   posthumously essentially the same rights as a process running as `root`
   would have had.  

   **:warning: Only run this program if you trust the creator of the files
   ultimately and can be sure the files have not been tampered with.**

2. Specifying `user` or `group` as -1 (or anything that equals to -1 when cast
   to a `uid_t` or `gid_t`, depending on your OS this could be any multiple of
   65536 (2^16) or 4294967296 (2^32) minus 1) will leave the owner or group
   unchanged. This is a limitation of the
   [`chown()`](http://manpages.ubuntu.com/manpages/bionic/man2/chown.2.html)
   system call. Under some circumstances, this could also be turned into a
   [security problem](https://www.sudo.ws/alerts/minus_1_uid.html), but as you
   have to trust the creator of the files fully anyway (see item 1 above), this
   probably does not make a difference in most use cases.
