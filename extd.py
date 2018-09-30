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

"""Class to store the data used during the calculations.
"""

import os
import numpy as np

from ctes import *
from kfiles import extract_list_text, save_data_to_csv
from kscrap import KScrap

class ExtD(object):
    
    def __init__(self, index):
        
        self._index = index
        self._lm = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self._ve = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self._qu = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self._q1 = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self._cq = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self._cqp = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self._mean = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        
    def __str__(self):
        return "lm: %d ve: %d qu: %d q1: %d cq: %d cqp: %d mean: %d" % \
            (len(self._lm), len(self._ve), len(self._qu), len(self._q1), 
             len(self._cq), len(self._cqp))
        
    @property
    def lm(self):
        return self._lm
    
    @lm.setter
    def lm(self, lm_data):
        self._lm = lm_data  
        
    @property
    def lm_exists(self):
        return len(self._lm) > 0   
        
    @property
    def ve(self):
        return self._ve
    
    @ve.setter
    def ve(self, ve_data):
        self._ve = ve_data  
        
    @property
    def ve_exists(self):
        return len(self._ve) > 0
        
    @property
    def qu(self):
        return self._qu
    
    @qu.setter
    def qu(self, qu_data):
        self._qu = qu_data  
        
    @property
    def qu_exists(self):
        return len(self._qu) > 0
        
    @property
    def q1(self):
        return self._q1
    
    @q1.setter
    def q1(self, q1_data):
        self._q1 = q1_data  
        
    @property
    def q1_exists(self):
        return len(self._q1) > 0 
    
    @property
    def cq(self):
        return self._cq
    
    @cq.setter
    def cq(self, cq_data):
        self._cq = cq_data 
        
    @property
    def cq_exists(self):
        return len(self._cq) > 0 
        
    @property
    def cqp(self):
        return self._cqp
    
    @cqp.setter
    def cqp(self, cqp_data):
        self._cqp = cqp_data 
        
    @property
    def cqp_exists(self):
        return len(self._cqp) > 0  
    
    @property
    def mean(self):
        
        if not len(self._mean):
            self._calc_mean()                                                      
        
        return self._mean
        
    @property
    def ext_data_ok(self):
         
        return len(self._lm) == NUM_ROWS and \
            len(self._ve) == NUM_ROWS and \
            len(self._qu) == NUM_ROWS and \
            len(self._q1) == NUM_ROWS and \
            len(self._cq) == NUM_ROWS and \
            len(self._cqp) == NUM_ROWS

    def _calc_mean(self):
        mean_sources = []
        
        self._mean = []
        
        if sum(self._lm[0]):
            mean_sources.append(self._lm)
        else:
            print("Ignoring lm for mean.")
            
        if sum(self._ve[0]):
            mean_sources.append(self._ve)
        else:
            print("Ignoring ve for mean.")
            
        if sum(self._qu[0]):
            mean_sources.append(self._qu)
        else:
            print("Ignoring qu for mean.")
            
        if sum(self._q1[0]):
            mean_sources.append(self._q1)
        else:
            print("Ignoring q1 for mean.")
            
        if 0:#sum(self._cq[0]):
            mean_sources.append(self._cq)
        else:
            print("Ignoring cq for mean.")
        
        if len(mean_sources) >= 1:
            for i in range(NUM_ROWS):
                new_row = []
                for j in range(NUM_COLS):
                    values = [s[i][j] for s in mean_sources]
                    new_row.append(int(round(np.mean(values))))
                
                self._mean.append(new_row) 
    
    def _read_extd(self):
        
        success = True
        lines = []    
        
        # Reading from local file the rest of data.
        file_name = EXTD_FILE_PREFIX + self._index + SCRAPPED_DATA_FILE_EXT 
        
        full_path_name = os.path.join(DATA_PATH, file_name) 
        
        print("Reading data from file: %s" % full_path_name)
        
        try:
            with open(full_path_name, "r") as f:
                for l in f:
                    
                    # Process text line.        
                    l_txt = l[:-1].strip()
                    
                    if len(l_txt):                  
                        if l_txt.find(LM_TEXT) >= 0:
                            self._lm = extract_list_text(l_txt, NUM_COLS_LM)
                                
                        elif l_txt.find(VE_TEXT) >= 0:
                            self._ve = extract_list_text(l_txt, NUM_COLS_VE)
                                
                        elif l_txt.find(QU_TEXT) >= 0:
                            self._qu = extract_list_text(l_txt, NUM_COLS_QU)
                                
                        elif l_txt.find(Q1_TEXT) >= 0:
                            self._q1 = extract_list_text(l_txt, NUM_COLS_Q1)
                                
                        elif l_txt.find(CQ_TEXT) >= 0:
                            self._cq = extract_list_text(l_txt, NUM_COLS_CQ)
                                
                        elif l_txt.find(CQP_TEXT) >= 0:
                            self._cqp = extract_list_text(l_txt, NUM_COLS_CQ)
                                
        except IOError as ioe:
            print("ERROR: Reading file '%s'" % full_path_name)  
            success = False
            
        return success
    
    def _save_extd(self):
        
        out_file_name = EXTD_FILE_PREFIX + self._index + SCRAPPED_DATA_FILE_EXT
        
        full_path_name = os.path.join(DATA_PATH, out_file_name)
        
        try:
            
            with open(full_path_name, 'w') as f:
            
                f.write("%s %s %s\n\n" % (LM_TEXT, SCR_TXT_DELIM, str(self._lm)))
                f.write("%s %s %s\n\n" % (VE_TEXT, SCR_TXT_DELIM, str(self._ve)))
                f.write("%s %s %s\n\n" % (QU_TEXT, SCR_TXT_DELIM, str(self._qu)))
                f.write("%s %s %s\n\n" % (Q1_TEXT, SCR_TXT_DELIM, str(self._q1)))
                f.write("%s %s %s\n\n" % (CQ_TEXT, SCR_TXT_DELIM, str(self._cq)))
                f.write("%s %s %s\n\n" % (CQP_TEXT, SCR_TXT_DELIM, str(self._cqp)))
            
            print("Data scrapped saved in: %s" % full_path_name)
            
        except IOError as ioe:
             print("Error saving file: '%s'" % full_path_name)  

    def _save_mean(self):
        
        output_file = MEAN_FILE_NAME_PREFIX + self._index + OUTPUT_FILE_NAME_EXT
        
        save_data_to_csv(output_file, self._mean)

    def load(self, force_read_ext = False):
        
        print("Loading external data ...")
        
        if force_read_ext or not self._read_extd():    
            
            KScrap.lm_scraping(self._lm)
            KScrap.ve_scraping(self._ve)
            #KScrap.qu_scraping(self._qu)
            #KScrap.q1_scraping(self._q1, self._index)
            #KScrap.cq_scraping(self._cq, self._cqp)
            
            if self.ext_data_ok:
                self._save_extd()   
                
        self._calc_mean()
        
        self._save_mean()