# -*- coding: utf-8 -*-
from __future__ import print_function

import time

from ._utils import Utils
from .spinnaker_interface import CoreSubset, CoreSubsets


class ACPContext(object):
    DELAY_1ms = 1 * Utils.si['m']
    VERBOSITY = 1

    def __init__(self, runtime, context_radius, context_cores):
        self._runtime = runtime
        self._context_radius = context_radius
        self._context_cores = context_cores

        self._context_dict = {
            (0, 0): range(1, 1 + context_cores)
        }

        if context_radius > 0:
            self._context_dict.update({
                (0, 1): range(1, 1 + context_cores),
                (1, 1): range(1, 1 + context_cores),
                (1, 0): range(1, 1 + context_cores)})         # 4
        if context_radius > 1:
            self._context_dict.update({
                (0, 2): range(1, 1 + context_cores),
                (1, 2): range(1, 1 + context_cores),
                (2, 2): range(1, 1 + context_cores),
                (2, 1): range(1, 1 + context_cores),
                (2, 0): range(1, 1 + context_cores)})        # 9
        if context_radius > 2:
            self._context_dict.update({
                (0, 3): range(1, 1 + context_cores),
                (1, 3): range(1, 1 + context_cores),
                (2, 3): range(1, 1 + context_cores),
                (3, 3): range(1, 1 + context_cores),
                (3, 2): range(1, 1 + context_cores),
                (3, 1): range(1, 1 + context_cores),
                (3, 0): range(1, 1 + context_cores)})        # 16
        if context_radius > 3:
            self._context_dict.update({
                (1, 4): range(1, 1 + context_cores),
                (2, 4): range(1, 1 + context_cores),
                (3, 4): range(1, 1 + context_cores),
                (4, 4): range(1, 1 + context_cores),
                (4, 3): range(1, 1 + context_cores),
                (4, 2): range(1, 1 + context_cores),
                (4, 1): range(1, 1 + context_cores),
                (4, 0): range(1, 1 + context_cores)})        # 24
        if context_radius > 4:
            self._context_dict.update({
                (2, 5): range(1, 1 + context_cores),
                (3, 5): range(1, 1 + context_cores),
                (4, 5): range(1, 1 + context_cores),
                (5, 5): range(1, 1 + context_cores),
                (5, 4): range(1, 1 + context_cores),
                (5, 3): range(1, 1 + context_cores),
                (5, 2): range(1, 1 + context_cores),
                (5, 1): range(1, 1 + context_cores)})        # 32
        if context_radius > 5:
            self._context_dict.update({
                (3, 6): range(1, 1 + context_cores),
                (4, 6): range(1, 1 + context_cores),
                (5, 6): range(1, 1 + context_cores),
                (6, 6): range(1, 1 + context_cores),
                (6, 5): range(1, 1 + context_cores),
                (6, 4): range(1, 1 + context_cores),
                (6, 3): range(1, 1 + context_cores),
                (6, 2): range(1, 1 + context_cores)})       # 40
        if context_radius > 6:
            self._context_dict.update({
                (4, 7): range(1, 1 + context_cores),
                (5, 7): range(1, 1 + context_cores),
                (6, 7): range(1, 1 + context_cores),
                (7, 7): range(1, 1 + context_cores),
                (7, 6): range(1, 1 + context_cores),
                (7, 5): range(1, 1 + context_cores),
                (7, 4): range(1, 1 + context_cores),
                (7, 3): range(1, 1 + context_cores)})       # 48

        self._cores_number = 0
        self._cores_subsets = None
        self._ranked_cores_dict = None
        self._chips_in_radius = [1, 3, 5, 7, 8, 8, 8, 8]
        self._init_create_subsets()

    def __str__(self):
        _str = ""
        _str += "SpiNNaker ACP Runtime - Context\n"
        cores_dict = self.cores_dict
        for x, y in cores_dict.keys():
            _str += "\tChip: %d %d Cores %s\n" % (x, y, cores_dict[(x, y)])

        if self.VERBOSITY > 0:
            cpu_info = self.get_info()
            _str += "\tCPU info:\n"
            for cpu in cpu_info:
                _str += "\t"
                _str += "%d %d %d " % (cpu.x, cpu.y, cpu.p)
                _str += "(%d) " % (cpu.physical_cpu_id,)
                _str += "%s" % (cpu.state,)
                _str += "\n"

        return _str

    def _init_create_subsets(self):
        self._ranked_cores_dict = dict()

        cores_dict = self.cores_dict
        self._cores_number = 0
        cores_subset_list = list()
        for x, y in sorted(cores_dict.keys()):
            for p in cores_dict[(x, y)]:
                self._ranked_cores_dict[self.cores_number] = (x, y, p)
                self._cores_number += 1
            cores_subset_list.append(CoreSubset(x, y, cores_dict[(x, y)]))

        self._cores_subsets = CoreSubsets(core_subsets=cores_subset_list)
        return

    def get_processor(self, rank):
        return self._ranked_cores_dict[rank]

    def get_info(self):
        cpu_info = self._runtime.transceiver.get_cpu_information(self._cores_subsets)
        cpu_info = sorted(cpu_info, key=lambda x: (x.x, x.y, x.p))
        return cpu_info

    def get_state_count(self, state):
        cpu_info = self.get_info()
        count = 0
        for cpu in cpu_info:
            if cpu.state == state:
                count += 1
        return count

    def get_buffers(self):
        io_buffer_obj = self._runtime.transceiver.get_iobuf(self._cores_subsets)
        io_buffer_dict = dict()

        for buf in io_buffer_obj:
            str_list = ("%s" % buf.iobuf).split("\n")
            io_buffer_dict[(buf.x, buf.y, buf.p)] = str_list
            time.sleep(self.DELAY_1ms)

        return io_buffer_dict

    @property
    def cores_dict(self):
        return dict(self._context_dict)

    @property
    def cores_subsets(self):
        return self._cores_subsets

    @property
    def cores_number(self):
        return self._cores_number
