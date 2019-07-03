# ==========================================================================
#                                  SpinACP
# ==========================================================================
# This file is part of SpinACP.
#
# SpinACP is Free Software: you can redistribute it and/or modify it
# under the terms found in the LICENSE[.md|.rst] file distributed
# together with this file.
#
# SpinACP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# ==========================================================================
# Author: Francesco Barchi <francesco.barchi@polito.it>
# ==========================================================================
# _helper.py: version get/set helper for SpinACP
# ==========================================================================

# -*- coding: utf-8 -*-
import struct


class ACPHelper(object):
    @classmethod
    def version2word(cls, s):
        y, w = s.split('w')
        w, r = w.split('r')
        y = int(y) & 0xFFF
        w = int(w) & 0xFFF
        r = int(r) & 0xFF

        word_byte = y << 20 | w << 8 | r

        return struct.pack(">1I", word_byte)

    @classmethod
    def word2version(cls, word_str):
        word_byte = struct.unpack(">1I", word_str)[0]

        y = (word_byte & 0xFFF00000) >> 20
        w = (word_byte & 0xFFF00) >> 8
        r = (word_byte & 0xFF)

        return "%02dw%02dr%02d" % (y, w, r)
