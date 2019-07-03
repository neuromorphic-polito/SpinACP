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
# _packet.py: packet formation for SpinACP
# ==========================================================================

# -*- coding: utf-8 -*-
from __future__ import print_function
import spinnman.messages.sdp.sdp_header
import spinnman.messages.sdp.sdp_message
import spinnman.messages.sdp.sdp_flag


class ACPPacket(object):
    SDP_PORT = 0x7

    def __init__(self, x, y, p, command):
        self._command = command
        flags = spinnman.messages.sdp.sdp_flag.SDPFlag.REPLY_NOT_EXPECTED
        if self._command.reply_expected:
            flags = spinnman.messages.sdp.sdp_flag.SDPFlag.REPLY_EXPECTED
        self._sdp_header = spinnman.messages.sdp.sdp_header.SDPHeader(
            flags=flags,
            destination_chip_x=x,
            destination_chip_y=y,
            destination_cpu=p,
            destination_port=ACPPacket.SDP_PORT)

    @property
    def sdp(self):
        return spinnman.messages.sdp.sdp_message.SDPMessage(
            self._sdp_header, self._command.bytecode)
