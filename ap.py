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

def get_second_index(index_maxi, index_mini):
        
    indexes = [0, 1, 2]
    
    indexes.remove(index_maxi)
    indexes.remove(index_mini)   
    
    return indexes[0]

def calc_ap_base(data):
    """Get the ap for each row. """
    
    print "Calculating ap ..."
    
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
                    
            print "%s -> %s" % (values, new_base)
                    
            try:
                base.append(AP_CONV[new_base])
            except KeyError:
                base.append(new_base)
                
        else:
            base.append(MAX_IS_SECOND)
            
    return base