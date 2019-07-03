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
# setup.py: Installation for spynnaker_acp in SpinACP
# ==========================================================================

# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='sPyNNaker-ACP',
    version='0.1.0',
    description="Spinnaker Application Command Protocol",
    packages=[
        'spynnaker_acp',
        'spynnaker_acp.types',
        'spynnaker_acp.commands',
    ],
)
