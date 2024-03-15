# -*- coding: utf-8 -*-
#
# pifo_lib.py
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

from pprint import pprint, pformat


class Packet:
    def __init__(self, flow, idn, length=1):
        self.flow = flow
        self.idn = idn
        self.length = length

    def __repr__(self):
        return f"P(F:{self.flow}, I:{self.idn}, L:{self.length})"


class Runner:
    """This class is responsible for running a test on a packet scheduling
    algorithm. It is accountable for enquing and dequeing packets. For now, it
    does so by dequing as many packets as it enqued. In the next iteration, when
    we add pacing, it will need to handle virtual time cycling.
    """

    def __init__(self, pkts, scheduler):
        self.input_pkts = pkts
        self.scheduler = scheduler

    def run(self):
        print(f"Running with scheduler: {self.scheduler}")
        print("  Inserting packets into scheduler:")
        pprint(self.input_pkts, indent=4)
        for p in self.input_pkts:
            self.scheduler.enqueue(p, p)
        print("  Scheduler state:")
        self.scheduler.dump()
        output = []

        for p in self.scheduler:
            output.append(p)
        print("  Got packets from queue:")
        pprint(output, indent=4)


class SchedulingAlgorithm():

    """A queuing packet scheduling algorithm requires an abstraction that keeps
    the queuing data structure and the algorithm separate. To create a new
    Scheduling algorithm, inherit this class, add the scheduling data structures
    to the constructor, and implement the constructor, enqueue, dequeue, and the
    dump functions.

    Please look at the pifo_fifo.py to see how you implement a FIFO.
    """

    def __init__(self, name=None):
        self._name = name

    def enqueue(self, ref, item):
        raise NotImplementedError(self.__class__.__name__ + ' missing implementation')

    def dequeue(self):
        raise NotImplementedError(self.__class__.__name__ + ' missing implementation')

    def dump(self):
        raise NotImplementedError(self.__class__.__name__ + ' missing implementation')

    def __next__(self):
        pkt = self.dequeue()
        if pkt is None:
            raise StopIteration
        return pkt

    def __iter__(self):
        return self

    def __repr__(self):
        result = f"{self.__class__.__name__} - {self.__class__.__doc__}"
        if self._name is not None:
            result = f"{self._name}: {result}"
        return result


class Queue:
    def __init__(self, idx=None):
        self._list = []
        self.idx = idx

    def enqueue(self, ref, rank=None):
        self._list.append(ref)

    def peek(self):
        try:
            return self._list[0]
        except IndexError:
            return None

    def dequeue(self):
        try:
            return self._list.pop(0)
        except IndexError:
            return None

    def __next__(self):
        item = self.dequeue()
        if item is None:
            raise StopIteration
        return item

    def __iter__(self):
        return self

    @property
    def qlen(self):
        return len(self._list)

    def __len__(self):
        return self.qlen

    def __repr__(self):
        return f"{self.__class__.__name__}({self.idx})"

    def dump(self):
        pprint(self._list, indent=4)


class Pifo(Queue):
    def enqueue(self, ref, rank):
        if rank is None:
            raise ValueError("Rank can't be of value 'None'.")

        super().enqueue((rank, ref))
        self.sort()

    def sort(self):
        self._list.sort(key=lambda x: x[0])

    def dequeue(self):
        itm = super().dequeue()
        return itm[1] if itm else None

    def peek(self):
        itm = super().peek()
        return itm[1] if itm else None


class Flow(Queue):
    def __init__(self, idx):
        super().__init__(idx)

    def __repr__(self):
        return f"F(I:{self.idx}, Q:{self.qlen}, L:{self.length})"

    @property
    def length(self):
        result = 0
        for itm in self._list:
            result += itm.length if itm else 0
        return result


class FlowTracker():
    """This class provides us with the typical operation of keeping track of
    flows. Use this class in your scheduling algorithms when your algorithm only
    has one type of flows.
    """

    def __init__(self):
        self._flows = {}

    def enqueue(self, pkt, flow_id=None):
        if not isinstance(pkt, Packet):
            raise ValueError(f"Expected a packet, but got '{pkt}' instead.")
        if flow_id is None:
            flow_id = pkt.flow
        if not flow_id in self._flows:
            self._flows[flow_id] = Flow(flow_id)
        flow = self._flows[flow_id]
        flow.enqueue(pkt)
        return flow

    def get_flow(self, flow_id):
        return self._flows[flow_id]
