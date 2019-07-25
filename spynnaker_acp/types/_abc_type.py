# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import ctypes


class ACPAbstractType(object):
    __metaclass__ = ABCMeta
    DEBUG = True
    _structs_format_value = {
        (8, False): "B",
        (8, True): "b",
        (16, False): "H",
        (16, True): "h",
        (32, False): "I",
        (32, True): "i",
        (64, False): "Q",
        (64, True): "q"
    }

    _ctypes_format_value = {
        (8, False): ctypes.c_uint8,
        (8, True): ctypes.c_int8,
        (16, False): ctypes.c_uint16,
        (16, True): ctypes.c_int16,
        (32, False): ctypes.c_uint32,
        (32, True): ctypes.c_int32,
        (64, False): ctypes.c_uint64,
        (64, True): ctypes.c_int64
    }
    _ctypes_padding = None

    @property
    def padding(self):
        if self._ctypes_padding is None:
            class Padding(ctypes.LittleEndianStructure):
                _fields_ = [('p', ctypes.c_int8), ]
            self._ctypes_padding = Padding(0x0)
        return self._ctypes_padding

    @property
    @abstractmethod
    def bytecode(self):
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @value.setter
    @abstractmethod
    def value(self, v):
        pass

    @abstractmethod
    def process_message(self, message):
        pass

    @abstractmethod
    def __len__(self):
        pass
