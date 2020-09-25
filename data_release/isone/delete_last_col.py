#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 16:49:27 2020

@author: stevenwu
"""

import pandas as pd

df = pd.read_csv(r'/Users/stevenwu/Desktop/research_group/COVID/COVID-EMDA/data_release/isone/isone_rto_genmix.csv')    
columns = df.columns.tolist()
new_col = columns[:len(columns)-1]
df = pd.read_csv('/Users/stevenwu/Desktop/research_group/COVID/COVID-EMDA/data_release/isone/isone_rto_genmix.csv',
                 usecols=new_col)
df.to_csv('output.csv', index=False)