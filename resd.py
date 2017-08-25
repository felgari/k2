#!/usr/bin/env python
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

"""Res data.
"""

import sys
import os
import csv
import glob

NUM_ARGS = 2

from ctes import *
from kdat import KDat
from kscrap import KScrap
import unicodedata as un
    
class Res(object):
    
    _LO = 0
    _VI = 1
    _SCO = 2
    _GO = 3    
    _END = 4
    
    _STATES = [ _LO, _VI, _SCO, _GO, _END ]    
    
    def __init__(self, the_type, the_j):
        
        self._state = Res._LO
        
        self._lo = ''
        self._vi = ''
        self._sco = ''
        self._lo_g = []
        self._vi_g = []
        self._min = []
        self._type = the_type
        self._j = the_j        
        
    def __str__(self):
        return "%s %d - %s %d -> %s" % (self._lo, len(self._lo_g), 
                                        self._vi, len(self._vi_g),
                                        self._min) 
        
    @property
    def next(self):
        self._state = ( self._state + 1 ) % len(Res._STATES)
        
    @property
    def is_lo(self):
        return self._state == Res._LO
    
    @property
    def is_vi(self):
        return self._state == Res._VI    
    
    @property
    def is_sco(self):
        return self._state == Res._SCO 
    
    @property
    def is_go(self):
        return self._state == Res._GO     
    
    @property
    def end(self): 
        return self._state == Res._END 
    
    def set_end(self):
        self._state = Res._END   
        
    @property
    def lo(self):
        return self._lo
    
    @lo.setter
    def lo(self, lo_val):
        self._lo = lo_val    
    
    @property
    def vi(self):
        return self._vi       
    
    @vi.setter
    def vi(self, vi_val):
        self._vi = vi_val 
        
    @property
    def sco(self):
        return self._sco
    
    @sco.setter
    def sco(self, the_sco):
        self._sco = the_sco
        
    @property
    def lo_g(self):
        return self._lo_g
        
    @property
    def vi_g(self):
        return self._vi_g    
    
    @property
    def sum_g(self):
        return len(self._lo_g) + len(self._vi_g) 
    
    @property
    def type(self):
        return self._type
    
    @property
    def j(self):
        return self._j    
    
    def _is_forward(self, g_list):
        return self.sum_g > 0 and len(g_list) > 0 and g_list[0] == 1

    def lo_is_forward(self):
        return self._is_forward(self._lo_g)    
    
    def lo_is_forward_and_w(self):
        return self._is_forward(self._lo_g) and len(self.lo_g) > len(self.vi_g)
            
    def lo_is_forward_and_t(self):
        return self._is_forward(self._lo_g) and len(self.lo_g) == len(self.vi_g)
            
    def lo_is_forward_and_l(self):
        return self._is_forward(self._lo_g) and len(self.lo_g) < len(self.vi_g)   
    
    def vi_is_forward(self):
        return self._is_forward(self._vi_g)                               
    
    def vi_is_forward_and_w(self):
        return self._is_forward(self._vi_g) and len(self.lo_g) < len(self.vi_g)
    
    def vi_is_forward_and_t(self):
        return self._is_forward(self._vi_g) and len(self.lo_g) == len(self.vi_g)  
    
    def vi_is_forward_and_l(self):
        return self._is_forward(self._vi_g) and len(self.lo_g) > len(self.vi_g)         
            
    def _front_recover_back(self, front, back): 
        return len(front) > len(back) and \
            any([ front[i] > back[i] for i in range(len(back)) ])        
            
    def lo_recover(self):
        return self._front_recover_back(self.lo_g, self.vi_g)
    
    def vi_recover(self):
        return self._front_recover_back(self.vi_g, self.lo_g)
    
    def final_in_ext(self):
        
        in_ext = False
        
        dif = abs(len(self._lo_g) - len(self._vi_g))
        
        if dif and min[-dif] > MIN_EXT:
            in_ext = True    
        
        return in_ext
    
    def dif_clear(self):
        
        return abs(len(self._lo_g) - len(self._vi_g)) >= DIF_CLEAR
    
    @staticmethod
    def _extract_sco(line):
    
        pos = line.split(SCO_DELIM)
        
        return int(pos[0]), int(pos[1])  
    
    def add_g(self, line):
        
        lo_g_val, vi_g_val = Res._extract_sco(line)
        
        lo_g_len = len(self._lo_g)
        vi_g_len = len(self._vi_g)
        
        sum_lo_vi_g = lo_g_len + vi_g_len
        
        if lo_g_val > lo_g_len:
            self._lo_g.append(sum_lo_vi_g + 1)
        elif vi_g_val > vi_g_len:
            self._vi_g.append(sum_lo_vi_g + 1)
        else:
            print "Error setting min in %s %s with: %d %d - %d %d" % \
                (self.lo, self.vi, lo_g_val, lo_g_len, vi_g_val, vi_g_len)
        
    def add_m(self, line): 
        self._min.append(int(line))
        
    def add_line(self, lin):
        
        if self.is_lo:
            self.lo = lin
            self.next
        elif self.is_vi:
            self.vi = lin
            self.next
        elif self.is_sco:
            self.sco = lin
            self.next
        elif lin.find(SCO_DELIM) > 0:
            self.add_g(lin)
        elif lin.isdigit():
            self.add_m(lin)
        else:
            self.set_end() 
        
    def check_coherence(self):              

        coherent = True
        
        if not self._lo:
            print "No value for lo."
            coherent = False 
            
        if not self._vi:
            print "No value for vi."
            coherent = False 
            
        if self.sum_g != len(self._min):
            print "g values does not match min ones."            

        return coherent

    __repr__ = __str__
    
class ResData(object):
    
    def __init__(self):
        self._all_res = []
        
    @property
    def all_res(self):
        return self._all_res
    
    @staticmethod
    def _save_res_data(out_file_name, data):
        
        full_path_name = os.path.join(DATA_PATH, out_file_name)
        
        print "Saving file: %s" % full_path_name
        
        try:
            
            with open(full_path_name, 'w') as f:
        
                for d in data:
                    if type(d) is int:
                        f.write("%d\n" % d)
                    else:
                        f.write("%s\n" % 
                                un.normalize('NFKD', d).encode('ascii','ignore'))
        
        except IOError as ioe:
             print "Error saving file: '%s'" % full_path_name  
        
    @staticmethod
    def _scrap_res(max_range, file_dir, url_prefix, data_size): 
        
        for i in range(1, max_range + 1):
            
            i_str = str(i).zfill(2)
            
            file_name = os.path.join(os.getcwd(),
                                     file_dir,
                                     RES_FILE_PREFIX + i_str + INPUT_FILE_NAME_EXT)
            
            if not os.path.exists(file_name):   
                print "Retrieving data for file: %s" % file_name  
                url = url_prefix + i_str   
                data = KScrap.res_scraping(url)
                
                # If data could not be get, exit.
                if len(data) > data_size * 4:                     
                    ResData._save_res_data(file_name, data)
                else:
                    print "Exiting as no data has been retrieved for: %s." % \
                        file_name
                    break                    
      
    @staticmethod 
    def _scrap_res_data():
        
        ResData._scrap_res(MAX_B1, RES_B1_DIR, RE_B1_URL, B1_SIZE / 2)
        
        ResData._scrap_res(MAX_A2, RES_A2_DIR, RE_A2_URL, A2_SIZE / 2)               

    @staticmethod
    def _process_lines(lines, file_type, j):
        
        res_list = []    
        current_res = Res(file_type, j)
        
        for lin in lines:
            
            current_res.add_line(lin)
                
            if current_res.end:
                
                if current_res.check_coherence():
                    res_list.append(current_res)
                    
                    current_res = None
                else:
                    print "Discarded: %s" % current_res
            
                current_res = Res(file_type, j)
                            
                current_res.add_line(lin)
                
        if current_res:
            res_list.append(current_res)
            
        return res_list
    
    @staticmethod
    def _extract_j(file_name):
        
        pos_start = file_name.find(RES_FILE_PREFIX) + len(RES_FILE_PREFIX)
        pos_end = file_name.find('.')
        
        return int(file_name[pos_start:pos_end])
            
    @staticmethod
    def _process_file(file_name, file_type):
        
        lines_pro = []
        
        full_path_name = os.path.join(DATA_PATH, file_name)
        
        j = ResData._extract_j(full_path_name)
        
        with open(full_path_name, 'r') as f:
            for line in f:
                
                # Remove new lines.
                line_wo_nl = line[:-1]
                
                try:
                    # Try to convert the line read.
                    lines_pro.append(SCO_STR_CONVERT[line_wo_nl])
                except KeyError:
                    # If exception, no conversion is needed, just add the line.
                    lines_pro.append(line_wo_nl)  
                    
        # With all the lines read, process them.
        return ResData._process_lines(lines_pro, file_type, j)   
    
    def get_names(self):
        
        names = set()
        
        for ar in self._all_res:
            names.add(ar.lo)
            names.add(ar.vi)
            
        return sorted(list(names)) 
    
    def get_res(self, name, is_lo):
        
        res = []
        
        for ar in self._all_res:
            if is_lo:
                if ar.lo == name:
                    res.append(ar)
            else:
                if ar.vi == name:
                    res.append(ar)            
        return res       
    
    def process_res(self):
        
        for d, t in zip(RES_DIRS, RES_TYPES):
        
            res_files = glob.glob(os.path.join(d, "%s*" % RES_FILE_PREFIX))
            
            for res in res_files:
                
                res_list = ResData._process_file(res, t)
                
                self._all_res.extend(res_list)
                
def save_file(file_name, data):
    
    full_path_name = os.path.join(DATA_PATH, file_name)
    
    data_sorted = sorted(data, key=lambda item: item[0])    
    
    print "Saving %d rows of data in: %s" % (len(data_sorted), full_path_name)
    
    try:                
        with open(full_path_name, 'wb') as fw:
            
            writer = csv.writer(fw, delimiter=',')
    
            # Walk the data.
            for d in data_sorted:
            
                # Write a row.
                writer.writerow(d)   
    except csv.Error as e:
        print "Error writing data in CSV file: '%s'" % full_path_name                
                
    except IOError as ioe:
        print "Error writing CSV file: '%s'" % full_path_name      
                
def generate_res(res):
    
    b1_res = []
    a2_res = []
    
    for r in res:

        len_lo = len(r.lo_g)
        len_vi = len(r.vi_g)
        
        if len_lo > len_vi:
            val = MAX_IS_FIRST
        elif len_lo == len_vi:
            val = MAX_IS_SECOND
        else:
            val = MAX_IS_THIRD
        
        new_row = [r.j, r.lo, r.vi, r.sco, len_lo, len_vi, val]
        
        if r.type == TYPE_1_COL:
            b1_res.append(new_row)
        else:
            a2_res.append(new_row)
            
    save_file(B1_RES_FILE, b1_res)
    save_file(A2_RES_FILE, a2_res)

def process_k_data(index, res):
    
    k_data = KDat(index) 
    
    for k in k_data.k:
        lo_name = k[K_NAME_1_COL]
        vi_name = k[K_NAME_2_COL]
        
        lo_res = res.get_res(lo_name, True)
        lo_n_for = len([r for r in lo_res if r.lo_is_forward()]) * 1.0
        lo_n_for_and_w = len([r for r in lo_res if r.lo_is_forward_and_w()])
        lo_n_for_and_t = len([r for r in lo_res if r.lo_is_forward_and_t()])
        lo_n_for_and_l = len([r for r in lo_res if r.lo_is_forward_and_l()])                        
        lo_n_rec = len([r for r in lo_res if r.lo_recover()])            
                
        vi_res = res.get_res(vi_name, False)
        vi_n_for = len([r for r in vi_res if r.vi_is_forward()]) * 1.0
        vi_n_for_and_w = len([r for r in vi_res if r.vi_is_forward_and_w()])
        vi_n_for_and_t = len([r for r in vi_res if r.vi_is_forward_and_t()])
        vi_n_for_and_l = len([r for r in vi_res if r.vi_is_forward_and_l()])                        
        vi_n_rec = len([r for r in vi_res if r.vi_recover()])  
        
        len_lo_res = len(lo_res) * 1.0
        len_vi_res = len(vi_res) * 1.0
        
        print "- %s - %s" % (lo_name, vi_name)
        print " lo %d%% (%d%% %d%% %d%% - %d%%)" % \
            (int(100.0 * lo_n_for / len_lo_res),
             int(100.0 * lo_n_for_and_w / lo_n_for),
             int(100.0 * lo_n_for_and_t / lo_n_for),
             int(100.0 * lo_n_for_and_l / lo_n_for),
             int(100.0 * lo_n_rec / len_lo_res))
        print " vi %d%% (%d%% %d%% %d%% - %d%%)" % \
            (int(100.0 * vi_n_for / len_vi_res),
             int(100.0 * vi_n_for_and_w / vi_n_for),
             int(100.0 * vi_n_for_and_t / vi_n_for),
             int(100.0 * vi_n_for_and_l / vi_n_for),
             int(100.0 * vi_n_rec / len_vi_res))                
        
def retrieve_res():   
    
    print "Retrieving res ..."
    
    ResData._scrap_res_data()     
    
    res = ResData() 
    
    res.process_res()        
    
    generate_res(res.all_res)  

def analyze_res(index):
    
    res = ResData() 
    
    res.process_res()
    
    process_k_data(index, res)
    
    return 0

if __name__ == "__main__":  
    
    if len(sys.argv) == NUM_ARGS:
        print "Analyzing data. No index must be provided to retrieve data."         
        sys.exit(analyze_res(sys.argv[1]))
    else:
        print "Only retrieving data. An index must be provided to analyze."         
        retrieve_res()