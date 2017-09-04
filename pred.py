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
    
    nn = skflow.TensorFlowEstimator(model_fn=nn_model, n_classes=3)
    
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
    
    nn = skflow.TensorFlowEstimator(model_fn=nn_model, n_classes=3)
    
    nn.fit(np_hist_data, np_classes_data, logdir = LOG_DIR)
    
    score = metrics.accuracy_score(np_classes_data, nn.predict(np_hist_data))
    print("Accuracy NN: %f" % score)
      
    prd = nn.predict_proba(np_prd_data) 
    
    return link_perc_to_cl(prd, CLASSES_PRE)

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

    return link_perc_to_cl(prd, np.ndarray.tolist(rf.classes_))

def process_input_data(pred_data):
    
    hist_data = [ e[RES_1ST_POS_FOR_PRED:] for e in pred_data]
    cl_data = [ e[RES_PRED_SCO_POS] for e in pred_data]
    
    return hist_data, cl_data

def predict(pred_data, data_to_predict):
    
    data_out_rf = []
    data_out_nn = []
        
    hist_data, cl_data = process_input_data(pred_data)
    
    if len(hist_data) and len(data_to_predict):
        
        data_out_rf = predict_rf(hist_data, cl_data, data_to_predict)
        data_out_nn = predict_nn(hist_data, cl_data, data_to_predict)
        
    return data_out_rf, data_out_nn

def eval_predict(pred_data, eval_data):
    
    rf_score = 0.0
    nn_score = 0.0
        
    prd_data, prd_cl_data = process_input_data(pred_data)
    eval_data, eval_cl_data = process_input_data(eval_data)
        
    rf_score = eval_predict_rf(prd_data, prd_cl_data, eval_data, eval_cl_data)
    nn_score = eval_predict_nn(prd_data, prd_cl_data, eval_data, eval_cl_data)
        
    return rf_score, nn_score