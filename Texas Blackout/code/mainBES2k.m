%% intro
clear;
define_constants;
case_path = "..\bte2k\case_Feb24_5pm.mat";
gen_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Generation by Source\2021-02-01 to 2021-02-19.csv";
load_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Demand by Subregion\2021-02-01 to 2021-02-19.csv";
wind_path = "..\data\BES_wind_20210224.csv";

mpc = load(case_path);
mpc = mpc.mpc;

% configs
mpopt = mpoption('pf.nr.max_it', 30);
mpopt = mpoption(mpopt,'out.all',1);
mpopt = mpoption(mpopt,'verbose',3); 
mpopt = mpoption(mpopt, 'gurobi.threads', 6);
mpopt = mpoption(mpopt, 'gurobi.opts.MIPGap', 1e-2); % gap <= 1%
mpopt = mpoption(mpopt,'most.dc_model', 1); 

[gen_val, gen_ts, garbage1] = xlsread(gen_path);
gen_ts(1, :) = [];
gen_ts = gen_ts(:, 2);

[load_val, load_ts, garbage2] = xlsread(load_path);
load_ts(1, :) = [];
load_ts = load_ts(:, 2);

wind_ts = readmatrix(wind_path);
wind_ts(:, 1) = [];
wind_ts(1, :) = [];

genmix_header = ["wind", "solar", "hydro", "other", "ng", "coal", "nuclear"];
% source: http://www.ercot.com/content/wcm/lists/219736/ERCOT_Fact_Sheet_2.12.21.pdf
genmix_pct = [0.248, 0.038, 0.002, 0.019, 0.51, 0.134, 0.049];

coal_ind = find(strcmp(mpc.genfuel, 'coal') == 1);
pv_ind = find(strcmp(mpc.genfuel, 'solar') == 1);
hydro_ind = find(strcmp(mpc.genfuel, 'hydro') == 1);
ng_ind = find(strcmp(mpc.genfuel, 'ng') == 1);
nuke_ind = find(strcmp(mpc.genfuel, 'nuclear') == 1);
wind_ind = find(strcmp(mpc.genfuel, 'wind') == 1);

% !!! add other to NG
gen_val(:, 5) = gen_val(:, 4) + gen_val(:, 5);

% coal_names = [];
% for i = coal_gens(:, 1)'
%     coal_names = [coal_names; mpc.bus_name(find(mpc.bus(:,1) == i))];
% end
area_mpc = ["FW", "N", "W", "S", "NC", "SC", "C", "E"];
load_rearranged = [load_val(:,3),load_val(:,4),load_val(:,8),load_val(:,6),load_val(:,5),load_val(:,7),load_val(:,1),load_val(:,2)];

%% modify base case gen
mpc.gen(:, GEN_STATUS) = 1;

% scale the generators using real fuel distribution
total_cap = 25251 / 0.248;
genmix_cap = total_cap * genmix_pct;
mpc.gen(coal_ind, PMAX) = mpc.gen(coal_ind, PMAX) / sum(mpc.gen(coal_ind, PMAX)) * genmix_cap(6);
mpc.gen(hydro_ind, PMAX) = mpc.gen(hydro_ind, PMAX) / sum(mpc.gen(hydro_ind, PMAX)) * genmix_cap(3);
mpc.gen(ng_ind, PMAX) = mpc.gen(ng_ind, PMAX) / sum(mpc.gen(ng_ind, PMAX)) * genmix_cap(5);
mpc.gen(nuke_ind, PMAX) = mpc.gen(nuke_ind, PMAX) / sum(mpc.gen(nuke_ind, PMAX)) * 5150;


% change the generator cost to linear (removing c2 in mpc.gencost)

mpc.gencost(mpc.gencost(:,1) == 2,4) = 2;



%% params
% Start with 1/31 0:00
day_skipped = 12; % Feb 12
hour_target = 10;
row_num = day_skipped * 24 + hour_target + 1;

% wind start with 02/01 0:00
wind_skipped = day_skipped - 1;
wind_row_num = wind_skipped * 24 + hour_target + 1;


% fetch and match gen
for gen_type_i = 1:7
    gen_type = genmix_header(gen_type_i);
    if gen_type == 'other'
        ;
    else
        type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
        base_gen = sum(mpc.gen(type_ind, PG));
        real_gen = gen_val(row_num, gen_type_i);
        
        % scale gen if non renewable !! need to be changed
        %mpc.gen(type_ind, PG) = mpc.gen(type_ind, PG) * real_gen / base_gen;
        %mpc.gen(type_ind, QG) = mpc.gen(type_ind, QG) * real_gen / base_gen;
        
        % supply-curve dispath for non renewables

        % set pmin/max if renewable
        if gen_type_i == 1 % wind
            mpc.gen(type_ind, PG) = wind_ts(wind_row_num,:)';
            mpc.gen(type_ind, PMIN) = mpc.gen(type_ind, PG);
            mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
            mpc.gen(type_ind, QMIN) = mpc.gen(type_ind, QG);
            mpc.gen(type_ind, QMAX) = mpc.gen(type_ind, QG);
        elseif gen_type_i < 4 && gen_type_i > 1 % not wind
            mpc.gen(type_ind, PG) = mpc.gen(type_ind, PG) * real_gen / base_gen;
            mpc.gen(type_ind, QG) = 0;
            mpc.gen(type_ind, PMIN) = mpc.gen(type_ind, PG);
            mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
            mpc.gen(type_ind, QMIN) = mpc.gen(type_ind, QG);
            mpc.gen(type_ind, QMAX) = mpc.gen(type_ind, QG);
        else
            mpc.gen(type_ind, PG) = supply_curve(mpc, real_gen,type_ind);

        end
    end
end


% fetch and match load
for load_area_i = 1:8
    real_area = load_area_i + 300;
    load_ind = find(mpc.bus(:, BUS_AREA) == real_area);
    base_load = sum(mpc.bus(load_ind, PD));
    real_load = load_rearranged(row_num, load_area_i);
    
    % scale load
    mpc.bus(load_ind, PD) = mpc.bus(load_ind, PD) * real_load / base_load;
    mpc.bus(load_ind, QD) = mpc.bus(load_ind, QD) * real_load / base_load;
    
end
