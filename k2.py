#!/usr/bin/env python3
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

"""Main module, predictions made with local data and data scrapped from 
web pages.
"""

import sys

from ctes import *
from kparser import ProgramArgumentsException, ProgramArguments
from kdat import KDat
from clda import ClDat
from resd import retrieve_res, calculate_res, calc_res_per
from extd import ExtD
from pred import predict_k
from ap import calc_q_from_pre
from kfiles import save_all_data, read_res_file
from report import do_report

def retrieve_data(index):
    
    success = True
    cl = None
    extd = None
        
    k = KDat(index)
    
    k.load()
    
    if k.loaded:
        
        cl = ClDat(k.index)
        
        cl.load()
        
        if progargs.retrieve_res:
            retrieve_res()
        else:
            print("Retrieving of res not asked, using existing res ...")
            
        extd = ExtD(k.index)
        
        extd.load()
    else:
        print("Error loading k ...")
        success = False
        
    return success, k, cl, extd

def main(progargs):
    """Main function.
    """    
    
    print("Here we go ...!!!")
        
    success, k, cl, extd = retrieve_data(progargs.index)
    
    if success:       
        b1_res = read_res_file(B1_RES_FILE)    
    
        a2_res = read_res_file(A2_RES_FILE)
        
        b1_per = calc_res_per(b1_res, cl, B1_TYPE)

        a2_per = calc_res_per(a2_res, cl, A2_TYPE)
        
        pre_1, sco_1, pre_2, sco_2 = predict_k(k.k, cl, b1_res, a2_res)
          
        rep_ap, trend_1, trend_2 = do_report(k.index, k.k, cl, 
                                         b1_res, a2_res, b1_per, a2_per, 
                                         extd, pre_1, sco_1, pre_2, sco_2)
        
        ap, var, var2, pre_avg, avg_red, ord, alt_ap = \
            calc_q_from_pre(pre_1, pre_2)
        
        save_all_data(k, extd, ap, pre_1, pre_2, pre_avg, avg_red, 
                      var, var2, ord, alt_ap)
        
    else:
        print("Source data couldn't be loaded, no calculations were made.")
        
    print("Program finished.")
    
    return 0

# Where all begins ...
if __name__ == "__main__":
    
    try:
        # Object to process the program arguments.
        progargs = ProgramArguments()
        
        sys.exit(main(progargs))   
    except ProgramArgumentsException as pae:
        print(pae)
