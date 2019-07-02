# -*- coding: utf-8 -*-
from __future__ import print_function
from ..types import ACPAbstractType
from ._abc_command import ACPAbstractCommand
from ._opcodes import OpCode

import struct


class ACPVariableCommand(ACPAbstractCommand):
    """
    The ACP Variable Command
    """

    def __init__(self, op_code, var_code, offset=0, data=None):
        self._op_code = op_code
        self._var_code = var_code
        self._offset = offset
        self._data = data
        if self._data is not None and not isinstance(self._data, ACPAbstractType):
            self._data = None

    def __len__(self):
        return len(self.bytecode)

    @property
    def reply_expected(self):
        return OpCode.get_reply_expected(self._op_code)

    @property
    def offset_hex(self):
        """
        8 bit Offset (Offset in byte of the payload)
        :return:
        """
        return self._offset & 0xFF

    @property
    def var_code_hex(self):
        """
        12bit Variable code
        :return:
        """
        return self._var_code & 0xFFF

    @property
    def op_code_hex(self):
        """
        8bit Operative Code
        :return:
        """
        return OpCode.get_hex(self._op_code) & 0xFF

    @property
    def op_code_length(self):
        """
        4bit Payload length (number of 32bit word)
        :return:
        """
        l = OpCode.get_length(self._op_code)

        if l is None:
            if self._data is not None:
                l = len(self._data)
            else:
                l = 0

        if l > 0xF:
            print("[ACh] [W] The data stream is too big: %d Byte / %d Byte" % (l * 4, 0xF * 4))

        return l & 0xF

    @property
    def bytecode(self):
        """
        Bytecode string formation using struct package
        :return:
        """
        header_bits_31_28 = self.op_code_length
        header_bits_27_20 = self.op_code_hex
        header_bits_19_08 = self.var_code_hex
        header_bits_07_00 = self.offset_hex
        header_bits = header_bits_31_28 << 28 | header_bits_27_20 << 20 | header_bits_19_08 << 8 | header_bits_07_00
        header = struct.pack("<1I", header_bits)
        # print("%u" % header_bits)

        bytecode = header
        if self.op_code_length > 0:
            bytecode += self._data.bytecode

        # if self.DEBUG:
        #     bytecode_hex = ":".join("{:02x}".format(ord(c)) for c in bytecode)
        #     print("[ACh] %s %u" % (bytecode_hex, header_bits))

        return bytecode
