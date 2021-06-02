#!/usr/bin/env python3
# coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pifo-stfq.py

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

from pifo_lib import Packet, Runner, Pifo


class Stfq(Pifo):
    def __init__(self):
        super().__init__()
        self.last_finish = {}
        self.virt_time = 0

    def get_rank(self, pkt):
        flow = pkt.flow
        if flow in self.last_finish:
            rank = max(self.virt_time, self.last_finish[flow])
        else:
            rank = self.virt_time
        self.last_finish[flow] = rank + pkt.length
        return rank

if __name__ == "__main__":
    pkts = [
        Packet(flow=1, idn=1, length=2),
        Packet(flow=1, idn=2, length=2),
        Packet(flow=2, idn=1, length=1),
        Packet(flow=2, idn=2, length=1),
        Packet(flow=2, idn=3, length=1),
    ]
    Runner(pkts, Stfq()).run()
