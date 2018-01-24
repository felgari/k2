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

"""Class to get res by difference of positions.
"""

from ctes import *
from kfiles import read_res_file
from clda import ClDat

class ResDiffPos(object):
    
    def __init__(self, cl = None):
        
        self._b1_dif = {}
        self._a2_dif = {}
        self._cl = cl
        
    @property
    def b1(self):
        return self._b1_dif
    
    @property
    def a2(self):
        return self._a2_dif
        
    def _dict_from_cl(self, cl_data):
        
        di = {}
        
        for c in cl_data:
            di.update( { c[CL_NAME_COL] : c[CL_POS_COL] } )
            
        return di
        
    def _calc_from_res(self, res_file_name, cl_data):
        
        final_dif = {}
        
        cl_dict = self._dict_from_cl(cl_data)
        
        res = read_res_file(res_file_name)
        
        for r in res:
            name1 = r[R_NAME_1_COL]
            name2 = r[R_NAME_2_COL]
            m = r[R_M_COL]
            
            dif = cl_dict[name1] - cl_dict[name2]
            
            sum = SUM_DIF_POS[m]
            
            try:
                val = final_dif[dif]
                
                new_val = [ val[i] + sum[i] for i in range(len(val))]
                
                final_dif.update( {dif: new_val} )
            except KeyError:
                final_dif.update( {dif: sum} )
        
        return final_dif
        
    def calculate(self):
        
        if not self._cl:
            self._cl = ClDat()
            
            self._cl.load()
            
        if self._cl.loaded:
            self._b1_dif = self._calc_from_res(B1_RES_FILE, self._cl.b1)
            
            self._a2_dif = self._calc_from_res(A2_RES_FILE, self._cl.a2)
        else:
            print("ERROR: Differences by positions no calculated, Cl data not loaded.")
            
    def trend(self, pos1, pos2, elt_type):
        
        values = []
        
        dif = pos1 - pos2

        for n in range(dif - DIF_RANGE, dif + DIF_RANGE + 1):
            
            if elt_type == TYPE_1_COL:
                dif_data = self._b1_dif
            else:
                dif_data = self._a2_dif
                
            try:
                val = dif_data[n]
                
                if len(values):
                    values = [ values[i] + val[i] for i in range(len(val))]
                else:
                    values = val
            except KeyError:
                pass
            
        s = sum(values)    
        
        return [ int((v/float(s))*100) for v in values]