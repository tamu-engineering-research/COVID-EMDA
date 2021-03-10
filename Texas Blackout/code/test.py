from esa import SAW
import pandas as pd
import numpy as np


CASE_PATH = r"C:\Users\Dongqi Wu\Dropbox\Work\thermal storage\synthetic_grid_v2\ACTIVSg2000\ACTIVSg2000.pwb"
CASE_PATH_SAVE = r"..\case\2000_mod.pwb"


saw = SAW(FileName=CASE_PATH)
saw.SolvePowerFlow()
saw.RunScriptCommand("EnterMode(EDIT);")
bus_key_fields = saw.get_key_field_list('bus')#['BusNum']
load_key_fields = saw.get_key_field_list('load')#['BusNum', 'LoadID']
line_key_fields = saw.get_key_field_list('branch')#['BusNum', 'BusNum:1', 'LineCircuit']
generator_key_fields = saw.get_key_field_list('gen')#['BusNum', 'GenID']

bus_frame = saw.GetParametersMultipleElement('bus', bus_key_fields + ['BusSlack'])
print(bus_frame)
