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
# _abc_command.py: Abstract commands for SpinACP
# ==========================================================================

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
