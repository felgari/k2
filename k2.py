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

"""Main module, predictions made with local data and data scrapped from 
web pages.
"""

import sys

from ctes import *
from kparser import ProgramArgumentsException, ProgramArguments
from kdat import KDat
from clda import ClDat
from resd import retrieve_res
from extd import ExtD
from ap import calc_ap_base
from kfiles import save_all_data 
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
            print "Retrieving of res not asked, using existing res ..."
            
        extd = ExtD(k.index)
        
        extd.load()
    else:
        print "Error loading k ..."
        success = False
        
    return success, k, cl, extd

def main(progargs):
    """Main function.
    """    
    
    print "Here we go ...!!!"
        
    success, k, cl, extd = retrieve_data(progargs.index)
    
    if success:
        ap = calc_ap_base(extd.mean)
          
        rep_ap = do_report(k.index, k.k, cl, None, None, extd.mean)
        
        save_all_data(k, extd, ap, rep_ap)
        
    else:
        print "Source data couldn't be loaded, no calculations were made."
        
    print "Program finished."
    
    return 0

# Where all begins ...
if __name__ == "__main__":
    
    try:
        # Object to process the program arguments.
        progargs = ProgramArguments()
        
        sys.exit(main(progargs))   
    except ProgramArgumentsException as pae:
        print pae       
