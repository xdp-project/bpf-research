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
        self.rank = 0

    def __repr__(self):
        return f"P(F:{self.flow}, I:{self.idn}, L:{self.length})"


class Runner:
    def __init__(self, pkts, queue):
        self.input_pkts = pkts
        self.queue = queue

    def run(self):
        print(f"Running with queue: {self.queue}")
        print("  Inserting packets into queue:")
        pprint(self.input_pkts, indent=4)
        for p in self.input_pkts:
            self.queue.enqueue(p)
        print("  Queue state:")
        self.queue.dump()
        output = []
        for p in self.queue:
            output.append(p)
        print("  Got packets from queue:")
        pprint(output, indent=4)


class Queue:
    def __init__(self, idx=None):
        self._list = []
        self.idx = idx

    def enqueue(self, item):
        self._list.append(item)

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

    def enqueue(self, item, rank=None):
        if rank is None:
            rank = self.get_rank(item)
        item.rank = rank
        super().enqueue((rank, item))
        self.sort()

    def sort(self):
        self._list.sort(key=lambda x: x[0])

    def dequeue(self):
        itm = super().dequeue()
        return itm[1] if itm else None

    def peek(self):
        itm = super().peek()
        return itm[1] if itm else None

    def get_rank(self, item):
        raise NotImplementedError


class Flow(Queue):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self.rank = 0

    def __repr__(self):
        return f"F({self.idx})"

    # Return the length of the first packet in the queue as the "length" of the
    # flow. This is not the correct thing to do, but it works as a stopgap
    # solution for testing the hierarchical mode, and we're only using
    # unit-length for that anyway
    @property
    def length(self):
        itm = self.peek()
        return itm.length if itm else 0
