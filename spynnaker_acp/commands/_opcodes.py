# -*- coding: utf-8 -*-

ACP_VAR_REGISTER = 0
ACP_VAR_DEREGISTER = 1
ACP_VAR_READ = 2
ACP_VAR_WRITE = 3
ACP_VAR_TOGGLE = 4


class OpCode(object):
    _op_code_db = {
        ACP_VAR_REGISTER:
            {'hex': 0xFB, 'length': None, 'reply': False},
        ACP_VAR_DEREGISTER:
            {'hex': 0xBF, 'length': None, 'reply': False},
        ACP_VAR_READ:
            {'hex': 0xF0, 'length': None, 'reply': True},
        ACP_VAR_WRITE:
            {'hex': 0xF1, 'length': None, 'reply': False},
        ACP_VAR_TOGGLE:
            {'hex': 0xF2, 'length': 0, 'reply': False}
    }

    class ExceptionOpCode(Exception):
        pass

    @classmethod
    def get_hex(cls, code):
        if code not in cls._op_code_db:
            raise cls.ExceptionOpCode
        return cls._op_code_db[code]['hex']

    @classmethod
    def get_length(cls, code):
        if code not in cls._op_code_db:
            raise cls.ExceptionOpCode
        return cls._op_code_db[code]['length']

    @classmethod
    def get_reply_expected(cls, code):
        if code not in cls._op_code_db:
            raise cls.ExceptionOpCode
        return cls._op_code_db[code]['reply']
