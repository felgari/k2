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

"""Class to scrap web sites.
"""

import requests
from bs4 import BeautifulSoup
import unicodedata as un
import json

from ctes import *

class ScrapingException(Exception):
    
    def __init__(self, msg):
        
        self._msg = msg
        
    def __str__(self):
        return self._msg

class KScrap(object):
    """Scraping on some web pages.
    """
    
    @staticmethod
    def retrieve_page(url):
        """Check connection and retrieving from the url received.
            
        """
        
        bsObj = None
        
        print("Reading page from: %s" % url)
        
        bsObj = BeautifulSoup(requests.get(url).content, "lxml")
        

            
            
                
        return bsObj 
    
    # ------------------------------------- K scraping.        
    @staticmethod
    def _process_k_page( bsObj):
        
        success = True
        
        temp_index = ''
        
        first = []
        second = []
        k_data = []
        table = str.maketrans(dict.fromkeys("b'"))
        
        for cobj in bsObj.findAll(K_COBJ, K_COBJ_DICT):
            for eobj in cobj.findAll(K_EOBJ, K_EOBJ_NAME):
                txt = eobj.get_text().strip()
                txt_norm = un.normalize('NFKD', txt).encode('ascii','ignore').__str__()
                pos2 = txt_norm.find(K_POS_1_SEP)
                pos1 = txt_norm[:pos2].rfind(K_POS_2_SEP)
                temp_index = txt_norm[pos1+1:pos2].strip()
        
        for cobj in bsObj.findAll(K_COBJ_INF, K_COBJ_INF_DICT):
            for eobj in cobj.findAll(K_EOBJ_1, K_EOBJ_1_NAME):
                txt = eobj.get_text().strip()
                txt_norm = un.normalize('NFKD', txt).encode('ascii','ignore').__str__()
                first.append(txt_norm)
                
            for eobj in cobj.findAll(K_EOBJ_2, K_EOBJ_2_NAME):
                txt = eobj.get_text().strip()
                txt_norm = un.normalize('NFKD', txt).encode('ascii','ignore').__str__()
                second.append(txt_norm)
            
        if len(first) == len(second):
            for i, first_it in enumerate(first):
                type_el = TYPE_1_COL
                
                try:               
                    first_name = NAMES_CONVERT[first_it[2:-1]]
                    try:               
                        second_name = NAMES_CONVERT[second[i][2:-1]]
                        
                        k_data.append([str(i), type_el, first_name, second_name])
                    except KeyError:                
                        print("ERROR converting k name: %s" % second[i])
                        success = False
  
                except KeyError:                
                    print("ERROR converting k name: %s" % first_it)
                    success = False
                    
                if not success:
                    k_data.append([str(i), type_el, K_UNKNOWN_NAME, K_UNKNOWN_NAME])
                    success = True
        else:
            print("ERROR reading K, k_data not paired.")    
            success = False 
            
        return k_data, temp_index, success
    
    @staticmethod
    def k_scraping():
        
        k_data = []
        index = ''
    
        bsObj = KScrap.retrieve_page(K_URL)
        
        if bsObj:
            try:
                k_data, index, success = KScrap._process_k_page(bsObj)
                
                if not success:
                    raise ScrapingException("Error scraping k.")
                    
            except KeyError as ke:
                print("ERROR retrieving k: %s" % ke)
                success = False
                
        return k_data, index
    
    # ------------------------------------- Re scraping.   
    @staticmethod     
    def _process_re_page(bsObj):

        data = []
        
        for cobj in bsObj.findAll(RE_COBJ, RE_LINE):            
            for eobj in cobj.findAll(RE_EOBJ, RE_SECOND): 
                second = eobj.get_text().strip()
            for eobj in cobj.findAll(RE_EOBJ, RE_FIRST): 
                data.append(eobj.get_text().strip())     
                
            data.append(second)              
                
            marcador = True
            for eobj in cobj.findAll(RE_EOBJ, RE_SCO):
                if marcador: 
                    data.append(eobj.get_text().strip())
                    marcador = False
                else:
                    data.append(eobj.get_text().strip())
                
            for eobj in cobj.findAll(RE_EOBJ, RE_VAL): 
                txt = eobj.get_text().strip()
                if len(txt) and txt[-1] == "'":
                    plus = -1
                    i = len(txt) - 2
                    while ( txt[i].isdigit() or txt[i] == RE_DELIM) and i >= 0:
                        if txt[i] == RE_DELIM:
                            plus = i
                        i -= 1
                    z = 0
                    if plus > 0:
                        x = int(txt[i:plus])
                        y = int(txt[plus+1:-1])
                        z =  x + y
                    else:
                        z = int(txt[i:-1])
                    data.append(z)
                    
        return data
    
    @staticmethod
    def res_scraping(url):
    
        bsObj = KScrap.retrieve_page(url)
        
        return KScrap._process_re_page(bsObj)    
    
    # ------------------------------------- LM scraping.   
    @staticmethod 
    def _process_lm_page(bsObj, lm):
        
        i = 0
        j = 0
        n = 0
        
        for cobj in bsObj.findAll(LM_COBJ):
            for eobj in cobj.findAll(LM_EOBJ, LM_DICT):        
                    
                if i == NUM_ROWS:
                    return 
                
                elif n >= LM_FIRST_COL and n <= LM_LAST_COL:
    
                    lm[i][j] = int(eobj.get_text().strip())
                    
                    j += 1
                    if j == NUM_COLS:
                        i += 1
                        j = 0                   
                     
                n = (n + 1) % LM_TD_ROW_SIZE        
    
    @staticmethod
    def lm_scraping(lm):
        
        try:
            bsObj = KScrap.retrieve_page(LM_URL)
            
            KScrap._process_lm_page(bsObj, lm)
            
            print("Read: %dx%d" % (len(lm), len(lm[0])))
        except AttributeError as ae:
            print("ERROR retrieving lm: %s" % ae)
        except requests.ConnectionError as ce:
            print("ERROR ConnectionError lm: %s" % ce)
        
    # ------------------------------------- VE scraping.  
    @staticmethod      
    def _process_ve_page(bsObj, ve):

        i = 0
        for ob in bsObj.findAll(VE_COBJ_1, VE_DICT_1):     
            j = 0   
            for cobj in ob.findAll(VE_COBJ_2, VE_DICT_2):
                ve[i][j] = int(cobj.get(VE_ATTRIBUTE))
                
                j += 1
                if j == NUM_COLS:
                    i += 1
                    j = 0      
    
    @staticmethod
    def ve_scraping(ve):
    
        try:
            bsObj = KScrap.retrieve_page(VE_URL)
            
            KScrap._process_ve_page(bsObj, ve)
        
            print("Read: %dx%d" % (len(ve), len(ve[0])))
        except AttributeError as ae:
            print("ERROR retrieving ve: %s" % ae)
        except requests.ConnectionError as ce:
            print("ERROR ConnectionError ve: %s" % ce)

    # ------------------------------------- QU scraping.
    @staticmethod
    def _process_qu_page(bsObj, qu):
        
        i = 0
        j = 0   
        n = 0 
        
        for cobj in bsObj.findAll(QU_COBJ, QU_DICT):
            
            if i == NUM_ROWS - 1:
                return
            
            elif n >= QU_FIRST_COL and n <= QU_LAST_COL:
    
                qu[i][j] = int(cobj.get_text())
                
                j += 1
                if j == NUM_COLS:
                    i += 1
                    j = 0                   
                 
            n = (n + 1) % QU_TD_ROW_SIZE 
    
    @staticmethod
    def qu_scraping(qu):
        
        if sum(qu[0]) == 0:
            try:
                bsObj = KScrap.retrieve_page(QU_URL)
                
                KScrap._process_qu_page(bsObj, qu)
            
                print("Read: %dx%d" % (len(qu), len(qu[0])))
            except AttributeError as ae:
                print("ERROR retrieving qu: %s" % ae)
            except requests.ConnectionError as ce:
                print("ERROR ConnectionError qu: %s" % ce)
            
    # ------------------------------------- Q1 scraping.
    @staticmethod
    def _process_q1_page(bsObj, q1):
        
        try:                       
            json_obj = bsObj.find(Q1_COBJ).get_text()
            
            json_data = json.loads(str(json_obj))
            
            for i in range(NUM_ROWS - 1):
                el = json_data[i]
                
                q1[i][0] = int(el[FIRST_FIELD])
                q1[i][1] = int(el[SECOND_FIELD])
                q1[i][2] = int(el[THIRD_FIELD])   
                
        except UnicodeEncodeError as uee:
            print(uee)  
    
    @staticmethod
    def q1_scraping(q1, index):
        
        if sum(q1[0]) == 0:
            
            try:
                bsObj = KScrap.retrieve_page(Q1_URL)
                
                KScrap._process_q1_page(bsObj, q1)    
            
                print("Read: %dx%d" % (len(q1), len(q1[0])))
            except AttributeError as ae:
                print("ERROR retrieving q1: %s" % ae)     
            except requests.ConnectionError as ce:
                print("ERROR ConnectionError q1: %s" % ce)    
            except Exception as e:
                print("ERROR Exception q1: %s" % e) 
         
    # ------------------------------------- CQ scraping.
    @staticmethod
    def _process_cq_page(bsObj, cq, cqp):
        
        current_data = cq
        table = str.maketrans(dict.fromkeys("b'"))
        
        i = 0
        for ob in bsObj.findAll(CQ_OB, CQ_DICT):        
            for cobj in ob.findAll(CQ_OBJ):
                j = 0
                for eobj in cobj.findAll(CQ_EOBJ, CQ_EOBJ_DICT):
                    txt = eobj.get_text().strip() 
                    if i < NUM_ROWS - 1:
                        if len(txt):
                            txt_nor = un.normalize('NFKD', txt).encode('ascii','ignore').__str__().translate(table)
                            
                            pos = txt_nor.find(CQ_SEP)
                            if pos > 0:
                                txt_red = txt_nor[:pos]                        
                        
                            current_data[i][j] = int(txt_red)
                            
                            j += 1
                            if j == NUM_COLS:
                                i += 1
                                j = 0 
                    
            current_data = cqp
            i = 0
            j = 0                     
    
    @staticmethod
    def cq_scraping(cq, cqp):
        
        if sum(cq[0]) == 0:
            
            try:
                bsObj = KScrap.retrieve_page(CQ_URL) 
                
                KScrap._process_cq_page(bsObj, cq, cqp)     
            
                print("Read: %dx%d" % (len(cq), len(cqp)))
            except AttributeError as ae:
                print("ERROR retrieving cq: %s" % ae)  
            except requests.ConnectionError as ce:
                print("ERROR ConnectionError cq: %s" % ce)
    
    # ------------------------------------- Cl scraping.
    @staticmethod
    def _fill_cl_data(data, index, size, bsObj, cobj_data):
        
        temp_lst = []
        
        for cobj in bsObj.findAll(CL_COBJ, cobj_data):        
            temp_lst.append(cobj.get_text())  
            
        for i in range(size):
            data[i][index] = int(temp_lst[i])                  
    
    @staticmethod
    def _process_cl_page(bsObj, size):
        
        cl_data = [[0 for _ in range(NUM_COLS_CL)] for _ in range(size)]
        
        temp_lst = []        
        
        for cobj in bsObj.findAll(CL_COBJ, CL_EQ_DICT): 
            the_text = cobj.get_text()
            if the_text[-1] == CL_ESP_CHR:
                the_text = the_text[:-1]
            temp_lst.append(the_text)
            
        for i in range(size):
            try:
                cl_data[i][CL_POS_COL] = i + 1
                cl_data[i][CL_NAME_COL] = NAMES_CONVERT[temp_lst[i]]
            except KeyError as ke:
                print("ERROR: %s" % ke)                  
           
        for i, elt in enumerate(CL_ELEMENTS):            
            KScrap._fill_cl_data(cl_data, i + CL_INDEX_P_LO, size, bsObj, elt) 
            
        return cl_data            
    
    @staticmethod
    def _cl_scraping(url, size):
    
        bsObj = KScrap.retrieve_page(url)
        
        cl_data = KScrap._process_cl_page(bsObj, size)
        
        print("Read: %dx%d for Cl" % (len(cl_data), len(cl_data[0])))
        
        return cl_data                      

    @staticmethod 
    def scrap_cl_data():
        """Scraping CL data.
        """
        
        b1 = KScrap._cl_scraping(CL_B1_URL, B1_SIZE)

        a2 = KScrap._cl_scraping(CL_A2_URL, A2_SIZE)
            
        return b1, a2          