# -*- coding: utf-8 -*-

# Copyright (c) 2016 Felipe Gallego. All rights reserved.
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

"""Class to get average pos.
"""

import datetime
import os

from ctes import *
from clda import ClDat
from kfiles import save_data_to_csv

class AvPos(object):
    
    def __init__(self):
        
        self._dir = None
        
        self._cl_files = []
        
        self._cl_files_order = []
        
        self._avpos = {}
        
    def avpos(self, name):
        return self._avpos[name]
    
    def trend(self, name):
        
        val = self._avpos[name]
        
        val = val[:-AVP_LAST_POS]
        
        if len(val) > 0:
            tr = sum(val) / float(len(val))
        else:
            return AVPOS_TREND_NONE
        
        if tr > val[-1]:
            return AVPOS_TREND_UP
        else:
            return AVPOS_TREND_DOWN
        
    def _compose_dir_name(self):
        
        now = datetime.datetime.now()
        
        first_year = now.year
        
        if now.month < REF_MONTH_COMP_STOP:
            first_year = first_year - 1
            
        self._dir = str(first_year - 2000) + "-" + str(first_year + 1 - 2000)
    
    def _get_cl_files(self, dir):
        
        print "Searching cl files in: %s" % dir
        
        return [fn for fn in os.listdir(dir) 
                    if fn.startswith(PREFIX_CL_FILE_NAME)]
    
    def _extract_order(self, file_name):
        
        return int(os.path.splitext(file_name)[0][len(PREFIX_CL_FILE_NAME):])
        
    def _compile_cl(self):
        
        self._compose_dir_name()
        
        self._cl_files = self._get_cl_files(self._dir)
        
        self._cl_files_order = \
            [ self._extract_order(fn) for fn in self._cl_files ]
            
    def _add_cl(self, avpos, cldata):
        
        for c in cldata:
            
            name = c[CL_NAME_COL]
            pos = c[CL_POS_COL]

            found = False
            
            for a in avpos:
                
                if a[AVPOS_NAME_COL] == name:
                    a.append(pos)
                    found = True
                    break
                
            if not found:
                avpos.append([name, pos])
            
        return avpos
        
    def calculate(self):
        
        avpos = []
        
        # Compile files with cl.
        self._compile_cl()
        
        # Process the files sorted by name.
        files_sorted = sorted(self._cl_files_order)
        
        for fs in files_sorted:
            idx = self._cl_files_order.index(fs)
            
            clda = ClDat(NO_READ_INDEX)
            
            full_file_name = self._cl_files[idx]
            
            clda.read_cldata(full_file_name)
            
            avpos = self._add_cl(avpos, clda.b1)
            avpos = self._add_cl(avpos, clda.a2)
            
        save_data_to_csv(AVPOS_FILE, avpos)
        
        for a in avpos:
            self._avpos.update( { a[0] : a[1:] } )
            
            