#!/usr/bin/env python3
# coding: utf-8 -*-
#
# eiffel-hiearch.py
#
# Author:   Toke Høiland-Jørgensen (toke@toke.dk)
# Date:     19 May 2021
# Copyright (c) 2021, Toke Høiland-Jørgensen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pifo_lib import Packet, Runner, Queue
from eiffel import Stfq

class EiffelHierarchical(Stfq):
    """Hierarchical Eiffel PIFO.

    Based on Stfq for the per-level scheduling, but implements a policy
    hierarchy by enqueueing references to itself in its parents."""

    def __init__(self, idx, parent=None):
        super().__init__()
        self.idx = idx
        self.parent = parent
        self.rank = 0

    def get_flow_idx(self, itm):
        if hasattr(itm, "idx"):
            return itm.idx
        # default two classes,
        return itm.flow % 2

    def enqueue(self, itm):
        if isinstance(itm, Packet):
            super().enqueue(itm)
        else:
            self.enqueue_flow(itm)
        if self.parent is not None:
            self.parent.enqueue_flow(self,
                                     rank=self.parent.get_rank(self, True))

    def dequeue(self):
        itm = super().dequeue()
        if self.parent is None:
            while hasattr(itm, "dequeue"):
                itm = itm.dequeue()
        return itm

    def __repr__(self):
        return f"{self.__class__.__name__}({self.idx})"

class Policy(Queue):
    def __init__(self):
        super().__init__()
        self.pq1 = EiffelHierarchical(1)
        self.pq2 = EiffelHierarchical(2, parent=self.pq1)
        self.pq3 = EiffelHierarchical(3, parent=self.pq1)

        # map flows to their classes
        self.class_map = {1: self.pq2,
                          2: self.pq2,
                          3: self.pq2,
                          4: self.pq3}

    def enqueue(self, pkt):
        self.class_map[pkt.flow].enqueue(pkt)

    def dequeue(self):
        return self.pq1.dequeue()

    def dump(self):
        self.pq1.dump()


if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=1),
        Packet(flow=1, idn=2, length=1),
        Packet(flow=1, idn=3, length=1),
        Packet(flow=2, idn=1, length=1),
        Packet(flow=2, idn=2, length=1),
        Packet(flow=2, idn=3, length=1),
        Packet(flow=2, idn=4, length=1),
        Packet(flow=2, idn=5, length=1),
        Packet(flow=3, idn=1, length=1),
        Packet(flow=3, idn=2, length=1),
        Packet(flow=3, idn=3, length=1),
        Packet(flow=4, idn=1, length=1),
        Packet(flow=4, idn=2, length=1),
        Packet(flow=4, idn=3, length=1),
        Packet(flow=4, idn=4, length=1),
        Packet(flow=4, idn=5, length=1),
        Packet(flow=4, idn=6, length=1),
        Packet(flow=4, idn=7, length=1),
        Packet(flow=4, idn=8, length=1),
        Packet(flow=4, idn=9, length=1),
        Packet(flow=4, idn=10, length=1),
    ]
    Runner(pkts, Policy()).run()
