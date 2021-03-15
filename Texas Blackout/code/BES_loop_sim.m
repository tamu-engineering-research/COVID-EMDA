%% intro
clear;
define_constants;
case_path = "..\bte2k\case_Mar1_5pm.mat";
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
mpopt = mpoption(mpopt,'verbose',0); 
%mpopt = mpoption(mpopt, 'gurobi.threads', 6);
%mpopt = mpoption(mpopt, 'gurobi.opts.MIPGap', 1e-2); % gap <= 1%
%mpopt = mpoption(mpopt,'most.dc_model', 1); 
%mpopt = mpoption(mpopt,'pf.tol', 1e-6); 
%mpopt = mpoption(mpopt,'model', 'DC');
%mpopt = mpoption(mpopt,'opf.violation', 1e-3); 

[gen_val, gen_ts, ~] = xlsread(gen_path);
gen_ts(1, :) = [];
gen_ts = gen_ts(:, 2);
gen_val(1:24,:) = [];
gen_val(end,:) = [];

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
pg_val(1,:) = [];

% [pf_val, pf_ts, ~] = xlsread('pf.csv');
% pf_ts(1, :) = [];
% pf_ts = pf_ts(:, 1);

mpc.gen(555, VG) = 1.02;
mpc.gencost(599:606, 5:7) = 0; 
%% looping through hours
% Start with 2/1 0:00
total_rows = size(load_val, 1);
real_date = 1;
real_hr = 0;

% initailize containers
genmix_mismatch = zeros(total_rows, 7);
genmix_opf = zeros(total_rows, 7);
wind_curt = zeros(total_rows, 8);
pv_curt = zeros(total_rows, 8);
all_renew_curt = zeros(total_rows, 2);
total_gen = zeros(total_rows,3);
for row_num = 1:total_rows

    pg_tar = pg_val(row_num,:)';
    fprintf('%d : %d\n',real_date, real_hr);
    % fetch and match gen
    for gen_type_i = 1:7
        gen_type = genmix_header(gen_type_i);
        if strcmp(gen_type,'other')
            ;
        else
            type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
            %base_gen = sum(mpc.gen(type_ind, PG));
            %real_gen = gen_val(row_num, gen_type_i);

            % scale gen if non renewable !! need to be changed
            %mpc.gen(type_ind, PG) = mpc.gen(type_ind, PG) * real_gen / base_gen;
            %mpc.gen(type_ind, QG) = mpc.gen(type_ind, QG) * real_gen / base_gen;

            % supply-curve dispath for non renewables

            % set pmin/max if renewable(allow curtailment), just set PMAX
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

    % solve OPF 
    opfres = rundcopf(mpc, mpopt);
    %assert(opfres.success);
    if ~opfres.success
       disp('error'); 
    end
    % generate stats
    
    % gen difference by type
    for gen_type_i = 1:7
        gen_type = genmix_header(gen_type_i);
        if gen_type == 'other'
            ;
        else
            type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
            real_gen = gen_val(row_num, gen_type_i);
            opf_gen = sum(opfres.gen(type_ind, PG));
            genmix_mismatch(row_num, gen_type_i) = opf_gen - real_gen;
            genmix_opf(row_num, gen_type_i) = opf_gen;
        end
    end
    
    % wind and PV curtailment by zone
    opf_wind = opfres.gen(wind_ind, :);
    opf_pv = opfres.gen(pv_ind, :);
    for load_area_i = 1:8
        area_wind_ind = find(floor((opf_wind(:, 1) - 3000000) /  1000) == load_area_i);
        area_pv_ind = find(floor((opf_pv(:, 1) - 3000000) /  1000) == load_area_i);
        wind_curt(row_num, load_area_i) = 100 * (1 - sum(opf_wind(area_wind_ind, PG)) / sum(opf_wind(area_wind_ind, PMAX)));
        pv_curt(row_num, load_area_i) = 100 * (1 - sum(opf_pv(area_pv_ind, PG)) / sum(opf_pv(area_pv_ind, PMAX)));
    end
    
    % total wind and PV curtailment
    %all_renew_curt(row_num, 1) = 100 * abs(sum(wind_ts(row_num, :)) - sum(opf_wind(:, PG))) / sum(wind_ts(row_num, :)); 
    %all_renew_curt(row_num, 2) = 100 * abs(sum(solar_ts(row_num,:)) - sum(opf_pv(:, PG))) / sum(solar_ts(row_num, :));
    
    all_renew_curt(row_num, 1) = 100 * abs(sum(wind_ts(row_num, :)) - sum(pg_val(row_num,wind_ind))) / sum(wind_ts(row_num, :)); 
    all_renew_curt(row_num, 2) = 100 * abs(sum(solar_ts(row_num,:)) - sum(pg_val(row_num,pv_ind))) / sum(solar_ts(row_num, :)); 
    
    % total gen
    total_gen(row_num,1) = sum(opfres.gen(:,PG));
    total_gen(row_num,2) = sum(gen_val(row_num,:));
    total_gen(row_num,3) = sum(pg_val(row_num,:));
    
    real_hr = real_hr + 1;
    if real_hr == 24
        real_hr = 0;
        real_date = real_date + 1;
    end
end 


%% plot results
ax1 = subplot(4,1,1);
plot(ax1,1:row_num, genmix_mismatch);
title(ax1, 'Dispatch Mismatch grouped by Generation Source');
xlabel(ax1, 'Time / hr');
ylabel(ax1, 'Mismatch / MW');
legend(ax1, genmix_header);

ax2 = subplot(4,1,2);
plot(ax2,1:row_num, wind_curt);
title(ax2, 'Wind Curtailment grouped by Area');
xlabel(ax2, 'Time / hr');
ylabel(ax2, 'Curtailment / PCT');
legend(ax2, ["A1","A2","A3","A4","A5","A6","A7","A8"]);

ax3 = subplot(4,1,3);
plot(ax3,1:row_num, pv_curt);
title(ax3, 'Solar Curtailment grouped by Area');
xlabel(ax3, 'Time / hr');
ylabel(ax3, 'Curtailment / PCT');
legend(ax3, ["A1","A2","A3","A4","A5","A6","A7","A8"]);

ax3 = subplot(4,1,4);
plot(ax3,1:row_num, all_renew_curt);
title(ax3, 'Total System-wide Renewable Curtailment');
xlabel(ax3, 'Time / hr');
ylabel(ax3, 'Curtailment / PCT');
legend(ax3, ["wind", "pv"]);