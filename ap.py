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
        
        if not int(v):
            ap.append(AP_MID_VAL)
        elif v < AP_VAR_MIN:
            
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

def calculate_alt_ap(ap, alt_ap, ord, trip_idxs, n_trip, doub_idxs, n_doub, ref_ap):
    
    final_q = [ a for a in ap ]
    
    if trip_idxs:
        mi = min([ord[i] for i in trip_idxs])
        for i in range(n_trip - ref_ap[AP_TR_IDX]):
            idx = ord.index(mi)
            final_q[idx] = alt_ap[idx]
            doub_idxs.append(mi)
            mi += 1

    if doub_idxs:
        mi = min(ord[i] for i in doub_idxs)
        for i in range(n_doub - ref_ap[AP_DO_IDX]):
            idx = ord.index(mi)
            final_q[idx] = alt_ap[idx]
            final_q[mi] = alt_ap[mi]
            mi += 1
        
    return final_q

def calculate_final_q(ap, alt_ap, ord):
    
    trip_idxs = [ i for i in range(len(ap)) if len(ap[i]) == TR_SIZE ]
    n_trip = len(trip_idxs)
    
    doub_idxs = [ i for i in range(len(ap)) if len(ap[i]) == DO_SIZE ]
    n_doub = len(doub_idxs)
    
    if n_trip > 1: 
        if n_trip + n_doub > sum(AP_3): # AP_4
            final_q = calculate_alt_ap(ap, alt_ap, ord,
                                       trip_idxs, n_trip, doub_idxs, n_doub, 
                                       AP_4)
            
        else: # AP_3
            final_q = calculate_alt_ap(ap, alt_ap, ord,
                                       trip_idxs, n_trip, doub_idxs, n_doub, 
                                       AP_3)
    else: # AP_2
        final_q = calculate_alt_ap(ap, alt_ap, ord,
                                   trip_idxs, n_trip, doub_idxs, n_doub, 
                                   AP_2)
        
    return final_q

def calc_q_from_pre(pre_1, pre_2):
    
    pre_avg, red = calc_pre_avg(pre_1, pre_2)
    
    ap, var3, var2, l_max, l_min = calc_ap_from_avg_pred(red)
    
    trip = [ v3 for a, v3 in zip(ap, var3) if len(a) == TR_SIZE ]
    doub = [ v2 for a, v2 in zip(ap, var2) if len(a) == DO_SIZE ]
    
    ord = []
    alt_ap = []
    
    for a, v3, v2, ma, mi, r, i in zip(ap, var3, var2, l_max, l_min, red, range(len(ap))):
        if len(a) == TR_SIZE:
            o = len([t for t in trip if t <= v3]) - 1
            
            if len([t for t in trip if t == v3]):
                o -= len([ va2 for va3, va2 in zip(var3, var2) if va3 == v3 and va2 > v2])
                
            ord.append(o + len(doub) + 1)
            alt_ap.append(COMPLEMENT[INDEX_TO_VAL[r.index(mi)]])
            
        elif len(a) == DO_SIZE:
            o = len([d for d in doub if d <= v2]) - 1
            
            if len([t for t in doub if t == v2]):
                o -= len([ va2 for va3, va2 in zip(var3, var2) if va2 == v2 and va3 > v3])
            
            ord.append(o + 1)
            alt_ap.append(INDEX_TO_VAL[r.index(ma)])
        else:
            ord.append(0)
            alt_ap.append(a)
            
    d = len(doub)
    t = len(trip)
    
    if ( d == AP_2[AP_DO_IDX] and t == AP_2[AP_TR_IDX] ) or \
        ( d == AP_3[AP_DO_IDX] and t == AP_3[AP_TR_IDX] ) \
        or ( d == AP_4[AP_DO_IDX] and t == AP_4[AP_TR_IDX] ):
        final_q = ap
    else:
        final_q = calculate_final_q(ap, alt_ap, ord)
    
    return ap, var3, var2, pre_avg, red, ord, alt_ap, final_q
    