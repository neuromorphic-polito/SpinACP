# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from .spinnaker_interface \
    import create_transceiver_from_hostname, \
           BMPConnectionData, \
           SpinnmanIOException, \
           SpinnmanInvalidPacketException, \
           SpinnmanInvalidParameterException, \
           SpinnmanUnexpectedResponseCodeException, \
           SpinnmanGenericProcessException


class Utils(object):
    si = {'T': 10**(+12),
          'G': 10**(+9),
          'M': 10**(+6),
          'k': 10**(+3),
          'h': 10**(+2),
          'da': 10**(+1),
          'd': 10**(-1),
          'c': 10**(-2),
          'm': 10**(-3),
          'u': 10**(-6),
          'n': 10**(-9),
          'p': 10**(-12)}

    @classmethod
    def spinn5_radius_processors(cls, r, p):
        _r = [1, 4, 9, 16, 24, 32, 40, 48]
        return _r[r] * p

    @classmethod
    def print_io_buffers(cls, io_buffer_dict):
        print("[ACPRuntime] Print SpiNNaker Buffers")
        chip_list = sorted(io_buffer_dict.keys())
        for x, y, p in chip_list:
            for line in io_buffer_dict[(x, y, p)]:
                print("%d:%d:%d > %s" % (x, y, p, line))
            print("")

    @classmethod
    def get_io_buffers(cls, io_buffer_dict):
        s = ["SpiNNaker - Buffers"]
        chip_list = sorted(io_buffer_dict.keys())
        for x, y, p in chip_list:
            for line in io_buffer_dict[(x, y, p)]:
                s.append("%d:%d:%d > %s" % (x, y, p, line))
            s.append("\n")
        return s

    @classmethod
    def runtime_check(cls, runtime):
        t = runtime.transceiver
        version_info = t.ensure_board_is_ready()
        print(version_info)

    @classmethod
    def get_transceiver(cls, spinn_url, bmp_url, version):
        bmp = BMPConnectionData(0, 0, bmp_url, [0], None)
        try:
            transceiver = create_transceiver_from_hostname(
                spinn_url, version,
                bmp_connection_data=[bmp],
                auto_detect_bmp=False)
        except (SpinnmanIOException,
                SpinnmanInvalidPacketException,
                SpinnmanInvalidParameterException,
                SpinnmanUnexpectedResponseCodeException,
                SpinnmanGenericProcessException) as e:
            print("[ACPRuntime] Error: Impossible to reach the SpiNNaker Board %s" % (spinn_url,))
            sys.exit(e)
        return transceiver
