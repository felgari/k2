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

"""Class to get and store cl data.
"""

import os
import glob

from ctes import *
from kscrap import KScrap
from kfiles import extract_list_text

class ClDat(object):
    
    def __init__(self, index = DEFAULT_INDEX, path = DATA_PATH):
        
        self._index = index
        self._b1 = []
        self._a2 = []
        self._path = path
                
    def load(self):
        
        if self._index != NO_READ_INDEX:
            
            print "Looking for cl data ..."
        
            # Try read data from a local file.
            file_name = self._get_file_to_read()
            self.read_cldata(file_name)
                
            # If not read from local, retrieve from external source.
            if not self.loaded:
                self._b1, self._a2 = KScrap.scrap_cl_data()
                
                if self.loaded:
                    self._save_cldata()
                    
                    print "Cl data retrieved successfully."
                else:
                    # If data isn't retrieved, update the index with the value 
                    # received.
                    self._index = index
                    
                    print "ERROR: Cl data not retrieved."
                
    def _get_file_to_read(self):
        
        file_name = ''
        
        if self._index != DEFAULT_INDEX:
            file_name = PREFIX_CL_FILE_NAME + self._index + SCRAPPED_DATA_FILE_EXT
        else:
            cl_files = glob.glob("%s*" % PREFIX_CL_FILE_NAME)
            
            if len(cl_files):
            
                cl_files.sort()
            
                file_name = cl_files[-1]         
            
        return file_name
                
    def read_cldata(self, file_name):
        
        lines = []   
        
        full_path_name = os.path.join(self._path, file_name)
        
        if len(full_path_name):
            if self._index != NO_READ_INDEX:
                print "Reading data from file: %s" % full_path_name
            
            try:
                with open(full_path_name, "r") as f:
                    for l in f:
                        
                        # Process text line.        
                        l_txt = l[:-1].strip()
                        
                        if len(l_txt):    
                                          
                            if l_txt.find(B1_TEXT) >= 0:
                                
                                l_text = extract_list_text(l_txt, NUM_COLS_CL)
                                
                                for l in l_text:
                                    self._b1.append([l[i] for i in CL_ORDER])
                                
                                if self._index != NO_READ_INDEX:
                                    print "Read %dx%d from file for B1" % \
                                        (len(self._b1), len(self._b1[0]))
                                
                            elif l_txt.find(A2_TEXT) >= 0:
                                
                                l_text = extract_list_text(l_txt, NUM_COLS_CL)
                                
                                for l in l_text:
                                    self._a2.append([l[i] for i in CL_ORDER])
                                    
                                if self._index != NO_READ_INDEX:
                                    print "Read %dx%d from file for A2" % \
                                        (len(self._a2), len(self._a2[0]))
                                    
            except IOError as ioe:
                print "ERROR: Reading file '%s'" % full_path_name  
                self._b1 = []
                self._a2 = []
        else:
            print "No file found to read cl."
            
    def _save_cldata(self):
        
        out_file_name = PREFIX_CL_FILE_NAME + self._index + SCRAPPED_DATA_FILE_EXT
        
        full_path_name = os.path.join(self._path, out_file_name)
        
        try:
            
            with open(full_path_name, 'w') as f:
            
                f.write("%s %s %s\n\n" % (B1_TEXT, SCR_TXT_DELIM, str(self._b1)))
                f.write("%s %s %s\n" % (A2_TEXT, SCR_TXT_DELIM, str(self._a2))) 
            
            print "Data scrapped saved in: %s" % full_path_name
            
        except IOError as ioe:
             print "Error saving file: '%s'" % full_path_name  
             
    def b1_data(self, name):
        
        for c in self._b1:
            if c[CL_NAME_COL] == name:
                return c
            
        return []
    
    def a2_data(self, name):
        
        for c in self._a2:
            if c[CL_NAME_COL] == name:
                return c
            
        return []
        
    @property
    def b1(self):
        return self._b1
    
    @property
    def a2(self):
        return self._a2
    
    @property
    def index(self):
        return self._index
    
    @property
    def loaded(self):
        return len(self._b1) and len(self._a2)