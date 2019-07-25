# -*- coding: utf-8 -*-
from __future__ import print_function
from ._abc_packet import ACPAbstractPacket

import struct


class ACPPacket(ACPAbstractPacket):
    PAYLOAD_MAX = 264
    
    def __init__(self, command, packet_number, header, payload):

        if payload is not None:
            assert isinstance(payload, str)

        self._command = command
        self._packet_number = packet_number
        self._header = header
        self._payload = payload

        self._bytecode = None

    @property
    def payload_length(self):
        if self._payload is None:
            return 0

        l = len(self._payload)
        if l > ACPPacket.PAYLOAD_MAX:
            print("[ACPVariableCommand] [Warning]")
            print("  The data stream is too big: %d Byte / %d Byte" % (l, ACPPacket.PAYLOAD_MAX))
            l = ACPPacket.PAYLOAD_MAX

        return l

    @property
    def bytecode(self):
        if self._bytecode is None:
            cmd = self._command
            seq = self.payload_length
            arg1 = self._header

            self._bytecode = struct.pack("<2H1I", cmd, seq, arg1)
            if self._payload is not None:
                self._bytecode += self._payload

        return self._bytecode
