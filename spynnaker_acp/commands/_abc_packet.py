# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class ACPAbstractPacket(object):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def bytecode(self):
        pass

    def __len__(self):
        return len(self.bytecode)
