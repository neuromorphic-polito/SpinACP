# -*- coding: utf-8 -*-

ACP_COMMAND_VERSION = 0x00
ACP_COMMAND_VERSION_REPLY = 0xFF

ACP_COMMAND_ME_CREATE = 0x01
ACP_COMMAND_ME_READ = 0x02
ACP_COMMAND_ME_UPDATE = 0x03
ACP_COMMAND_ME_DELETE = 0x04

ACP_COMMAND_ME_READ_REPLY = 0xF2

ACP_COMMAND_SYN = 0x0F
ACP_COMMAND_ACK = 0x0B


class ExceptionOpCode(Exception):
    pass


class BuiltinCommands(object):
    _op_code_db = {
        ACP_COMMAND_ME_CREATE:
            {'length': None},
        ACP_COMMAND_ME_READ:
            {'length': None},
        ACP_COMMAND_ME_UPDATE:
            {'length': None},
        ACP_COMMAND_ME_DELETE:
            {'length': None},
    }

    @classmethod
    def get_hex(cls, code):
        if code not in cls._op_code_db:
            raise cls.ExceptionOpCode
        return code

    @classmethod
    def get_length(cls, code):
        if code not in cls._op_code_db:
            raise cls.ExceptionOpCode
        return cls._op_code_db[code]['length']
