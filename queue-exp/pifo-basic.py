#!/usr/bin/env python3
# coding: utf-8 -*-
#
# pifo-basic.py
#
# Author:   Toke Høiland-Jørgensen (toke@toke.dk)
# Date:     17 May 2021
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

from pifo_lib import Packet, Runner, Pifo


class Fifo(Pifo):
    def get_rank(self, item):
        return self.qlen


class Stfq(Pifo):
    def __init__(self):
        super().__init__()
        self.last_finish = {}
        self.virt_time = 0

    def get_rank(self, pkt):
        f = pkt.flow
        if f in self.last_finish:
            r = max(self.virt_time, self.last_finish[f])
        else:
            r = self.virt_time
        self.last_finish[f] = r + pkt.length
        return r

if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=2),
        Packet(flow=1, idn=2, length=2),
        Packet(flow=2, idn=1, length=1),
        Packet(flow=2, idn=2, length=1),
        Packet(flow=2, idn=3, length=1),
    ]
    Runner(pkts, Fifo()).run()
    Runner(pkts, Stfq()).run()
