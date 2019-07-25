# -*- coding: utf-8 -*-
from __future__ import print_function
from ._acp_packet import ACPPacket
from ._builtin_commands import BuiltinCommands


class ACPPacketME(ACPPacket):
    """
    The ACP Variable Command
    """

    def __init__(self, me_command, me_id, packet_number, payload):
        super(ACPPacketME, self).__init__(me_command, packet_number, me_id & 0xFFFF, payload)
