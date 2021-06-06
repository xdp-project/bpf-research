#!/usr/bin/env python3
# coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pifo-hpfq.py

"""HierarchicalPacket  Fair  Queueing  (HPFQ)

This scheduling algorithm is mentioned in the paper "Programmable packet
scheduling at line rate" by Sivaraman, Anirudh, et al. It creates a hierarchy of
WFQ schedulers. The central scheduler is called root and contains references to
other WFQ schedulers. Those two WFQ schedulers are called left and right. We
chose that packets with flow ids lower than ten go into the left scheduler in
our implementation. In contrast, the others go into the right scheduler."""

__copyright__ = """
Copyright (c) 2021, Toke Høiland-Jørgensen <toke@toke.dk>
Copyright (c) 2021, Frey Alfredsson <freysteinn@freysteinn.com>
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

from sched_lib import Packet, Runner, SchedulingAlgorithm
from pifo_wfq import Wfq


class Hpfq(SchedulingAlgorithm):
    """HierarchicalPacket  Fair  Queueing  (HPFQ)"""

    def __init__(self, name=None):
        super().__init__(name)
        self._root = Wfq("root")
        self._left = Wfq("Left")
        self._right = Wfq("Right")

    def enqueue(self, ref, item):
        queue = None
        if item.flow < 10:
            self._left.enqueue(ref, item)
            queue = self._left
        else:
            self._right.enqueue(ref, item)
            queue = self._right

        self._root.enqueue(queue, item)

    def dequeue(self):
        queue = self._root.dequeue()
        return queue.dequeue() if queue is not None else None

    def dump(self):
        print("   Root:")
        self._root.dump()
        print("   Left:")
        self._left.dump()
        print("   Right:")
        self._right.dump()


if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=200),
        Packet(flow=1, idn=2, length=200),
        Packet(flow=10, idn=1, length=200),
        Packet(flow=10, idn=2, length=200),
        Packet(flow=2, idn=1, length=100),
        Packet(flow=2, idn=2, length=100),
        Packet(flow=2, idn=3, length=100),
        Packet(flow=20, idn=1, length=100),
        Packet(flow=20, idn=2, length=100),
        Packet(flow=20, idn=3, length=100),
    ]
    Runner(pkts, Hpfq()).run()
