# -*- coding: utf-8 -*-
from __future__ import print_function
from ._abc_packet import ACPAbstractPacket
from ..spinnaker_interface import SDPHeader, SDPMessage, SDPFlag


class SDPPacket(object):
    SDP_ACP_PORT = 0x07

    def __init__(self, x, y, p, acp_packet):
        assert isinstance(acp_packet, ACPAbstractPacket)

        self._packet = acp_packet

        self._sdp_header = SDPHeader(
            flags=SDPFlag.REPLY_NOT_EXPECTED,
            destination_chip_x=x,
            destination_chip_y=y,
            destination_cpu=p,
            destination_port=self.__class__.SDP_ACP_PORT)

    @property
    def sdp(self):
        return SDPMessage(self._sdp_header, self._packet.bytecode)
