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

"""Script to perform predictions.
"""

import sys
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import tensorflow as tf
import tensorflow.contrib.learn as skflow

from ctes import *
from utils import get_matchings

def _get_val_index(values, order, sort_values, name):
    
    try:
        i = order.index(name)
        sort_values.append(values[i])
    except ValueError:
        sort_values.append(0)

def _sort_pre_values(values, order):
    
    sort_values = []
    
    _get_val_index(values, order, sort_values, FIRST_NAME)
    _get_val_index(values, order, sort_values, SECOND_NAME)
    _get_val_index(values, order, sort_values, THIRD_NAME)     
    _get_val_index(values, order, sort_values, FOURTH_NAME) 
    _get_val_index(values, order, sort_values, FIFTH_NAME)            
                
    return sort_values  

def prepare_data_for_nn(hist_data, data_to_predict, cl_data):
    
    np_hist_data = np.matrix(hist_data).astype(float)
    
    np_cl_data_num = np.array([CL_TO_NUM[x] for x in cl_data])
    
    np_prd_data = np.matrix(data_to_predict).astype(float)
    
    return np_hist_data, np_prd_data, np_cl_data_num

def link_perc_to_cl(prd, cl):
    
    data_out = []
    
    for p in prd:
        
        sort_pre_val = _sort_pre_values(p, cl)
        
        data_out.append([int(100 * x) for x in sort_pre_val])
        
    return data_out

def nn_model(x, y):

    layers = skflow.ops.dnn(x, NN_LEVELS, tf.tanh)
    
    return skflow.models.logistic_regression(layers, y)

def eval_predict_nn(prd_data, prd_cl_data, eval_data, eval_cl_data):
    
    np_prd_data = np.matrix(prd_data).astype(float)
    np_prd_cl_data = np.array([CL_TO_NUM[x] for x in prd_cl_data])
    np_eval_data = np.matrix(eval_data).astype(float)
    np_eval_cl_data = np.array([CL_TO_NUM[x] for x in eval_cl_data])
    
    nn = skflow.TensorFlowEstimator(model_fn=nn_model, n_classes=len(CLASSES_PRE))
    
    nn.fit(np_prd_data, np_prd_cl_data, logdir = LOG_DIR)
    
    return metrics.accuracy_score(np_eval_cl_data, nn.predict(np_eval_data))

def eval_predict_rf(prd_data, prd_cl_data, eval_data, eval_cl_data):
    
    np_prd_data = np.matrix(prd_data)
    np_prd_cl_data = np.array(prd_cl_data)
    np_eval_data = np.matrix(eval_data)
    np_eval_cl_data = np.array(eval_cl_data)
    
    rf = RandomForestClassifier(n_estimators=RF_NUM_ESTIMATORS_PRUN, 
        random_state=RF_SEED)
    
    rf.fit(np_prd_data, np_prd_cl_data)
    
    return metrics.accuracy_score(np_eval_cl_data, rf.predict(np_eval_data))

def predict_nn(hist_data, cl_data, data_to_predict):
    
    np_hist_data, np_prd_data, np_classes_data = \
        prepare_data_for_nn(hist_data, data_to_predict, cl_data)
    
    nn = skflow.TensorFlowEstimator(model_fn=nn_model, n_classes=len(CLASSES_PRE))
    
    nn.fit(np_hist_data, np_classes_data, logdir = LOG_DIR)
    
    score = metrics.accuracy_score(np_classes_data, nn.predict(np_hist_data))
    print("Accuracy NN: %f" % score)
      
    prd = nn.predict_proba(np_prd_data) 
    
    return link_perc_to_cl(prd, CLASSES_PRE), score

def predict_rf(hist_data, cl_data, data_to_predict):
    
    np_hist_data = np.matrix(hist_data)
    np_classes_data = np.array(cl_data)
    np_prd_data = np.matrix(data_to_predict)
    
    rf = RandomForestClassifier(n_estimators=RF_NUM_ESTIMATORS_PRUN, 
        random_state=RF_SEED)
    
    rf.fit(np_hist_data, np_classes_data)
    
    score = metrics.accuracy_score(np_classes_data, rf.predict(np_hist_data))
    print("Accuracy RF: %f" % score)
    
    prd = rf.predict_proba(np_prd_data)

    return link_perc_to_cl(prd, np.ndarray.tolist(rf.classes_)), score

def extract_pred_data(pred_data):
    
    hist_data = [ e[:-1] for e in pred_data]
    cl_data = [ e[-1] for e in pred_data]
    
    return hist_data, cl_data

def predict(pred_data, data_to_predict):
    
    data_out_rf = []
    data_out_nn = []
        
    hist_data, cl_data = extract_pred_data(pred_data)
    
    if len(hist_data) and len(data_to_predict):
        
        data_out_rf, score_rf = predict_rf(hist_data, cl_data, data_to_predict)
        data_out_nn, score_nn = predict_nn(hist_data, cl_data, data_to_predict)
        
    return data_out_rf, score_rf, data_out_nn, score_nn

def eval_predict(pred_data, eval_data):
    
    rf_score = 0.0
    nn_score = 0.0
        
    prd_data, prd_cl_data = extract_pred_data(pred_data)
    eval_data, eval_cl_data = extract_pred_data(eval_data)
        
    rf_score = eval_predict_rf(prd_data, prd_cl_data, eval_data, eval_cl_data)
    nn_score = eval_predict_nn(prd_data, prd_cl_data, eval_data, eval_cl_data)
        
    return rf_score, nn_score

def gen_hist(k, cl, b1_res, a2_res):

    data_for_predict = []
    data_to_predict = []
    
    for k_elt in k:
        hist_data = []
        to_pred_data = []
        
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
            
        cl_lo = [cl_1[i] for i in LO_D_RANGE]
        cl_vi = [cl_2[i] for i in VI_D_RANGE]
        
        pos_lo = cl_1[CL_POS]
        pos_vi = cl_2[CL_POS]
        
        dif_pos = pos_vi - pos_lo
        
        to_pred_data.append(dif_pos)
        
        to_pred_data.extend(cl_lo)
        to_pred_data.extend(cl_vi)
        
        mat1, val_res1 = get_matchings(k_name_1, data, True)
        mat2, val_res2 = get_matchings(k_name_2, data, False)
        
        for m in mat1:
            name = m[MAT_NAME_2_COL]
            if elt_type == TYPE_1_COL:
                cl_data = cl.b1_data(name)
            else:
                cl_data = cl.a2_data(name)
                
            h = [cl_data[CL_POS] - pos_lo]
            h.extend(cl_lo)
            h.extend([cl_data[i] for i in VI_D_RANGE])
            h.extend(m[MAT_RES_COL])
            hist_data.append(h)
        
        for m in mat2:
            name = m[MAT_NAME_1_COL]
            if elt_type == TYPE_1_COL:
                cl_data = cl.b1_data(name)
            else:
                cl_data = cl.a2_data(name)
                
            h = [pos_vi - cl_data[CL_POS]]
            h.extend([cl_data[i] for i in LO_D_RANGE])
            h.extend(cl_vi)
            h.extend(m[MAT_RES_COL])
            hist_data.append(h)
            
        data_for_predict.append(hist_data)
        data_to_predict.append(to_pred_data)
    
    return data_for_predict, data_to_predict

def predict_k(k, cl, b1_res, a2_res):
    
    pre_rf = []
    sco_rf = []
    pre_df = []
    sco_df = []
    
    data_for_predict, data_to_predict = gen_hist(k, cl, b1_res, a2_res)
            
    if len(data_for_predict) == len(data_to_predict):
        
        for i in range(len(data_for_predict)):
            
            print "Predicting: %s vs %s" % (k[i][K_NAME_1_COL], 
                                            k[i][K_NAME_2_COL])
            
            p1, s1, p2, s2 = predict(data_for_predict[i], data_to_predict[i])
            
            pre_rf.extend(p1)
            sco_rf.append(s1)
            pre_df.extend(p2)
            sco_df.append(s2)
    else:
        print "ERROR: Length of data for prediction don't match: %d %d" % \
            (len(data_for_predict), len(data_to_predict))
            
    return pre_rf, sco_rf, pre_df, sco_df
            
            