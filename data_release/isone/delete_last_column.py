#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 09:58:59 2020

@author: stevenwu
"""

import pandas as pd

df = pd.read_csv('isone_rto_genmix.csv')
df = df.drop(columns='Unnamed: 0')
df.to_csv('isone_rto_genmix_backup.csv', index=False)