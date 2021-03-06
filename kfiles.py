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

"""Common functions to read and write files.
"""

import csv
import os

from ctes import *

def read_input_file(input_file_name):
                
    data = []
    
    full_path_name = os.path.join(DATA_PATH, input_file_name)
    
    print("Reading local file: %s" % full_path_name)

    try:
        with open(full_path_name, 'rt') as f:
            
            reader = csv.reader(f)
        
            for row in reader:
                if row[0].isdigit():
                    data.append(row)
                else:
                    print("Ignoring line in file %s, maybe a header: %s" %
                        (full_path_name, row))
        
    except csv.Error:
        print("ERROR: reading file %s" % full_path_name)
        data = []
    except IOError:
        print("ERROR: reading file %s" % full_path_name)
        data = []
        
    if len(data):
        print("Read: %dx%d" % (len(data), len(data[0])))
    else:
        print("ERROR: No data read.")
            
    return data
    
def read_res_file(input_file_name):
                
    res_data = []
    
    full_path_name = os.path.join(DATA_PATH, input_file_name)
    
    print("Reading res file: %s" % full_path_name)

    try:
        with open(full_path_name, 'rt') as f:
            
            reader = csv.reader(f)
        
            for row in reader:
                
                # Ignore header.
                if row[R_J_COL].isdigit():
                
                    red_row = [row[i] for i in RES_ELEMENTS]
                    
                    res_data.append(red_row)
        
    except csv.Error:
        print("ERROR: reading file %s" % full_path_name)
    except IOError:
        print("ERROR: reading file %s" % full_path_name)
        
    if len(res_data):
        print("Read: %dx%d" % (len(res_data), len(res_data[0])))
            
    return res_data

def extract_list_text(txt, num):
    
    the_list = []
    
    pos = txt.find(SCR_TXT_DELIM)
    txt_red = txt[pos + 1:].strip()
    
    lst_from_txt = txt_red.translate(str.maketrans(dict.fromkeys("[],\'"))).split()

    n = 0
    new_list = []
    for elt in lst_from_txt:
        if elt.isdigit():
            new_list.append(int(elt))
        else:
            new_list.append(elt)
            
        n += 1
        
        if n == num:
            the_list.append(new_list)
            new_list = []
            n = 0
    
    return the_list   

def save_file_resm(out_file_name, index, loc, vis, res, size):
    
    the_size = int(size / 2)
    
    if len(loc) == len(vis) and len(vis) == len(res):
    
        full_path_name = os.path.join(DATA_PATH, out_file_name)
        
        print("Saving res file: %s" % full_path_name)
        
        try:
            
            with open(full_path_name, 'w') as f:
        
                for i in range(len(index)):
                    
                    for j in range(the_size):
                        
                        pos = res[i * the_size + j].find('-')
                        
                        if pos > 0:
                            loc_v = int(res[i * the_size + j][:pos])
                            vis_v = int(res[i * the_size + j][pos+1:])
                            
                            if loc_v > vis_v:
                                lv = MAX_IS_FIRST
                            elif loc_v == vis_v:
                                lv = MAX_IS_SECOND
                            else:
                                lv = MAX_IS_THIRD
        
                            f.write("%s,%s,%s,%s,%d,%d,%s\n" % 
                                    (index[i], 
                                     NAMES_CONVERT[loc[i * the_size + j]], 
                                     NAMES_CONVERT[vis[i * the_size + j]], 
                                     res[i * the_size + j], 
                                     loc_v, vis_v, lv))
                        else:
                            break
        
        except IOError as ioe:
             print("Error saving file: '%s'" % full_path_name) 
             
    else:     
        print("Error length of date is different: %d %d %d" % 
              (len(loc), len(vis), len(res)))

def save_data_to_csv(out_file_name, data, path = DATA_PATH):
    
    full_path_name = os.path.join(path, out_file_name)
    
    try:

        with open(full_path_name, 'w') as f:        
            for d in data:            
                f.write("%s\n" % CSV_DELIMITER.join(str(e) for e in d))
        
        print("File saved: %s" % full_path_name)
           
    except IOError as ioe:
         print("Error saving file: '%s'" % full_path_name)
         
def save_all(k, extm, p, p_rf, ap_rf, p_nn, ap_nn, pre_avg, index):
    
    out_file_name = OUTPUT_FILE_PREFIX + index + OUTPUT_FILE_NAME_EXT
    
    full_path_name = os.path.join(DATA_PATH, out_file_name)
    
    print("Saving all data to: %s" % full_path_name)
    
    try:

        with open(full_path_name, 'w') as f:  
                  
            for i, k_elt in enumerate(k):    
                
                row = [k_elt[K_NAME_1_COL], k_elt[K_NAME_2_COL]] + extm[i] + \
                    p[i] + p_rf[i] + p_nn[i] + pre_avg[i] + [ap_nn[i]]
                       
                f.write("%s\n" % CSV_DELIMITER.join(str(e) for e in row))
        
        print("File saved: %s" % full_path_name)
           
    except IOError as ioe:
         print("Error saving file: '%s'" % full_path_name)
         
def save_all_data(k, extd, ap, pre_1, pre_2, pre_avg, avg_red, 
                  var, var2, ord, alt_ap, final_q, rep_ap, the_trend):

    out_file_name = OUTPUT_FILE_PREFIX + k.index + OUTPUT_FILE_NAME_EXT
    
    full_path_name = os.path.join(DATA_PATH, out_file_name)
    
    print("Saving all data to: %s" % full_path_name)
    
    try:

        with open(full_path_name, 'w') as f:  
            
            f.write("%s\n" % CSV_DELIMITER_TAB.join(str(e) for e in OUT_COLS))
            
            for i in range(len(k.k)):  
                if i >= len(the_trend):
                    the_trend.append([0, 0, 0])

                row = [ 
    #                extd.lm[i][0], extd.lm[i][1], extd.lm[i][2], \
    #                extd.ve[i][0], extd.ve[i][1], extd.ve[i][2], \
    #               extd.qu[i][0], extd.qu[i][1], extd.qu[i][2], \
    #               extd.q1[i][0], extd.q1[i][1], extd.q1[i][2], \
    #                extd.cq[i][0], extd.cq[i][1], extd.cq[i][2], \
    #                extd.cqp[i][0], extd.cqp[i][1], extd.cqp[i][2],
                    extd.mean[i][0], extd.mean[i][1], extd.mean[i][2],
                    the_trend[i][0], the_trend[i][1], the_trend[i][2],
                    rep_ap[i]
                    #,pre_1[i], pre_2[i], pre_avg[i], avg_red[i], 
                    #var[i], var2[i], ap[i], alt_ap[i], ord[i], final_q[i]
                    ]
                       
                f.write("%s%s%s%s%s\n" % ( k.k[i][NAME_LO_COL], CSV_DELIMITER_TAB,
                                   k.k[i][NAME_VI_COL], CSV_DELIMITER_TAB,
                                   CSV_DELIMITER_TAB.join(str(e) for e in row)))
            
        print("File with all data saved in: %s" % full_path_name)
           
    except IOError as ioe:
         print("Error saving file: '%s'" % full_path_name)

    