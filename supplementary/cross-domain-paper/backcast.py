import time, shutil
from backcast_tools import *


if __name__ == '__main__':
    # configurations
    area = 'nyc'
    date_range = pd.date_range('2018-02-01', '2020-01-31')
    date_range_covid = pd.date_range('2020-02-01', '2020-06-30')
    model_num, model_sel = 800, 200
    base_hidden = (32, 64)

    time_stamp = time.strftime('%Y%m%d-%H%M')
    paths = {
        'all_models':       'param/' + area + '_' + time_stamp + '/',
        'selected_models':  'param/' + area + '_select_' + time_stamp + '/',
        'train_test_data':  'train_test_data/',
        'scan_result':      'scan_prediction_result/',
        'reduction_result': 'reduction_result/',
    }
    create_path(paths)

    # # -------------------- STEP 01: DATA PREPARATION -------------------- # #
    # generate train & test datasets
    ddc = DailyDataCollector(area=area)
    files_training = ddc.generate_train_test_data(date_range=date_range, save_path=paths['train_test_data'])

    # # -------------------- STEP 02: TRAINING AND VERIFICATION -------------------- # #
    inputs = pd.read_csv(files_training['input_train'], index_col='date')
    outputs = pd.read_csv(files_training['output_train'], index_col='date')

    scan_training(  # scanning
        inputs=inputs,
        outputs=outputs,
        n_batch=model_num,
        base_hidden=base_hidden,
        save_path=paths['all_models'],
    )
    ver_mdl_out = verify_model(  # verification
        paths['all_models'], files_training['input_test'], files_training['output_test'], model_sel)

    # model selection
    for fn in ver_mdl_out['model'].values.flatten():
        shutil.copy(paths['all_models'] + fn, paths['selected_models'])  # copy models
        print(':: Copying %s to %s' % (fn, paths['selected_models']))

    # # -------------------- STEP 03: BASELINE ESTIMATION -------------------- # #
    # estimation for COVID-19 time
    files_covid = ddc.generate_train_test_data(date_range=date_range_covid, save_path=paths['train_test_data'])
    inputs = pd.read_csv(files_covid['input_test'], index_col='date', parse_dates=True)
    scan_file = paths['scan_result'] + area + '_scan_prediction.csv'
    scan_prediction(inputs, paths['selected_models'], scan_file)

    # generate reduction result
    redu_result_file = paths['reduction_result'] + area + '_load_backcast.csv'
    redu_result_rate_file = paths['reduction_result'] + area + '_load_backcast_pct.csv'
    generate_reduction_result(scan_file, files_covid['output_test'], redu_result_file)
    print_reduction_summary(redu_result_rate_file)
