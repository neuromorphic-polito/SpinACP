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
# _int.py: integer type for SpinACP
# ==========================================================================

# -*- coding: utf-8 -*-
import math
import ctypes
import io

from ._abc_type import ACPAbstractType


class ACPIntegerType(ACPAbstractType):
    def __init__(self, bits, sign):
        """
        TODO: This class is only a draft

        :param bits:
        :param sign:
        """
        self._bits = bits
        self._sign = sign
        self._val = self._factory()()

    def __len__(self):
        """
        Size in 32bit Word
        :return:
        """
        return int(math.ceil(ctypes.sizeof(self._val)/4.0))

    def _factory(self):
        format_value = self._ctypes_format_value[(self._bits, self._sign)]

        class Cls(ctypes.LittleEndianStructure):
            _fields_ = [('v', format_value)]

        return Cls

    @property
    def value(self):
        return self._val

    @value.setter
    def value(self, v):
        self._val.v = v

    @property
    def bytecode(self):

        # print("[TYPE] size: %d Byte" % (ctypes.sizeof(self._val)))
        # print("[TYPE] __len__: %d Word" % (self.__len__(), ))
        bytes_stream = io.BytesIO()
        bytes_stream.write(self._val)
        for _ in range(self.__len__() * 4 - ctypes.sizeof(self._val)):
            bytes_stream.write(self.padding)
        bytes_stream.flush()
        bytes_stream.seek(0)

        # format_string = ">1" + self._format_value[(32, self._sign)]
        #return struct.pack(format_string, self._val)

        return bytes_stream.read()
