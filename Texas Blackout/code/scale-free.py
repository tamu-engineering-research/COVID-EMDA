# /**
#  * @author Xiangtian Zheng
#  * @email zxt0515@tamu.edu
#  * @create date 2020-11-08 09:47:59
#  * @modify date 2020-11-21 19:53:22
#  * @desc [description]
#  */
from esa import SAW
import pandas as pd
import numpy as np
from AssignPara2ScaleFree import *
from utils import *

"""
"""
CASE_PATH = r"C:\Users\Dongqi Wu\Dropbox\Work\thermal storage\synthetic_grid_v2\ACTIVSg2000\ACTIVSg2000.pwb"
CASE_PATH_SAVE = r"..\case\2000_mod.pwb"
Case_path_ref = r"E:\PowerWorld\Low-rankness\ACTIVSg10k\ACTIVSg10k.PWB"

# """
# get reference data generator/load/branch
# """
# saw_ref = SAW(FileName=Case_path_ref, early_bind=True)
# load_ref = saw_ref.GetParametersMultipleElement('load', ['BusNum', 'LoadID'] + ['LoadSMW', 'LoadSMVR', 'LoadStatus'])


"""
start creating
"""
saw = SAW(FileName=CASE_PATH, CreateIfNotFound=True, early_bind=True)
saw.RunScriptCommand("EnterMode(EDIT);")
bus_key_fields = saw.get_key_field_list('bus')#['BusNum']
load_key_fields = saw.get_key_field_list('load')#['BusNum', 'LoadID']
line_key_fields = saw.get_key_field_list('branch')#['BusNum', 'BusNum:1', 'LineCircuit']
generator_key_fields = saw.get_key_field_list('gen')#['BusNum', 'GenID']

"""
clean existing branch, generator and load
"""
bus_frame = saw.GetParametersMultipleElement('bus', bus_key_fields + ['BusSlack'])
load_frame = saw.GetParametersMultipleElement('load', load_key_fields + ['LoadStatus'])
line_frame = saw.GetParametersMultipleElement('branch', line_key_fields + ['LineStatus'])
gen_frame = saw.GetParametersMultipleElement('gen', generator_key_fields + ['GenStatus'])
bus_frame['BusSlack'] = 'NO'
load_frame['LoadStatus'] = 'Open'
line_frame['LineStatus'] = 'Open'
gen_frame['GenStatus'] = 'Open'
saw.change_and_confirm_params_multiple_element('bus', bus_frame)# remember to delete and reset slack bus 
saw.change_and_confirm_params_multiple_element('load', load_frame)
saw.change_and_confirm_params_multiple_element('branch', line_frame)
saw.change_and_confirm_params_multiple_element('gen', gen_frame)

"""
create scale-free network
"""
#### create scale-free network g
g = generate_scale_free_network(num_bus=2000, num_branch=2)

#### create parameters to assign
# num_gen, num_load = 1937, 4899
num_gen, num_load = 544, 1350
# num_gen, num_load = 54, 135
bus_df_columns = bus_key_fields+['BusName','BusNomVolt','AreaNum','ZoneNum', 'BusB:1']
load_df_columns = load_key_fields+['LoadSMW', 'LoadSMVR', 'LoadStatus']
line_df_columns = line_key_fields+['LineR', 'LineX', 'LineC', 'LineAMVA', 'LineAMVA:1', 'LineAMVA:2', 'LineStatus']
gen_df_columns = generator_key_fields+['GenAGCAble', 'GenAVRAble', 'GenStatus', 'GenMVABase','GenVoltSet', 
                                        'GenMvrSetPoint','GenMVRMax', 'GenMVRMin',
                                        'GenMWSetPoint','GenMWMax','GenMWMin',]#, 'TSGenExciterName', 'TSGenGovernorName',
machine_df_columns = generator_key_fields+['TSH','TSD','TSXd','TSXq','TSXd:1','TSXq:1','TSXd:2','TSXl','TSTdo','TSTqo','TSTdo:1','TSTqo:1']
exciter_df_columns = generator_key_fields+['TSDeviceStatus', 'TSEfdMax', 'TSEfdMin','TSK','TSTaSlashTb','TSTb','TSTe']##################
governor_df_columns = generator_key_fields+['TSDeviceStatus', 'TSDt', 'TSR', 'TST:1', 'TST:2', 'TST:3', 'TSTrate', 'TSVmax', 'TSVmin']##################
bus_df = assign_bus(g, bus_df_columns)
line_df = assign_line(g, line_df_columns)
load_df, sum_load = assign_load(g, load_df_columns, num_load)
gen_df, machine_df, slack_df, exciter_df, governor_df = assign_gen(g, gen_df_columns, machine_df_columns, exciter_df_columns, governor_df_columns, num_gen, sum_load)
#### create power grid with the created parameters
saw.change_and_confirm_params_multiple_element('bus', bus_df)
saw.change_and_confirm_params_multiple_element('bus', slack_df)
saw.change_and_confirm_params_multiple_element('load', load_df)
saw.change_and_confirm_params_multiple_element('branch', line_df)
saw.change_and_confirm_params_multiple_element('gen', gen_df)
saw.change_and_confirm_params_multiple_element('MachineModel_GENROU', machine_df)
saw.change_and_confirm_params_multiple_element('Exciter_SEXS_PTI', exciter_df)#('Exciter_EXST1_GE', exciter_df)
saw.change_and_confirm_params_multiple_element('Governor_TGOV1', governor_df)
saw.SolvePowerFlow()

"""
save case
"""
saw.RunScriptCommand('SaveCase("'+CASE_PATH_SAVE+'");')
saw.exit()
