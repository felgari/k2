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

from ctes import *
from resd import load_res
from clda import ClDat
from pred import eval_predict
from kfiles import save_data_to_csv

def get_indexes_to_add(sco, sco_list):
    
    lo_index = RES_LO_THIRD
    lo_evol = RES_LO_FIRST_AND_FIRST
    vi_index = RES_VI_FIRST
    vi_evol = RES_VI_THIRD_AND_THIRD
    
    if sco[0] > sco[1]:
        
        lo_index = RES_LO_FIRST
        vi_index = RES_VI_THIRD
        
        if len(sco_list) > 0:
            first_sco = sco_list[0]
            
            if first_sco[0] > first_sco[1]:
                lo_evol = RES_LO_FIRST_AND_FIRST
                vi_evol = RES_VI_THIRD_AND_THIRD
            else:
                lo_evol = RES_LO_THIRD_AND_FIRST
                vi_evol = RES_VI_FIRST_AND_THIRD
        
    elif sco[0] == sco[1]:
        
        lo_index = RES_LO_SECOND
        vi_index = RES_VI_SECOND
        
        if len(sco_list) > 0:
            first_sco = sco_list[0]
            
            if first_sco[0] > first_sco[1]:
                lo_evol = RES_LO_FIRST_AND_SECOND
                vi_evol = RES_VI_THIRD_AND_SECOND
            else:
                lo_evol = RES_LO_THIRD_AND_SECOND
                vi_evol = RES_VI_FIRST_AND_SECOND
        
    else:
        
        if len(sco_list) > 0:
            first_sco = sco_list[0]
            
            if first_sco[0] > first_sco[1]:
                lo_evol = RES_LO_FIRST_AND_THIRD
                vi_evol = RES_VI_THIRD_AND_FIRST
            else:
                lo_evol = RES_LO_THIRD_AND_THIRD
                vi_evol = RES_VI_FIRST_AND_FIRST
        
    return lo_index, lo_evol, vi_index, vi_evol

def data_calculation(r_group):
    
    group_stats = {}
    elements = []
    
    for r_g in r_group:
        
        for r in r_g:
            
            names = r[RES_NAMES_POS]
            sco = r[RES_SCO_POS]
            sco_list = r[RES_SCO_LST_POS]
            min_list = r[RES_MIN_LST_POS]
            
            try:
                gs_lo = group_stats[names[RES_NAME_LO_POS]]
            except KeyError:
                gs_lo = [0] * RES_STAT_SIZE
                
            try:
                gs_vi = group_stats[names[RES_NAME_VI_POS]]
            except KeyError:
                gs_vi = [0] * RES_STAT_SIZE
                
            lo_index, lo_evol, vi_index, vi_evol = get_indexes_to_add(sco, sco_list)
                
            gs_lo[lo_index] += 1
            gs_lo[lo_evol] += 1
            
            gs_vi[vi_index] += 1
            gs_vi[vi_evol] += 1
                
            group_stats[names[RES_NAME_LO_POS]] = gs_lo
            group_stats[names[RES_NAME_VI_POS]] = gs_vi
            
            s = MAX_IS_THIRD
            
            if sco[0] > sco[1]:
                s = MAX_IS_FIRST
            elif sco[0] == sco[1]:
                s = MAX_IS_SECOND
            
            elements.append([r[RES_J], names[RES_NAME_LO_POS], 
                             names[RES_NAME_VI_POS], s])
        
    return group_stats, elements

def _convert_cl_data(cl_data):
    
    cl_converted = {}
    
    for cl in cl_data:
        name = cl[CL_NAME_COL]
        data = [cl[CL_POS_COL]]
        
        data.extend(cl[CL_NAME_COL+1:])
        
        cl_converted[name] = data
        
    return cl_converted

def generate_data(all_cl, lo_data, vi_data, r):
    
    r_stats, elements = data_calculation(r)
    
    for e in elements:
        j = e[R_J_COL]
        sco = e[R_M_COL]
        
        lo_name = e[R_NAME_1_COL]
        vi_name = e[R_NAME_2_COL]
        
        lo_pos = all_cl[lo_name][CL_POS]
        vi_pos = all_cl[vi_name][CL_POS]
        
        lo_cl = all_cl[lo_name][CL_LO_MIN:CL_LO_MAX + 1]
        vi_cl = all_cl[vi_name][CL_VI_MIN:CL_VI_MAX + 1]
        
        lo_stats = r_stats[lo_name][RES_LO_RANGE[0]:RES_LO_RANGE[1]]
        vi_stats = r_stats[vi_name][RES_VI_RANGE[0]:RES_VI_RANGE[1]]
        
        try:
            lo_elt = lo_data[lo_name]
        except KeyError:
            lo_elt = []
            
        e = [j, sco, vi_pos]
        e.extend(vi_cl)
        e.extend(vi_stats)
        lo_elt.append(e)
        lo_data[lo_name] = lo_elt
        
        try:
            vi_elt = vi_data[vi_name]
        except KeyError:
            vi_elt = []
            
        e = [j, sco, lo_pos]
        e.extend(lo_cl)
        e.extend(lo_stats)
        vi_elt.append(e)
        vi_data[vi_name] = vi_elt

def compile_pred_data(res):
    
    # Compile CL data.
    cl_data = ClDat(SIMUL_CL_INDEX, SIMUL_DATA_PATH)
    
    cl_data.load()
    
    all_cl = _convert_cl_data(cl_data.b1)
    all_cl.update(_convert_cl_data(cl_data.a2))
    
    lo_data = {}
    vi_data = {}
    
    data_num = []
    
    # Compile res data.
    print "Number of groups: %d" % len(res.all_res)
    
    for r in res.all_res:
        print "Group of %d elements." % len(r)
        
        data_num.append(len(r))
        
        generate_data(all_cl, lo_data, vi_data, r)

    return lo_data, vi_data, data_num, cl_data

def simul_data(the_data, train_num, cl_names):
    
    simul_resul = []
    
    k = the_data.keys()
    
    for name in cl_names:
        data_for_name = the_data[name]
        
        data_for_model = []
        data_for_eval = []
        
        for dn in data_for_name:
        
            if dn[RES_PRED_J_POS] <= train_num:
                data_for_model.append(dn)
            else:
                data_for_eval.append(dn)
                
        rf_score, nn_score = eval_predict(data_for_model, data_for_eval)
            
        print "%s -> Accuracy RF: %f Accuracy NN: %f" % \
            (name, rf_score, nn_score)
            
        simul_resul.append([name, rf_score, nn_score])
        
    return simul_resul

def simul(lo_data, vi_data, data_num, cl_data):
    
    for dn, rd, cl in zip(data_num, RES_DIRS, [cl_data.b1, cl_data.a2]):
        
        num = dn - SIMUL_LAST
        
        train_num = round(num * SIMUL_PERC / 100)
                                  
        chk_num = num - train_num
        
        print "%s -> Total: %d Train: %d Check: %d Pred: %d" % \
            (rd, dn, train_num, chk_num, dn - num)
            
        print "Simulating LO ..."
        lo_simul = simul_data(lo_data, train_num, [e[CL_NAME_COL] for e in cl])
        
        save_data_to_csv(SIMUL_LO_PREFIX_FILE_NAME + rd + OUTPUT_FILE_NAME_EXT,
                         lo_simul, SIMUL_DATA_PATH)
        
        print "Simulating VI ..."
        vi_simul = simul_data(vi_data, train_num, [e[CL_NAME_COL] for e in cl])
        
        save_data_to_csv(SIMUL_VI_PREFIX_FILE_NAME + rd + OUTPUT_FILE_NAME_EXT,
                         vi_simul, SIMUL_DATA_PATH)

def main():
    """Main function.
    """    
    
    print "Here we go ...!!!"
    
    res = load_res()
    
    lo_data, vi_data, data_num, cl_data = compile_pred_data(res)
    
    simul(lo_data, vi_data, data_num, cl_data)

# Where all begins ...
if __name__ == "__main__":
    
    sys.exit(main())   
