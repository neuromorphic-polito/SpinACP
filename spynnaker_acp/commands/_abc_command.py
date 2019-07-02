# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class ACPAbstractCommand(object):
    __metaclass__ = ABCMeta
    DEBUG = True

    @property
    @abstractmethod
    def bytecode(self):
        pass

    @property
    @abstractmethod
    def reply_expected(self):
        pass

    @abstractmethod
    def __len__(self):
        pass
