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

def get_second_index(index_maxi, index_mini):
        
    indexes = [0, 1, 2]
    
    indexes.remove(index_maxi)
    indexes.remove(index_mini)   
    
    return indexes[0]

def calc_ap_base(data):
    """Get the ap for each row. """
    
    print("Calculating ap ...")
    
    base = []
    
    for d in data:       
        values = [ int(x) for x in d ]
        
        if sum(values) > AP_MIN_PERCENT:
        
            maxi = max(values)
            index_maxi = values.index(maxi)
            
            mini = min(values)
            index_mini = values.index(mini)
            
            index_mid = get_second_index(index_maxi, index_mini)
            
            if maxi >= HIST_MAX_P: # One clear option
                new_base = CURRENT_MAX[index_maxi]           
            elif mini <= AP_MIN_VAL_P: # Three options.
                new_base = NAMES_AP_STR
            else:   # Two bigger options.                            
                new_base = CURRENT_MAX[index_maxi] + CURRENT_MAX[index_mid] 
                    
            if new_base == MAX_IS_SECOND:
                if mini > AP_MIN_VAL_P:
                    new_base = NAMES_AP_STR
                else:
                    new_base += CURRENT_MAX[index_mid]
                    
            try:
                base.append(AP_CONV[new_base])
            except KeyError:
                base.append(new_base)
                
        else:
            base.append(MAX_IS_SECOND)
            
    return base

def calc_q(rep_ap, res_1, res_2):
    
    q = []
    
    for i in range(len(rep_ap)):
        
        if rep_ap[i] == TREND_3:
            
            a = ""
            
            for j in range(len(rep_ap[i])):
                if ( rep_ap[i][j] in res_1[i] ) or ( rep_ap[i][j] in res_2[i] ):
                    a += rep_ap[i][j]  
                    
            if a == AP_UNDEF_VAL or a == TREND_3:
                a = TREND_2 
            
            q.append(a)
        else:
            q.append(rep_ap[i])
    
    return q

def calc_ap(avg):
    
    ap = []
    var = []
    
    for a in avg:
        
        if a[IDX_FIRST_VAL] >= AP_FIRST_ENO_VAL:
            val = FIRST_VAL
            
        elif a[IDX_FIRST_VAL] >= AP_FIRST_MIN_VAL:    
            if a[IDX_THIRD_VAL] < AP_THIRD_IGN_VAL:
                val = FIRST_VAL + SECOND_VAL
            else:
                val = AP_ALL_VAL
                
        elif a[IDX_THIRD_VAL] >= AP_THIRD_MIN_VAL:
            val = THIRD_VAL
        else:
            if a[IDX_FIRST_VAL] < AP_FIRST_IGN_VAL:
                val = SECOND_VAL + THIRD_VAL
            else:
                val = AP_ALL_VAL  
            
        ap.append(val)
        
        if len(val) > 1:
            var.append('{:.2f}'.format(np.var(a)))
        else:
            var.append(VAR_ZERO)
    
    return ap, var

def calc_q_from_pre(pre_1, pre_2):
    
    pre_avg = []
    red = []
    l_min = []
    l_max = []
    l_min_pos = []
    l_max_pos = []
    
    for p1, p2 in zip(pre_1, pre_2):
        av = [int(x * WEIGTHS_PRE[W_PRE_1] + y * WEIGTHS_PRE[W_PRE_2]) \
              for x, y in zip(p1, p2)]
        pre_avg.append(av)
        
        red.append([int(av[0] + av[1]/2), \
                    int(av[1]/2 + av[2] + av[3]/2), \
                    int(av[3]/2 + av[4])])
    
    for r in red:
        l_min.append(min(r))
        l_max.append(max(r))
        
    l_min_sorted = sorted(l_min, reverse=True)
    l_max_sorted = sorted(l_max, reverse=True)
    
    for r in red:
        l_min_pos.append(l_min_sorted.index(min(r))+1)
        l_max_pos.append(l_max_sorted.index(max(r))+1)
    
    ap, var = calc_ap(red)
    
    return ap, var, pre_avg, red, l_min, l_max, l_min_pos, l_max_pos
    