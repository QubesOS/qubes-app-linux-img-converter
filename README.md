Qubes Image Converter
====================

Qubes Image converter is a [Qubes](https://qubes-os.org) Application that
utilizes Disposable VMs and Qubes' flexible qrexec (inter-VM communication)
infrastructure to securely convert potentially untrusted image into a
safe-to-view image.

This is done by having a Disposable VM parse the image into a very simple
representation (RGB bitmap) that (presumably) leaves no room for malicious
code. This representation is then sent back to the client AppVM which then
constructs an entirely new image out of the received bitmaps.

Usage
------

    [user@domU ~]$ qvm-convert-img src.png dest.png
