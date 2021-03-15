%% intro
clear;
define_constants;
case_path = "..\bte2k\case_Mar3_5pm.mat";
gen_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Generation by Source\2021-02-01 to 2021-02-19.csv";
%load_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_demand_Feb2021_v20210224.csv";
load_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Demand by Subregion\2021-02-01 to 2021-02-19.csv";
wind_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_wind_Feb2021_v20210224.csv";
solar_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_solar_Feb2016_v20210224.csv";
hydro_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\BES profiles\BES_hydro_Feb2016_v20210224.csv";
lf_path =  "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Demand, Demand Forecast, and Net Interchange\2021-02-01 to 2020-02-19.csv";


out_path = "..\data\out_mat.mat";
shed_path = "..\data\shed_mat.mat";
cap_path = "..\data\ercotcap_mat.mat";
lcf_path = "..\data\lf_mat.mat";

out_ts = load(out_path);
out_ts = out_ts.out_mat;
shed_ts = load(shed_path);
shed_ts = shed_ts.shed_mat;
shed_ts(1:312,3) = NaN;
cap_ts = load(cap_path);
cap_ts = cap_ts.cap_mat;
lcf_ts = load(lcf_path);
lcf_ts = lcf_ts.lf_mat;

mpc = load(case_path);
mpc = mpc.mpc;

% configs
mpopt = mpoption('pf.nr.max_it', 50);
mpopt = mpoption(mpopt,'out.all',0);
mpopt = mpoption(mpopt,'verbose',0); 

[gen_val, gen_ts, ~] = xlsread(gen_path);
gen_ts(1, :) = [];
gen_ts = gen_ts(:, 2);
gen_val(1:24,:) = [];
gen_val(end,:) = [];

[load_val, load_ts, ~] = xlsread(load_path);
load_ts(1, :) = [];
load_val(1:24, :) = [];

[lf_val, lf_ts, ~] = xlsread(lf_path);
lf_ts(1, :) = [];
lf_val(1:24, :) = [];

dcnet_ts = lf_val(:,4);

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


area_mpc = ["FW", "N", "W", "S", "NC", "SC", "C", "E"];
load_rearranged = [load_val(:,3),load_val(:,4),load_val(:,8),load_val(:,6),load_val(:,5),load_val(:,7),load_val(:,1),load_val(:,2)];


%% modify base case gen
mpc.gen(:, GEN_STATUS) = 1;

% change the generator cost to linear (removing c2 in mpc.gencost)
mpc.gen(555, VG) = 1.02;

% save basic thermal capacity
coal_base = sum(mpc.gen(coal_ind,PMAX));
ng_base = sum(mpc.gen(ng_ind,PMAX));
nuke_base = mpc.gen(379, PMAX);


%% modify gen out data
out_ts(isnan(out_ts)) = 0;
%out_ts(:, 6) = out_ts(:, 6) + 500;
%out_ts(:, 5) = out_ts(:, 5) + 750;

out_ts(339, :) = out_ts(338, :);
out_ts(340:342, :) = out_ts(341:343,:);
%out_ts(340:341, :) = out_ts(340:341, :) + 250;

%% modify DC tie flow
dcbus_ind = [145; 1966];
dc_ratio = [0.25, 0.75];

%% change counterfacturals
% anti-frost
weatherization_pct = 0.6; % pct of winterized plants

% hvdc
newdc_cap = 2000;
newdc_id = 3003048;
newdcbus_ind = 272;

% storage
store_cap = 5000; % 5GW

% DR
dr_cap = 3000; % 5GW

% %% line upgrades
% d3mpc = load('..\bte2k\design3.mat');
% d3mpc = d3mpc.mpc;
% mpc.branch(:,RATE_A) = max(mpc.branch(:,RATE_A), d3mpc.branch(d3mpc.branch(:, 1) > 3000000,RATE_A));
% mpc.branch(:,BR_X) = min(mpc.branch(:,BR_X), d3mpc.branch(d3mpc.branch(:, 1) > 3000000,BR_X));



%% looping through hours
% Start with 2/1 0:00
total_rows = size(load_val, 1);
real_date = 1;
real_hr = 0;


% Start with 2/12 0:00
day_tar = 12; % Feb 12
hour_tar = 0;
row_num_start = (day_tar-1) * 24 + hour_tar + 1;
time_steps = row_num_start:409; %load data only up to 2/18

% initialize containers
ts_num = size(time_steps,1);
system_gen = zeros(ts_num,1);
system_load = zeros(ts_num,1);
genmix_mismatch = zeros(ts_num, 7);
genmix_opf = zeros(ts_num, 7);
genmix_cf = zeros(ts_num, 7);
loaddiff_cf = zeros(ts_num, 1);

all_gen_pg = zeros(ts_num, size(mpc.gen, 1));
all_brn_pf = zeros(ts_num, size(mpc.branch, 1));
ci = 1; % container index


for row_num = time_steps
    % fetch and match gen
    for gen_type_i = 1:7
        gen_type = genmix_header(gen_type_i);
        if strcmp(gen_type,'other')
            ;
        else
            type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
            
            % set pmin/max if renewable(allow curtailment), just set PMAX
            if gen_type_i == 1 % wind
                % scale wind according to real EIA data AND anti-frost
                bes_wind = sum(wind_ts(row_num,:));
                eia_wind = gen_val(row_num, gen_type_i);
                real_wind_pct = eia_wind / bes_wind;
                cf_wind_pct = 1 - (1 - real_wind_pct) * (1 - weatherization_pct);
                mpc.gen(type_ind, PG) = wind_ts(row_num,:)' * cf_wind_pct;
                mpc.gen(type_ind, PMIN) = 0;
                mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
            elseif gen_type_i == 2 % solar
                % scale PV according to real EIA
                bes_pv = sum(solar_ts(row_num,:));
                eia_pv = gen_val(row_num, gen_type_i);
                if bes_pv == 0
                    bes_pv = 1;
                end
                real_pv_pct = eia_pv / bes_pv;
                cf_pv_pct = 1 - (1 - real_pv_pct) * (1 - weatherization_pct);
                mpc.gen(type_ind, PG) = solar_ts(row_num,:)';
                mpc.gen(type_ind, PMIN) = 0;
                mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);   
            elseif gen_type_i == 3 % hydro
                mpc.gen(type_ind, PG) = hydro_ts(row_num,:)';
                mpc.gen(type_ind, PMIN) = 0;
                mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
            elseif gen_type_i == 5 % ng
                % scale down system_wide ng capacity
                ng_up = (ng_base - (1 - weatherization_pct) * out_ts(row_num, gen_type_i));
                mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PMAX) * ng_up / sum(mpc.gen(type_ind, PMAX));
            elseif gen_type_i == 6 % coal\
                coal_up = (coal_base - (1 - weatherization_pct) * out_ts(row_num, gen_type_i));
                mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PMAX) * coal_up / sum(mpc.gen(type_ind, PMAX));
%             elseif gen_type_i == 7 % nuke
%                 if out_ts(row_num, gen_type_i) > nuke_base 
%                     mpc.gen(379, GEN_STATUS) = 0;
%                     mpc.gen(379, PMAX) = 0;
%                 else
%                     mpc.gen(379, GEN_STATUS) = 1;
%                     mpc.gen(379, PMAX) = nuke_base - out_ts(row_num, gen_type_i);
%                 end
            end
        end
    end
    
    % reset DC injection
    mpc.bus(dcbus_ind, PD) = 0;
    mpc.bus(newdcbus_ind, PD) = 0;
    
    % fetch and match load
    for load_area_i = 1:8
        real_area = load_area_i + 300;
        load_ind = find(mpc.bus(:, BUS_AREA) == real_area);
        base_load = sum(mpc.bus(load_ind, PD));
        
        if row_num > 313
            dr_area = lcf_ts(row_num, load_area_i) / sum(lcf_ts(row_num, :)) * dr_cap;
        else
            dr_area = 0;
        end
        real_load = lcf_ts(row_num, load_area_i) - dr_area;

        % scale load
        mpc.bus(load_ind, PD) = mpc.bus(load_ind, PD) * real_load / base_load;
        %mpc.bus(load_ind, QD) = mpc.bus(load_ind, QD) * real_load / base_load;
    end

    % modify DC injection
    mpc.bus(dcbus_ind, PD) = dc_ratio * dcnet_ts(row_num);
    mpc.bus(newdcbus_ind, PD) = -newdc_cap;
    
    
    % solve OPF 
    opfres = rundcopf(mpc, mpopt);
    %assert(opfres.success);
    if ~opfres.success
       disp('error'); 
       disp(row_num);
       % use storage
       mpc.bus(mpc.bus(:,PD) > 0, PD) = mpc.bus(mpc.bus(:,PD) > 0, PD) * (sum(mpc.bus(mpc.bus(:,PD) > 0, PD)) - 1000) / sum(mpc.bus(mpc.bus(:,PD) > 0, PD));

    end
    
    % calculate each type of addition
    %if row_num > 313
        
    all_gen_pg(ci, :) = opfres.gen(:, PG)';
    all_brn_pf(ci, :) = opfres.branch(:, PF)';
    
    % plot load and demand
    system_gen(ci, 1) = sum(opfres.gen([coal_ind;ng_ind;nuke_ind],PMAX)) + sum(opfres.gen([wind_ind;pv_ind;hydro_ind],PG));
    system_load(ci, 1) = sum(opfres.bus(:,PD)) - dcnet_ts(row_num) + newdc_cap;
    
    % gen difference by type
    for gen_type_i = 1:7
        gen_type = genmix_header(gen_type_i);
        if gen_type == 'other'
            ;
        else
            type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
            real_gen = gen_val(row_num, gen_type_i);
            opf_gen = sum(opfres.gen(type_ind, PG));
            genmix_mismatch(ci, gen_type_i) = opf_gen - real_gen;
            genmix_opf(ci, gen_type_i) = opf_gen;
            % save counterfactural
            genmix_cf(ci, gen_type_i) = opf_gen - real_gen;
        end
    end
    loaddiff_cf(ci, 1) = sum(lcf_ts(row_num, :)) - sum(load_rearranged(row_num, :));
    
    real_hr = real_hr + 1;
    ci = ci + 1;
    if real_hr == 24
        real_hr = 0;
        real_date = real_date + 1;
    end
    
    
end

all_gen_pg = [double(mpc.genid'); all_gen_pg];
all_brn_pf = [double(mpc.branchid'); all_brn_pf];

%% plot results
% modify genout curve
system_gen(1:48) = system_gen(1:48) - (system_gen(48) - system_gen(49));

ax1 = subplot(2,1,1);
plot(ax1,time_steps, system_gen);
hold on;
plot(ax1,time_steps, system_load);
plot(ax1,time_steps, cap_ts(time_steps,1));
title(ax1, 'Simulated Capacity and Load During the Event');
xlabel(ax1, 'Time / hr');
ylabel(ax1, 'Capacity / MW');
legend(ax1, ["Gen","Load","ERCOT-Capacity"]);

ax2 = subplot(2,1,2);
plot(ax2, time_steps, genmix_mismatch);
title(ax2, 'Dispatch Mismatch grouped by Generation Source');
xlabel(ax2, 'Time / hr');
ylabel(ax2, 'Mismatch / MW');
legend(ax2, genmix_header);
