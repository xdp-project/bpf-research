#!/usr/bin/env python3
# coding: utf-8 -*-
#
# eiffel-procedural.py
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

from pifo_lib import Packet, Runner, Queue, Pifo, Flow


class Policy(Queue):
    def __init__(self):
        super().__init__()
        self.queues = {1: Pifo(1),
                       2: Pifo(2),
                       3: Pifo(3)}
        self.state = {1: {'last_finish': {}, 'parent': None},
                      2: {'last_finish': {}, 'parent': 1},
                      3: {'last_finish': {}, 'parent': 1}}
        self.flows = {1: Flow(1),
                      2: Flow(2),
                      3: Flow(3),
                      4: Flow(4)}

        # map flows to their classes
        self.class_map = {1: 2,
                          2: 2,
                          3: 2,
                          4: 3}

    def get_queue_state(self, queue_idx):
        return self.queues[queue_idx], self.state[queue_idx]

    def compute_rank(self, state, cls):
        r = state['last_finish'].get(cls, 1)
        state['last_finish'][cls] = r + 1
        return r

    def enqueue(self, pkt):
        fid = pkt.flow
        queue_idx = self.class_map[pkt.flow]
        q, state = self.get_queue_state(queue_idx)

        flow = self.flows[fid]
        flow.enqueue(pkt)

        if len(flow) == 1:
            q.enqueue(flow, rank=self.compute_rank(state, fid % 2))

        if state['parent']:
            parent, p_state = self.get_queue_state(state['parent'])
            parent.enqueue(q, rank=self.compute_rank(p_state, queue_idx))

    def dequeue(self):
        flow = self.queues[1].dequeue()
        if flow is None:
            return None
        pkt = flow.dequeue()
        while hasattr(pkt, "dequeue"):
            flow = pkt
            pkt = flow.dequeue()

        # re-enqueue flow in class PIFO with new rank
        if len(flow) > 0:
            q, state = self.get_queue_state(self.class_map[flow.idx])
            q.enqueue(flow, rank=self.compute_rank(state, flow.idx % 2))
        return pkt


    def dump(self):
        self.queues[1].dump()
        self.queues[2].dump()
        self.queues[3].dump()


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
