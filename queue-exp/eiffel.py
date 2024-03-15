#!/usr/bin/env python3
# coding: utf-8 -*-
#
# eiffel.py
#
# Author:   Toke Høiland-Jørgensen (toke@toke.dk)
# Date:     18 May 2021
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

from pifo_lib import Packet, Runner, Pifo, Flow


class EiffelPifo(Pifo):
    def __init__(self):
        super().__init__()
        self.flows = {}

    def get_flow_idx(self, pkt):
        return pkt.flow

    def enqueue_flow(self, f, rank=None, idx=None):
        if idx is None:
            idx = self.get_flow_idx(f)
        if idx not in self.flows:
            self.flows[idx] = f
        super().enqueue(f, rank=rank)

    def enqueue(self, pkt):
        # If we don't have state for the flow, create it and enqueue the flow to
        # the PIFO
        fid = self.get_flow_idx(pkt)
        if fid not in self.flows:
            f = Flow(fid)
            f.enqueue(pkt)
            self.enqueue_flow(f, idx=fid)

        # Otherwise, if we *do* have state for the flow, enqueue the packet to
        # the flow,recompute its rank and update the position in the PIFO
        else:
            f = self.flows[fid]
            f.enqueue(pkt)

            # FIXME: This doesn't work after adding the ability for items to be
            # enqueued multiple times with different ranks (needed for the
            # hierarchical mode)
            f.rank = self.get_rank(f)
            self.sort()

    def dequeue(self):
        f = super().dequeue()

        # This handles empty flows and recursive instances of PIFOs
        if not isinstance(f, Flow):
            return f

        pkt = f.dequeue()

        # If we emptied out the flow, remove it from the flow state table
        if len(f) == 0:
            del self.flows[f.idx]
        # Otherwise, compute a new flow rank and re-enqueue it into the PIFO
        # with that rank
        else:
            self.enqueue_flow(f, idx=f.idx, rank=self.get_rank_dequeue(f))

        return pkt

    def get_rank_dequeue(self, flow):
        return flow.rank


class Stfq(EiffelPifo):
    def __init__(self):
        super().__init__()
        self.last_finish = {}
        self.virt_time = 1

    def get_rank(self, flow, force=False):
        # We don't change the flow rank on enqueue if it already has one
        if flow.rank and not force:
            return flow.rank

        if flow.idx in self.last_finish:
            r = max(self.virt_time, self.last_finish[flow.idx])
        else:
            r = self.virt_time

        self.last_finish[flow.idx] = r + flow.peek().length
        return r

    def get_rank_dequeue(self, flow):
        # Recompute rank for next packet in flow; always exists in last_finish
        # because we never clean that up
        pkt = flow.peek()
        r = self.last_finish[flow.idx]
        self.last_finish[flow.idx] = r + pkt.length
        return r


class Fifo(EiffelPifo):
    def get_flow_idx(self, _pkt):
        return 0

    def get_rank(self, _flow):
        return 0


if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=1),
        Packet(flow=1, idn=2, length=1),
        Packet(flow=1, idn=3, length=1),
        Packet(flow=2, idn=1, length=1),
        Packet(flow=2, idn=2, length=1),
        Packet(flow=2, idn=3, length=1),
    ]
    Runner(pkts, Fifo()).run()
    Runner(pkts, Stfq()).run()
