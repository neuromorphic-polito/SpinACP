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
# __init__.py: Initialization for spynnaker_acp in SpinACP
# ==========================================================================

# -*- coding: utf-8 -*-
from ._immediate import ACPImmediateCommand
from ._opcodes import \
    ACP_VAR_REGISTER, ACP_VAR_DEREGISTER, \
    ACP_VAR_READ, ACP_VAR_WRITE, ACP_VAR_TOGGLE
