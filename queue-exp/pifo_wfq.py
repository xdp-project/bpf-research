#!/usr/bin/env python3
# coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pifo-wfq.py

"""Weighted Fair Queueing (WFQ)

This scheduling algorithm is mentioned in the paper "Programmable packet
scheduling at line rate" by Sivaraman, Anirudh, et al. It schedules flows by
giving them a fraction of the capacity using predefined weights. In our example,
we defined flows with an odd number to get a weight of 50 and even numbers to
get 100.
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


class Wfq(SchedulingAlgorithm):
    """Weighted Fair Queueing (WFQ)"""

    def __init__(self, name=None):
        super().__init__(name)
        self._pifo = Pifo()
        self._last_finish = {}
        self._virt_time = 0

    def get_rank(self, item):
        """Rank the items by their start time, which we calculate from the
        finish time of the last packet. However, we divide the packet's length
        with weights to prioritize them. We determine the weights by splitting
        the flow-ids into odd and even numbers.
        """
        flow = item.flow
        weight = 50 if flow % 2 == 1 else 100
        if flow in self._last_finish:
            rank = max(self._virt_time, self._last_finish[flow])
        else:
            rank = self._virt_time
        self._last_finish[flow] = rank + item.length / weight
        return rank

    def enqueue(self, ref, item):
        rank = self.get_rank(item)
        self._pifo.enqueue(ref, rank)

    def dequeue(self):
        return self._pifo.dequeue()

    def dump(self):
        self._pifo.dump()


if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=100),
        Packet(flow=1, idn=2, length=100),
        Packet(flow=1, idn=3, length=100),
        Packet(flow=2, idn=1, length=100),
        Packet(flow=2, idn=2, length=100),
        Packet(flow=2, idn=3, length=100),
    ]
    Runner(pkts, Wfq()).run()
