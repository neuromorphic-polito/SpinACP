# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import uuid
import time
import struct
import threading

from ._utils import Utils
from .spinnaker_interface import ConnectionListener, UDPSDPConnection, IPTag
from .routing_keys import load_routing_keys


class ACPRuntime(object):
    MAX_ATTEMPTS = 10
    DELAY_500ms = 500 * Utils.si['m']
    DELAY_100ms = 100 * Utils.si['m']
    DELAY_THR = 350 * Utils.si['u']

    VERBOSE = False
    HOST_IP = "."
    HOST_PORT = 50000
    HOST_VCHIP = 255
    SPINNAKER_PORT = 17893
    IP_TAG = 1

    __factory_key = uuid.uuid4()
    __instance = None

    @classmethod
    def create(cls, spinn_url, bmp_url):
        print("[ACPRuntime] Create")
        if cls.__instance is not None:
            print("[ACPRuntime] Warning: The ACP Runtime exist")
            return cls.__instance

        # Info
        board_version = 5

        # Create Transceiver and Boot with SCAMP
        transceiver = Utils.get_transceiver(spinn_url, bmp_url, board_version)
        scamp_version = transceiver.ensure_board_is_ready(enable_reinjector=False)

        # Create ACP Host-Board connection via IP-Tag
        iptag = IPTag(None, cls.IP_TAG, cls.HOST_IP, cls.HOST_PORT)
        transceiver.set_ip_tag(iptag)
        connection = UDPSDPConnection(
            chip_x=cls.HOST_VCHIP,
            chip_y=cls.HOST_VCHIP,
            remote_host=spinn_url,
            remote_port=cls.SPINNAKER_PORT,
            local_port=cls.HOST_PORT)

        # TODO: move in MCM Runtime?
        # Load Routing Keys
        load_routing_keys(transceiver)

        # Create Instance
        cls.__instance = cls(
            cls.__factory_key, 
            transceiver, 
            connection,
            spinn_url, 
            bmp_url, 
            board_version, 
            scamp_version)

        return cls.__instance

    def __init__(self, key, transceiver, connection, spinn_url, bmp_url, board_version, scamp_version):
        print("[ACPRuntime] Init")
        if key != ACPRuntime.__factory_key:
            raise Exception("[ACPRuntime] Error: Create this object from factory method!")

        # --
        self._spinn_url = spinn_url
        self._bmp_url = bmp_url
        self._board_version = board_version
        self._scamp_version = scamp_version

        # --
        self._transceiver = transceiver
        self._connection = connection

        # --
        self._enabled = False
        self._start = False

        # --
        self._reactions = dict()
        self._stop_event = threading.Event()
        self._listener = None

    def __del__(self):
        self._connection._socket.close()
        ACPRuntime.__instance = None

    def __str__(self):
        _str = "SpiNNaker ACP Runtime\n"
        _str += "\tspinn: {}\n".format(self.spinn_url)
        _str += "\tbmp: {}\n".format(self.bmp_url)
        _str += "\tboard: {}\n".format(self.board_version)
        _str += "\tSC&MP: {}\n".format(self.scamp_version)
        return _str

    @classmethod
    def _get_callback(cls, instance):
        def _callback(msg):
            self = instance
            try:
                acp_cmd, acp_me_code, bytecode = self._get_acp(msg)
                if (acp_cmd, acp_me_code) in self._reactions:
                    self._reactions[(acp_cmd, acp_me_code)](bytecode)
            except Exception as e:
                raise e
            
        return _callback

    @classmethod
    def _get_acp(cls, msg):
        if msg.data < 18:
            raise Exception("[ACPRuntime] Error: Wrong ACP packet!")
        
        # Remove 2 Byte padding
        bytecode = msg.data[2:]  
        
        if cls.VERBOSE:
            print("[ACPRuntime] Incoming ACP: {} Bytes".format(len(bytecode)))
            bytecode_hex = ":".join("{:02x}".format(ord(c)) for c in bytecode)
            print("             RAW: {}".format(bytecode_hex))
        
        # Header SDP
        (flags, ip_tag, dst_port, src_port, dst_x, dst_y, src_x, src_y) = struct.unpack("<8B", bytecode[:8]) # SDP
        sdp_destination = (dst_x, dst_y, dst_port & 0x1F)
        sdp_destination_port = (dst_port & 0xE0)
        sdp_source = (src_x, src_y, src_port & 0x1F)
        sdp_source_port = (src_port & 0xE0)

        # Header ACP
        (acp_header_cmd, acp_header_cnt_len, acp_header2) = struct.unpack("<2H1I", bytecode[8:16])
        acp_header_cnt = acp_header_cnt_len >> 9
        acp_header_len = acp_header_cnt_len & 0x01FF
        acp_me_id = acp_header2 & 0xFFFF

        # Payload
        acp_payload = bytecode[16:]
        
        # Verbose
        if cls.VERBOSE:
            print("  SDP: From {} [{}] To {} [{}]".format(sdp_source, sdp_source_port, sdp_destination, sdp_destination_port))        
            print("       Flags  {:02x}".format(flags))
            print("       IP-Tag {:02x}".format(ip_tag))

            print("  ACP: Command {:04x}".format(acp_header_cmd))
            print("       Counter {:02x}".format(acp_header_cnt))
            print("       Length  {:02x}".format(acp_header_len))
            print("       Command Header {:08x}".format(acp_header2))
            
            payload_hex = ":".join("{:02x}".format(ord(c)) for c in acp_payload)
            print("       Payload [{:d} Byte] {:s}".format(len(acp_payload), payload_hex))

        return acp_header_cmd, acp_me_id, bytecode

    def board_sync(self, app_id, context, state=None, signal=None):
        # State wait
        if state is not None:
            if self._board_check_state(context, state):
                print("[ACPRuntime]: All instance are in correct state!")
            else:
                print("[ACPRuntime]: Error, some instances are not in correct state!")
                sys.exit(1)

        # Send signal
        if signal is not None:
            self.transceiver.send_signal(app_id, signal)

    def _board_check_state(self, context, state):
        attempts = 0
        count = context.get_state_count(state)

        while count != context.cores_number and attempts < self.MAX_ATTEMPTS:
            attempts += 1
            if attempts > self.MAX_ATTEMPTS/2:
                print("\t...Attempt %d" % (attempts,))
            count = context.get_state_count(state)
            time.sleep(self.DELAY_500ms)

        if count == context.cores_number:
            return True
        else:
            return False

    def add_reaction(self, acp_cmd, acp_var, callback):
        #print("[ACPRuntime] Add Reaction {}:{}".format(acp_cmd, acp_var))
        self._reactions[(acp_cmd, acp_var)] = callback
        return

    def remove_reaction(self, acp_cmd, acp_var):
        k = (acp_cmd, acp_var)
        if k in self._reactions:
            #print("[ACPRuntime] Del Reaction {}:{}".format(acp_cmd, acp_var))
            del self._reactions[k]
        return

    def enable(self):
        print("[ACPRuntime] Enabling")
        self._listener = ConnectionListener(self._connection)
        self._listener.add_callback(self._get_callback(self))
        self._enabled = True

    def start(self):
        if not self._enabled:
            print("[ACPRuntime] Error: ACP Runtime not enabled!")
            sys.exit(2)
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

    def send_sdp(self, message):
        self.transceiver.send_sdp_message(
            message, connection=self.connection)
        time.sleep(self.DELAY_THR)
        return

    @property
    def transceiver(self):
        return self._transceiver

    @property
    def connection(self):
        return self._connection

    @property
    def spinn_url(self):
        return self._spinn_url

    @property
    def bmp_url(self):
        return self._bmp_url

    @property
    def board_version(self):
        return self._board_version

    @property
    def scamp_version(self):
        return self._scamp_version.version_string
