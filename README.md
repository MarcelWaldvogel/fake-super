# Fake-super — A tool to save/restore `rsync --fake-super` attributes

[`--fake-super`](https://download.samba.org/pub/rsync/rsync.html) is one of the
coolest options of the [`rsync`](https://rsync.samba.org/) remote file
synchronization tool. It is especially useful when sending system-level backups
to a remote backup server, on which the backup client should not have system
(`root`) permission, but

* permissions (including setuid/setgid bits),
* information about owners and groups,
* access control lists (ACLs), or
* special files, i.e.
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
