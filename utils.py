#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Felipe Gallego. All rights reserved.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Script with utils.
"""

from ctes import *

def get_matchings(name, data, is_first):
    
    mat = []
    res = [0, 0, 0]
    val_res = ""
    
    for d in data:
        if is_first:
            data_name = d[R_NAME_1_COL]
        else:
            data_name = d[R_NAME_2_COL]
            
        if name == data_name:
            r = d[FIRST_R_COL:]
            mat.append(r)
            res = [x + y for x, y in zip(res, SUM_DIF_POS[r[R_NAME_2_COL]])]
            
    mx = max(res)
    
    for i in range(len(NAMES_AP)):
        if res[i] == mx:
            val_res += NAMES_AP[i]
            
    return mat, val_res