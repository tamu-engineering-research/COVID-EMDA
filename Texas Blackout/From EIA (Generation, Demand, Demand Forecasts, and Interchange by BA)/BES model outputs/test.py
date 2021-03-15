import pickle5
import pandas as pd

PF = pickle5.load(open('PF.pkl','rb'))
PG = pickle5.load(open('PG.pkl','rb'))

print(PG)
print(PF)
print(PG.index)
