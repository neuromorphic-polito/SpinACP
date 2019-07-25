from __future__ import print_function
import threading

from .types import ACPAbstractType
from .commands import SDPPacket
from .commands import ACPPacket
from .commands import ACPPacketME
from .commands import ACP_COMMAND_ME_UPDATE, \
                      ACP_COMMAND_ME_READ, \
                      ACP_COMMAND_ME_READ_REPLY, \
                      ACP_COMMAND_SYN, \
                      ACP_COMMAND_ACK


class ReadReply:
    def __init__(self, payload, verbose=False):
        self._payload = payload
        self._verbose = verbose
        self._stop_event = threading.Event()
    
    def get_callback(self):
        def callback(msg):
            if self._verbose:
                print("[ACP-ME] Read Reply Received!")
            self._payload.process_message(msg)
            self._stop_event.set()
        return callback
    
    def wait(self):
        if self._verbose:
            print("[ACP-ME] Read Reply Wait..")
        self._stop_event.wait()
        self._stop_event.clear()
        if self._verbose:
            print("[ACP-ME] Read Reply Done!")
        return


class SynAck:
    def __init__(self, runtime, verbose=False):
        self._runtime = runtime
        self._verbose = verbose
        self._stop_event = threading.Event()
        
    def get_callback(self):
        def callback(msg):
            if self._verbose:
                print("[ACP-ME] Ack Received!")
            self._stop_event.set()
        return callback
    
    def syn(self, x, y, p):
        if self._verbose:
            print("[ACP-ME] Send Sync..")
        acp_packet = ACPPacket(ACP_COMMAND_SYN, 0, 0, None)
        syn_packet = SDPPacket(x, y, p, acp_packet)
        self._runtime.send_sdp(syn_packet.sdp)
        if self._verbose:
            print("[ACP-ME] Send Sync Done!")
        
        if self._verbose:
            print("[ACP-ME] Wait for Ack..")
        self._stop_event.wait()
        self._stop_event.clear()
        if self._verbose:
            print("[ACP-ME] Wait for Ack Done!")
        return


class RemoteMemoryEntity(object):
    def __init__(self, acp_runtime, acp_code):
        self._runtime = acp_runtime
        self._code = acp_code

    def update(self, x, y, p, payload, sync=False, verbose=False):
        assert isinstance(payload, ACPAbstractType)

        acp_packet = ACPPacketME(ACP_COMMAND_ME_UPDATE, self._code, 0, payload.bytecode)
        sdp_packet = SDPPacket(x, y, p, acp_packet)

        if sync:
            sync_ack = SynAck(self._runtime, verbose=verbose)
            self._runtime.add_reaction(ACP_COMMAND_ACK, 0, sync_ack.get_callback())
            sync_ack.syn(x, y, p)
            #self._runtime.remove_reaction(ACP_COMMAND_ACK, 0)

        self._runtime.send_sdp(sdp_packet.sdp)

        return

    def read(self, x, y, p, payload, verbose=False):
        assert isinstance(payload, ACPAbstractType)

        reply = ReadReply(payload, verbose=verbose)
        self._runtime.add_reaction(ACP_COMMAND_ME_READ_REPLY, 0, reply.get_callback())

        acp_packet = ACPPacketME(ACP_COMMAND_ME_READ, self._code, 0, None)
        sdp_packet = SDPPacket(x, y, p, acp_packet)
        self._runtime.send_sdp(sdp_packet.sdp)
        
        reply.wait()
        self._runtime.remove_reaction(ACP_COMMAND_ME_READ_REPLY, 0)

        return
