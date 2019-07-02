# -*- coding: utf-8 -*-
import math
import ctypes
import io

from ._abc_type import ACPAbstractType


class ACPStructVersionType(ACPAbstractType):
    def __init__(self, year, week, revision):
        """
        TODO: This class is only a draft
        """
        self._val = self._factory()()
        self._val.y = year
        self._val.w = week
        self._val.r = revision

    def __len__(self):
        return int(math.ceil(ctypes.sizeof(self._val)/4))

    def _factory(self):
        class Cls(ctypes.LittleEndianStructure):
            _fields_ = [('y', ctypes.c_uint16,
                         'w', ctypes.c_uint16,
                         'r', ctypes.c_uint8)]
        return Cls

    @property
    def value(self):
        return "%02dw%02dr%02r" % (self._val.y, self._val.w, self._val.r)

    @value.setter
    def value(self, s):
        y, w = s.split("w")
        w, r = w.split("r")
        self._val.y = int(y)
        self._val.w = int(w)
        self._val.r = int(r)

    @property
    def bytecode(self):
        # print("[TYPE] size: %d" % (ctypes.sizeof(self._val)))
        bytes_stream = io.BytesIO()
        bytes_stream.write(self._val)
        bytes_stream.flush()
        bytes_stream.seek(0)

        # format_string = ">1" + self._format_value[(32, self._sign)]
        #return struct.pack(format_string, self._val)

        return bytes_stream.read()
