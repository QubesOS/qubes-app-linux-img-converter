#!/usr/bin/python2 -O

# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2013  Wojciech Porczyk <wojciech@porczyk.eu>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import math
import re
import cStringIO as StringIO
import subprocess
import sys

import qubes

MAX_WIDTH = 1920
MAX_HEIGHT = 1280
ICON_MAXSIZE = 512

re_imghdr = re.compile(r'^\d+ \d+\n$')

class Image(object):
    def __init__(self, path=None, rgba=None, size=(None, None)):
        self._path = path
        self._rgba = rgba
        self._size = size

    def save(self, dst):
        'dst may specify format, like png:aqq.gif'
        if self._rgba is None:
            raise NotImplementedError('Nothing to save')

        p = subprocess.Popen(['convert',
            '-depth', '8',
            '-size', '{0[0]}x{0[1]}'.format(self._size),
            'rgba:-', dst], stdin=subprocess.PIPE)
        p.stdin.write(self._rgba)
        p.stdin.close()

        if p.wait():
            raise qubes.QubesException('Conversion failed')

    def colorise(self, dst, colour):
        'dst may specify format, like png:aqq.gif'
        if self._rgba is None:
            raise NotImplementedError('Nothing to save')

        p = subprocess.Popen(['convert',
            '-depth', '8',
            '-size', '{0[0]}x{0[1]}'.format(self._size),
            'rgba:-',
            '-fill', colour,
            '-colorspace', 'gray',
            '-tint', '50',
            dst], stdin=subprocess.PIPE)
        p.stdin.write(self._rgba)
        p.stdin.close()

        if p.wait():
            raise qubes.QubesException('Colorisation failed')

    # THIS METHOD IS SENSITIVE
    @classmethod
    def get_from_stream(cls, stream, max_width=MAX_WIDTH, max_height=MAX_HEIGHT):
        maxhdrlen = int(math.ceil(math.log10(max_width)) \
            + math.ceil(math.log10(max_height)) \
            + 2)
        maxhdrlen = 256

        untrusted_header = stream.readline(maxhdrlen)
        if not re_imghdr.match(untrusted_header):
            raise qubes.QubesException('Image format violation')
        header = untrusted_header
        del untrusted_header

        untrusted_width, untrusted_height = (int(i) for i in header.rstrip().split())
        if not (0 < untrusted_width <= max_width \
                and 0 < untrusted_height <= max_height):
            raise qubes.QubesException('Image size constraint violation: width={width} height={height} max_width={max_width} max_height={max_height}'.format(width=untrusted_width, height=untrusted_height, max_width=max_width, max_height=max_height))
        width, height = untrusted_width, untrusted_height
        del untrusted_width, untrusted_height

        expected_data_len = width * height * 4    # RGBA
        untrusted_data = stream.read(expected_data_len)
        if len(untrusted_data) != expected_data_len:
            raise qubes.QubesException( \
                'Image data length violation (is {0}, should be {1})'.format( \
                len(untrusted_data), expected_data_len))
        data = untrusted_data
        del untrusted_data

        return cls(rgba=data, size=(width, height))

    @classmethod
    def get_from_vm(cls, vm, src, **kwargs):
        p = vm.run('QUBESRPC qubes.GetImageRGBA dom0', passio_popen=True)
        p.stdin.write('{0}\n'.format(src))
#       p.stdin.close()

        img = cls.get_from_stream(p.stdout, **kwargs)

        p.stdout.close()
        if p.wait():
            raise qubes.QubesException('Something went wrong with receiver')

        return img

    @classmethod
    def get_through_dvm(cls, filename, **kwargs):
        filetype = None 
        if ':' in filename:
            filetype, filename = filename.split(':', 1)[0]
            sys.stdout.write('{0}:-\n'.format(filetype))
        else:
            sys.stdout.write('-\n')

        try:
            sys.stdout.write(open(filename).read())
        except Exception, e:
            raise qubes.QubesException('Something went wrong: {0!s}'.format(e))
        finally:
            sys.stdout.close()

        return cls.get_from_stream(sys.stdin, **kwargs)
        
# vim: ft=python sw=4 ts=4 et
