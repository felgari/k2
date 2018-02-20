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

"""Calculation of ap.
""" 

from ctes import *
import numpy as np

def calc_ap_from_avg_pred(red):
    
    l_min = []
    l_max = []
    ap = []
    var = []
    var2 = []
    
    for r in red:
        l_min.append(min(r))
        l_max.append(max(r))
    
    for r, mi, ma in zip(red, l_min, l_max):

        v = np.var(r)
        var.append(int(v))
        
        v2 = np.var([ma, 100.0 - ma - mi])
        var2.append(int(v2))
        
        if v < AP_VAR_MIN:
            
            if ma > AP_ENO_VAL_VAR:
                ap.append(INDEX_TO_VAL[r.index(ma)])
            else:
                ap.append(AP_ALL_VAL)
                
        elif v2 < AP_VAR2_MIN:
            if ma > AP_ENO_VAL_VAR:
                ap.append(INDEX_TO_VAL[r.index(ma)])
            else:
                ap.append(COMPLEMENT[INDEX_TO_VAL[r.index(mi)]])
        else:
            ap.append(INDEX_TO_VAL[r.index(ma)])
            
    return ap, var, var2, l_max, l_min

def calc_pre_avg(pre_1, pre_2):
    
    pre_avg = []
    red = []    

    for p1, p2 in zip(pre_1, pre_2):
        av = [int(x * WEIGTHS_PRE[W_PRE_1] + y * WEIGTHS_PRE[W_PRE_2]) 
                for x, y in zip(p1, p2)]

        pre_avg.append(av)
        
        red.append([int(av[0] + av[1] / 2), 
                    int(av[1] / 2 + av[2] + av[3] / 2), 
                    int(av[3] / 2 + av[4])])
        
    return pre_avg, red

def calc_q_from_pre(pre_1, pre_2):
    
    pre_avg, red = calc_pre_avg(pre_1, pre_2)
    
    ap, var, var2, l_max, l_min = calc_ap_from_avg_pred(red)
    
    trip = [ v for a, v in zip(ap, var) if len(a) == 3 ]
    doub = [ v for a, v in zip(ap, var2) if len(a) == 2 ]
    
    ord = []
    alt_ap = []
    
    for a, v, v2, ma, mi, r, i in zip(ap, var, var2, l_max, l_min, red, range(len(ap))):
        if len(a) == 3:
            o = len([t for t in trip if t <= v]) - 1
            
            if len([t for t in trip if t == v]) > 0:
                o -= len([ va2 for va, va2 in zip(var, var2) if va == v and va2 > v2])
                
            ord.append(o + len(doub) + 1)
            alt_ap.append(COMPLEMENT[INDEX_TO_VAL[r.index(mi)]])
            
        elif len(a) == 2:
            o = len([d for d in doub if d <= v2]) - 1
            
            if len([t for t in doub if t == v2]) > 0:
                o -= len([ va2 for va, va2 in zip(var, var2) if va2 == v2 and va > v])
            
            ord.append(o + 1)
            alt_ap.append(INDEX_TO_VAL[r.index(ma)])
        else:
            ord.append(0)
            alt_ap.append(a)
            
    final_q = ap
            
#    if len(trip) == 0:
#        if len(doub) > 7:
#            to_red = len(doub) - 7 
#            for q, o, aa in zip(final_q, ord, alt_ap):
                
#    else:
        
    
    return ap, var, var2, pre_avg, red, ord, alt_ap, final_q
    