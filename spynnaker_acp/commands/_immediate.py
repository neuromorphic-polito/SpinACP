# -*- coding: utf-8 -*-
from __future__ import print_function
from ._abc_command import ACPAbstractCommand
from ._command import ACPVariableCommand

import struct


class ACPImmediateCommand(ACPAbstractCommand):
    """
    The ACP Immediate Command
    """
    SCP_CODE = 0xF1

    def __init__(self, op_code, var_code, offset=0, data=None):
        """
        By default create a Variable Command
        :param op_code:
        :param var_code:
        :param offset:
        :param data:
        """
        self._command = ACPVariableCommand(op_code, var_code, offset, data)

    def __len__(self):
        return len(self.bytecode)

    @property
    def reply_expected(self):
        """
        The reply is expected depends on Variable Command
        :return:
        """
        return self._command.reply_expected

    @property
    def bytecode(self):
        """
        Create the bytecode string with struct module
        :return:
        """
        header = struct.pack("<2H", self.SCP_CODE, 0)

        bytecode = header
        bytecode += self._command.bytecode

        # if self.DEBUG:
        #     bytecode_hex = ":".join("{:02x}".format(ord(c)) for c in bytecode)
        #     print("[SCP/ACP] %s" % bytecode_hex)

        return bytecode
