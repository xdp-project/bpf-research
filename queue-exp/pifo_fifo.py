#!/usr/bin/env python3
# coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pifo-fifo.py

"""First in, first out (FIFO)

The FIFO scheduling algorithm preserves the order of the scheduled packets. This
implementation is here for completeness and uses a PIFO. It is here to help
people understand how to add new scheduling algorithms to this framework.
"""

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

from pifo_lib import Packet, Runner, Pifo
from pifo_lib import SchedulingAlgorithm


class Fifo(SchedulingAlgorithm):
    """First in, first out (FIFO)"""

    def __init__(self):
        self._pifo = Pifo()

    def enqueue(self, item):
        rank = self.get_rank(item)
        self._pifo.enqueue(item, rank)

    def get_rank(self, item):
        return self._pifo.qlen

    def dequeue(self):
        return self._pifo.dequeue()

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
    Runner(pkts, Fifo()).run()
