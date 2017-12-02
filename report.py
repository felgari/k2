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

"""Script to report results.
"""

import sys
import os
import csv

from ctes import *
from avpos import AvPos
from resdifpos import ResDiffPos
from aptrend import ApTrend
from kfiles import read_input_file, read_res_file
from utils import get_matchings

def report_file_name(index):    
    
    return REP_OUT_FILE_PREFIX + index + REP_OUT_FILE_EXT     

def do_report(index, k_data, cl, b1_res, a2_res, ex_mean, pre_rf = None, pre_df = None): 
    
    print "Generating report ..."
    
    rep_ap = []
    
    res_1 = []
    
    res_2 = []
    
    out_file_name = os.path.join(DATA_PATH, report_file_name(index))
    
    avp = AvPos() 

    avp.calculate()   
    
    rdp = ResDiffPos(cl)
    
    rdp.calculate()
    
    aptr = ApTrend()
    
    print "Saving to file: %s" % out_file_name
                    
    try:    
    
        with open(out_file_name, 'w') as f: 
            idx = 0
        
            for k_elt in k_data:
                k_name_1 = k_elt[K_NAME_1_COL]
                k_name_2 = k_elt[K_NAME_2_COL]
                
                data = b1_res
                elt_type = TYPE_1_COL
                cl_1 = cl.b1_data(k_name_1)
                cl_2 = cl.b1_data(k_name_2)
                
                if len(cl_1) == 0:
                    data = a2_res
                    elt_type = TYPE_2_COL
                    cl_1 = cl.a2_data(k_name_1)
                    cl_2 = cl.a2_data(k_name_2)
                    
                mat1, val_res1 = get_matchings(k_name_1, data, True)
                mat2, val_res2 = get_matchings(k_name_2, data, False)
                
                f.write("%s\n" % GEN_SEP)
                
                f.write("-> %s (%s) - %s (%s)\n" % \
                        (k_name_1, cl_1[CL_POS_COL], k_name_2, cl_2[CL_POS_COL]))
                    
                if pre_rf:
                    f.write("Pre RF: %s\n" % pre_rf[idx])
                    
                if pre_df:
                    f.write("Pre DF: %s\n" % pre_df[idx])
                    
                f.write("Ext %s\n" % ex_mean[idx])
                
                trend = rdp.trend(cl_1[CL_POS_COL], cl_2[CL_POS_COL], elt_type)
                
                f.write("Trend %s\n" % trend)
                
                name_1_trend = avp.trend(k_name_1)
                name_2_trend = avp.trend(k_name_2)
                
                f.write("Pos. %s: %s %s\n" % \
                        (k_name_1, avp.avpos(k_name_1), name_1_trend))
                f.write("Pos. %s: %s %s\n" % \
                        (k_name_2, avp.avpos(k_name_2), name_2_trend))
                
                if len(trend) > 0:
                    ap_t = aptr.calculate_ap(trend, name_1_trend, 
                                             name_2_trend, int(cl_1[CL_POS_COL]), 
                                             int(cl_2[CL_POS_COL]))
                    
                    rep_ap.append(ap_t)
                    
                    res_1.append(val_res1)
                    res_2.append(val_res2)
                    
                    f.write("Ap trend: %s -> %s %s\n" % \
                            (ap_t, val_res1, val_res2))
                    
                    f.write("Pred-> RF: %s NN: %s\n" % \
                            (pre_rf[idx], pre_df[idx]))
                
                f.write("%s\n" % FIRST_SEP)
                
                for m in mat1:
                    if elt_type == TYPE_1_COL:
                        mat_cl = cl.b1_data(m[MAT_NAME_2_COL])
                    else:
                        mat_cl = cl.a2_data(m[MAT_NAME_2_COL])
                    f.write("%s (%s)\n" % (m, mat_cl[CL_POS_COL]))
                    
                f.write("%s\n" % SECOND_SEP)
                
                for m in mat2:
                    if elt_type == TYPE_1_COL:
                        mat_cl = cl.b1_data(m[MAT_NAME_1_COL])
                    else:
                        mat_cl = cl.a2_data(m[MAT_NAME_1_COL])
                    f.write("%s (%s)\n" % (m, mat_cl[CL_POS_COL]))
                    
                idx += 1
                
        aptr.write_data(index)
                    
    except IOError as ioe:
        print "IOError saving file: '%s'" % out_file_name 
    except KeyError as ke:
        print "KeyError saving file: '%s'" % out_file_name
    except IndexError as ie:
        print "IndexError saving file: '%s'" % out_file_name
         
    return rep_ap, res_1, res_2
    
def report_generated(index):
    
    return os.path.exists(report_file_name(index))

if __name__ == "__main__":
    
    if len(sys.argv) == NUM_ARGS:
        sys.exit(do_report(sys.argv[1]))
    else:
        print "The index is needed as argument."