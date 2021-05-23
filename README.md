Qubes Image Converter
====================

Qubes Image Converter is a [Qubes OS](https://qubes-os.org) application that
uses DisposableVMs and Qubes' flexible qrexec (inter-VM communication)
infrastructure to securely convert untrusted image into a
safe-to-view image.

This is done by using a DisposableVM to parse the image into a very simple
representation (RGBA) that (presumably) leaves no room for malicious
code. This representation is then sent back to the client qube which then
constructs an entirely new image out of the received bitmaps.

Usage
------

    [user@domU ~]$ qvm-convert-img src.png dest.png
