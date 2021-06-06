#!/usr/bin/env python3
# coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pifo-srpt.py

"""Shortest Remaining Processing Time (SRPT).

This scheduling algorithm is referenced in companion C++ implementation for the
paper "Programmable packet scheduling at line rate" by Sivaraman, Anirudh, et
al.

It schedules packets in the order of how much data the flow has left. It assumes
complete knowledge of the flow length. In the real world, this would either need
to be estimated or limited to predictable flows.
"""

__copyright__ = """
Copyright (c) 2021 Toke Høiland-Jørgensen <toke@toke.dk>
Copyright (c) 2021 Frey Alfredsson <freysteinn@freysteinn.com>
"""

__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from sched_lib import Packet, Runner, Pifo, SchedulingAlgorithm
from sched_lib import FlowTracker


class Srpt(SchedulingAlgorithm):
    """Shortest Remaining Processing Time"""

    def __init__(self, name=None):
        super().__init__(name)
        self._pifo = Pifo()
        self._flow_tracker = FlowTracker()

        self._remains = {}

        # We cheat by accessing the global packet list directly
        for pkt in pkts:
            if pkt.flow in self._remains.keys():
                self._remains[pkt.flow] += pkt.length
            else:
                self._remains[pkt.flow] = pkt.length

    def get_rank(self, item):
        """Rank the items by their remaining total flow length."""

        rank = self._remains[item.flow]
        self._remains[item.flow] -= item.length
        return rank

    def enqueue(self, ref, item):
        flow = self._flow_tracker.enqueue(item)
        rank = self.get_rank(item)
        self._pifo.enqueue(flow, rank)

    def dequeue(self):
        flow = self._pifo.dequeue()
        item = None
        if flow is not None:
            item = flow.dequeue()
        return item

    def dump(self):
        self._pifo.dump()

if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=2),
        Packet(flow=1, idn=2, length=2),
        Packet(flow=2, idn=1, length=1),
        Packet(flow=2, idn=2, length=1),
        Packet(flow=2, idn=3, length=1),
    ]
    Runner(pkts, Srpt()).run()
