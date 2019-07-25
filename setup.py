# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='spynnaker_acp',
    version='0.1.3',
    description="Spinnaker Application Command Protocol",
    packages=[
        'spynnaker_acp',
        'spynnaker_acp.types',
        'spynnaker_acp.commands',
    ],
)
