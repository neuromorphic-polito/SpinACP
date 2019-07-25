# -*- coding: utf-8 -*-
import struct
import ctypes
import io

from ._abc_type import ACPAbstractType


class ACPIntegerType(ACPAbstractType):

    def __init__(self, bits, sign):
        self._bits = bits
        self._sign = sign
        self._val = self._factory()()

    def __len__(self):
        return int(ctypes.sizeof(self._val))

    def _factory(self):
        format_value = self._ctypes_format_value[(self._bits, self._sign)]
        class Cls(ctypes.LittleEndianStructure):
            _fields_ = [('v', format_value)]
        return Cls

    @property
    def value(self):
        return self._val.v

    @value.setter
    def value(self, v):
        self._val.v = v

    @property
    def bytecode(self):
        bytes_stream = io.BytesIO()
        bytes_stream.write(self._val)
        bytes_stream.flush()
        bytes_stream.seek(0)

        return bytes_stream.read()

    def process_message(self, bytecode):
        format_value = self._structs_format_value[(self._bits, self._sign)]
        acp_payload = bytecode[16:]
        if len(acp_payload)>0:
            (v,) = struct.unpack("<1{}".format(format_value), acp_payload)
            self.value = v        
        return
