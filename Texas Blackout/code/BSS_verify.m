%% intro
clear;
define_constants;
case_path = "..\bte2k\case_Feb24_5pm.mat";
gen_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Generation by Source\2021-02-01 to 2021-02-19.csv";
load_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_demand_Feb2021_v20210224.csv";
wind_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_wind_Feb2021_v20210224.csv";
solar_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_solar_Feb2016_v20210224.csv";
hydro_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_hydro_Feb2016_v20210224.csv";

mpc = load(case_path);
mpc = mpc.mpc;


% TODO:
% gen mismatch by source/region
% renewable curtailment by region


% configs
mpopt = mpoption('pf.nr.max_it', 50);
mpopt = mpoption(mpopt,'out.all',0);
mpopt = mpoption(mpopt,'verbose',3); 
mpopt = mpoption(mpopt, 'gurobi.threads', 6);
mpopt = mpoption(mpopt, 'gurobi.opts.MIPGap', 1e-2); % gap <= 1%
mpopt = mpoption(mpopt,'most.dc_model', 1); 
mpopt = mpoption(mpopt,'pf.tol', 1e-6); 
mpopt = mpoption(mpopt,'model', 'DC');
%mpopt = mpoption(mpopt,'opf.violation', 1e-3); 

[gen_val, gen_ts, ~] = xlsread(gen_path);
gen_ts(1, :) = [];
gen_ts = gen_ts(:, 2);

[load_val, load_ts, ~] = xlsread(load_path);
load_ts(1, :) = [];
load_val(1, :) = [];

wind_ts = readmatrix(wind_path);
wind_ts(:, 1) = [];
wind_ts(1, :) = [];
wind_ts(1:6,:) = []; % remove first 6 rows

solar_ts = readmatrix(solar_path);
solar_ts(:, 1) = [];
solar_ts(1, :) = [];

hydro_ts = readmatrix(hydro_path);
hydro_ts(:, 1) = [];
hydro_ts(1, :) = [];

genmix_header = ["wind", "solar", "hydro", "other", "ng", "coal", "nuclear"];

coal_ind = find(strcmp(mpc.genfuel, 'coal') == 1);
pv_ind = find(strcmp(mpc.genfuel, 'solar') == 1);
hydro_ind = find(strcmp(mpc.genfuel, 'hydro') == 1);
ng_ind = find(strcmp(mpc.genfuel, 'ng') == 1);
nuke_ind = find(strcmp(mpc.genfuel, 'nuclear') == 1);
wind_ind = find(strcmp(mpc.genfuel, 'wind') == 1);


%% modify base case gen
mpc.gen(:, GEN_STATUS) = 1;

% change the generator cost to linear (removing c2 in mpc.gencost)
[pg_val, pg_ts, ~] = xlsread('pg.csv');
pg_ts(1, :) = [];
pg_ts = pg_ts(:, 1);

[pf_val, pf_ts, ~] = xlsread('pf.csv');
pf_ts(1, :) = [];
pf_ts = pf_ts(:, 1);

mpc.gen(555, VG) = 1.02;
%% params
% Start with 1/31 0:00
day_skipped = 7; % Feb 12
hour_target = 12;
%row_num = day_skipped * 24 + hour_target + 1;
row_num = 346;

pg_tar = pg_val(row_num+1,:)';

% fetch and match gen
for gen_type_i = 1:7
    gen_type = genmix_header(gen_type_i);
    if gen_type == 'other'
        ;
    else
        type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
        %base_gen = sum(mpc.gen(type_ind, PG));
        %real_gen = gen_val(row_num, gen_type_i);
        
        % scale gen if non renewable !! need to be changed
        %mpc.gen(type_ind, PG) = mpc.gen(type_ind, PG) * real_gen / base_gen;
        %mpc.gen(type_ind, QG) = mpc.gen(type_ind, QG) * real_gen / base_gen;
        
        % supply-curve dispath for non renewables

        % set pmin/max if renewable
        if gen_type_i == 1 % wind
            mpc.gen(type_ind, PG) = wind_ts(row_num,:)';
            mpc.gen(type_ind, PMIN) = 0;
            mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
        elseif gen_type_i == 2 % solar
            mpc.gen(type_ind, PG) = solar_ts(row_num,:)';
            mpc.gen(type_ind, PMIN) = 0;
            mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);   
        elseif gen_type_i == 3 % hydro
            mpc.gen(type_ind, PG) = hydro_ts(row_num,:)';
            mpc.gen(type_ind, PMIN) = 0;
            mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
        end
    end
end

% fetch and match load
for load_area_i = 1:8
    real_area = load_area_i + 300;
    load_ind = find(mpc.bus(:, BUS_AREA) == real_area);
    base_load = sum(mpc.bus(load_ind, PD));
    real_load = load_val(row_num, load_area_i);
    
    % scale load
    mpc.bus(load_ind, PD) = mpc.bus(load_ind, PD) * real_load / base_load;
    %mpc.bus(load_ind, QD) = mpc.bus(load_ind, QD) * real_load / base_load;
end

%mpc.gen(:,PG) = pg_tar;
%dcres = rundcpf(mpc);
opfres = rundcopf(mpc, mpopt);