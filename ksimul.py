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

"""Main module, simulations.
"""

import sys

from resd import load_res, compile_pred_data

def simul(lo_data, vi_data, data_num):
    
    for dn, rd in zip(data_num, RES_DIRS):
        
        print "%d %s" % (dn, rd)
        

def main():
    """Main function.
    """    
    
    print "Here we go ...!!!"
    
    res = load_res()
    
    lo_data, vi_data, data_num = compile_pred_data(res)
    
    simul(lo_data, vi_data, data_num)

# Where all begins ...
if __name__ == "__main__":
    
    sys.exit(main())   
