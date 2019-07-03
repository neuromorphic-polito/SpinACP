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
# _runtime.py: Runtime management for SpinACP
# ==========================================================================

# -*- coding: utf-8 -*-
from __future__ import print_function
from spinnman.connections.connection_listener import ConnectionListener
import struct
import threading


class ACPRuntime(object):
    IP_TAG = 7

    def __init__(self, transceiver, connection, start=False):
        self._transceiver = transceiver
        self._connection = connection
        self._start = start

        self._stop_event = threading.Event()

        self._listener = ConnectionListener(self._connection)
        self._listener.add_callback(self._get_callback())
        self._reactions = dict()
        if self._start:
            self._listener.start()

    def add_reaction(self, acp_cmd, acp_var, callback):
        k = (acp_cmd, acp_var)
        if k not in self._reactions:
            self._reactions[k] = callback
        return

    def start(self):
        if not self._start:
            self._listener.start()
            self._start = True
        return

    def stop(self):
        if self._start:
            self._listener.close()
            self._listener.join(1)

    def wait(self):
        self._stop_event.wait()

    def signal(self):
        self._stop_event.set()

    def _get_callback(self):
        def _callback(msg):
            cls = self
            # print("[ACP-RUNTIME] Received a SDP!")

            # Get reaction key
            try:
                reaction = cls._message2reaction(msg)
                if reaction in cls._reactions:
                    print("[ACP-RUNTIME] Reaction: (%04x:%04x)" % (reaction[0], reaction[1]))
                    cls._reactions[reaction]()
            except Exception as e:
                print("Error!", e)

        return _callback

    @classmethod
    def _message2reaction(cls, msg):
        bytecode = msg.data[2:]
        bytecode_hex = ":".join("{:02x}".format(ord(c)) for c in bytecode)
        # print("[ACP-RUNTIME] %s" % bytecode_hex)

        flags, ip_tag, dst_port, src_port, dest_x, dest_y, src_x, src_y, \
        acp_cmd, acp_var, acp_length, acp_value = \
            struct.unpack("<8B2H2I", bytecode)

        # print("[ACP-RUNTIME] SDP Fields")
        # print("\tflag: %02x" % (flags,))
        # print("\tip-tag: %02x" % (ip_tag,))
        # print("\tdst_port: %02x" % (dst_port,))
        # print("\tsrc_port: %02x" % (src_port,))
        # print("\tdest_x: %02x" % (dest_x,))
        # print("\tdest_y: %02x" % (dest_y,))
        # print("\tsrc_x: %02x" % (src_x,))
        # print("\tsrc_y: %02x" % (src_y,))
        #
        # print("[ACP-RUNTIME] SCP/ACP Fields")
        # print("\tacp_cmd: %04x" % (acp_cmd,))
        # print("\tacp_var: %04x" % (acp_var,))
        # print("\tacp_length: %08x" % (acp_length,))
        # print("\tacp_value: %08x" % (acp_value,))

        return acp_cmd, acp_var
