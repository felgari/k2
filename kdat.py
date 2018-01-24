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

"""Class to get and store K data.
"""

import os

from ctes import *
from kfiles import read_input_file
from kscrap import KScrap, ScrapingException

class KDat(object):

    def __init__(self, index = DEFAULT_INDEX):
        
        self._index = index
        self._k = []
        
    def load(self):
        
        if self._index != DEFAULT_INDEX:
            print("Let's go with the index provided: %s ..." % self._index)
            self._read_k()
            
        else:
            print("No index provided, so looking for index and k data ...")
            
        # If not read from local, retrieve from external source.
        if not self.loaded:
            try:
                self._k, self._index = KScrap.k_scraping()
                
                if self.loaded:
                    self._save_k()
                    
                    print("k retrieved successfully for index %s" % self._index)
                    
                else:
                    print("ERROR: k data not retrieved.")
                    
            # If data isn't retrieved, update the index with the value received.
            except ScrapingException as se:
                print("ERROR: %s" % se)
        
    def _read_k(self):
        
        k_file_name = K_FILE_NAME_PREFIX + self._index + INPUT_FILE_NAME_EXT
        
        self._k = read_input_file(k_file_name) 

    def _save_k(self):
        
        success = True
        
        out_file_name = K_FILE_NAME_PREFIX + self._index + INPUT_FILE_NAME_EXT
        
        full_path_name = os.path.join(DATA_PATH, out_file_name)
        
        print("Saving file: %s with %dx%d elements" %
              (full_path_name, len(self._k), len(self._k[0])))
            
        try:
        
            with open(full_path_name, 'w') as f:
            
                for d in self._k:
                    f.write("%s,%s,%s,%s\n" % (d[0], d[1], d[2], d[3]))
            
        except IOError as ioe:
             print("Error saving file: '%s'" % full_path_name)
        
    @property
    def k(self):
        return self._k
    
    @property
    def index(self):
        return self._index
    
    @property
    def loaded(self):
        return len(self._k)
        