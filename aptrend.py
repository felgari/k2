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

"""Script to calculate ap for trend.
"""

import sys
import os
import csv

from ctes import *

class ApTrend(object):
    
    def __init__(self):
        
        self._ap = []

    def calculate_ap(self, trend, first_trend, second_trend, pos1, pos2):
        
        cur_ap = TREND_IG
        
        v1 = trend[0]
        v2 = trend[1]
        v3 = trend[2]
        
        if v1 > TREND_HIGH_VALUE:
            if first_trend == AVPOS_TREND_UP:
                cur_ap = TREND_1
        elif v2 > TREND_HIGH_VALUE:
            if v2 - v1 > v3 and first_trend == AVPOS_TREND_UP:
                cur_ap = TREND_2
            elif v2 - v3 > v1 and second_trend == AVPOS_TREND_UP:
                cur_ap = TREND_4
            else:
                cur_ap = TREND_3
        elif v3 > TREND_HIGH_VALUE:
            if first_trend == AVPOS_TREND_DOWN or second_trend == AVPOS_TREND_UP:
                cur_ap = TREND_5            
        elif abs(v1 - TREND_AV < TREND_AV_DIFF) and \
            abs(v2 - TREND_AV < TREND_AV_DIFF) and \
            abs(v3 - TREND_AV < TREND_AV_DIFF):
            cur_ap = TREND_3
        elif first_trend == AVPOS_TREND_UP and second_trend == AVPOS_TREND_DOWN:
            cur_ap = TREND_1
        elif first_trend == AVPOS_TREND_DOWN and second_trend == AVPOS_TREND_UP \
            and v2 >= v1 and v3 > v1:
            cur_ap = TREND_4
        elif pos1 < pos2 and pos1 - pos2 <= TREND_POS_DIFF_H:
            cur_ap = TREND_1
        elif pos1 > pos2 and pos1 - pos2 >= TREND_POS_DIFF_V:
            cur_ap = TREND_4
            
        self._ap.append(cur_ap)
        
        return cur_ap
    
    def write_data(self, index):
        
        out_file_name = os.path.join(DATA_PATH, AP_FILE_TREND_PREFIX + str(index) + AP_FILE_TREND_EXT)
        
        print "Saving trend ap in: %s" % out_file_name    
                    
        with open(out_file_name, "wb") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=CSV_DELIMITER)            
            
            for ap_d in self._ap:
                row = [ ap_d ]
                csvwriter.writerow(row)   