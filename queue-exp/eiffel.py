# -*- coding: utf-8 -*-
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

    def enqueue(self, pkt):
        # If we don't have state for the flow, create it and enqueue the flow to
        # the PIFO
        if pkt.flow not in self.flows:
            f = Flow(pkt.flow)
            f.enqueue(pkt)
            self.flows[f.idx] = f
            super().enqueue(f)

        # Otherwise, if we *do* have state for the flow, enqueue the packet to
        # the flow,recompute its rank and update the position in the PIFO
        else:
            f = self.flows[pkt.flow]
            f.enqueue(pkt)
            f.rank = self.get_rank(f)
            self.sort()

    def dequeue(self):
        f = self.peek()
        if f is None:
            return f

        pkt = f.dequeue()

        # If we emptied out the flow, remove it from the queue and the flow
        # state table
        if len(f) == 0:
            super().dequeue()
            del self.flows[f.idx]
        # Otherwise, update the flow rank and its position in the FIFO
        else:
            f.rank = self.get_rank_dequeue(f)
            self.sort()
        return pkt

    def get_rank_dequeue(self, flow):
        raise NotImplementedError

