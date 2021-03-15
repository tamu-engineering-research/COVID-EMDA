fp = 'ercot_load_forecast.csv';
load_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Demand by Subregion\2021-02-01 to 2021-02-19.csv";

[lf_val, lf_ts, ~] = xlsread(fp);
lf_ts(1,:) = [];

[load_val, load_ts, ~] = xlsread(load_path);
load_ts(1, :) = [];
load_val(1:24, :) = [];
load_rearranged = [load_val(:,3),load_val(:,4),load_val(:,8),load_val(:,6),load_val(:,5),load_val(:,7),load_val(:,1),load_val(:,2)];


used_val = lf_val(strcmp(lf_ts(:,13),'Y'),:);
used_val = used_val(:,2:9);
area_mpc = ["FW", "N", "W", "S", "NC", "SC", "C", "E"];
rearr_val = [used_val(:,3),used_val(:,4),used_val(:,8),used_val(:,7),used_val(:,5),used_val(:,6),used_val(:,1),used_val(:,2)];
lf_mat = zeros(504,8);
lf_mat(1:313,:) = load_rearranged(1:313,:);
lf_mat(313:504,:) = rearr_val(:,:);