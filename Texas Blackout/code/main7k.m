%% intro
clear;
define_constants;
case_path = "..\Texas7k\Texas7k_20210206.m";
gen_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Generation by Source\2021-02-01 to 2021-02-19.csv";
load_path = "..\From EIA (Generation, Demand, Demand Forecasts, and Interchange by BA)\ERCOT Demand by Subregion\2021-02-01 to 2021-02-19.csv";

mpc = loadcase(case_path);

[gen_val, gen_ts, garbage1] = xlsread(gen_path);
gen_ts(1, :) = [];
gen_ts = gen_ts(:, 2);

[load_val, load_ts, garbage2] = xlsread(load_path);
load_ts(1, :) = [];
load_ts = load_ts(:, 2);


genmix_header = ["wind", "solar", "hydro", "other", "ng", "coal", "nuclear"];
% source: http://www.ercot.com/content/wcm/lists/219736/ERCOT_Fact_Sheet_2.12.21.pdf
genmix_pct = [0.248, 0.038, 0.002, 0.019, 0.51, 0.134, 0.049];

coal_ind = find(strcmp(mpc.genfuel, 'coal') == 1);
pv_ind = find(strcmp(mpc.genfuel, 'solar') == 1);
hydro_ind = find(strcmp(mpc.genfuel, 'hydro') == 1);
ng_ind = find(strcmp(mpc.genfuel, 'ng') == 1);
nuke_ind = find(strcmp(mpc.genfuel, 'nuclear') == 1);
wind_ind = find(strcmp(mpc.genfuel, 'wind') == 1);
other_ind = find(strcmp(mpc.genfuel, 'other') == 1);

% modify generator sizes
mpc.gen(nuke_ind, PMAX) = mpc.gen(nuke_ind, PMAX) / sum(mpc.gen(nuke_ind, PMAX)) * 5200;


% coal_names = [];
% for i = coal_gens(:, 1)'
%     coal_names = [coal_names; mpc.bus_name(find(mpc.bus(:,1) == i))];
% end
area_mpc = ["FW", "N", "W", "S", "NC", "SC", "C", "E"];
load_rearranged = [load_val(:,3),load_val(:,4),load_val(:,8),load_val(:,6),load_val(:,5),load_val(:,7),load_val(:,1),load_val(:,2)];

%% re-number base case areas
for i = 1:size(mpc.bus, 1)
    if mpc.bus(i, BUS_AREA) == 1 
        mpc.bus(i, BUS_AREA) = 7;
    elseif mpc.bus(i, BUS_AREA) == 2
        mpc.bus(i, BUS_AREA) = 6;
    elseif mpc.bus(i, BUS_AREA) == 3
        mpc.bus(i, BUS_AREA) = 5;
    elseif mpc.bus(i, BUS_AREA) == 4
        mpc.bus(i, BUS_AREA) = 6;
    elseif mpc.bus(i, BUS_AREA) == 5
        mpc.bus(i, BUS_AREA) = 5;
    elseif mpc.bus(i, BUS_AREA) == 6
        mpc.bus(i, BUS_AREA) = 4;
    elseif mpc.bus(i, BUS_AREA) == 7
        mpc.bus(i, BUS_AREA) = 2;
    elseif mpc.bus(i, BUS_AREA) == 8
        mpc.bus(i, BUS_AREA) = 4;
    elseif mpc.bus(i, BUS_AREA) == 9
        mpc.bus(i, BUS_AREA) = 1;
    elseif mpc.bus(i, BUS_AREA) == 10
        mpc.bus(i, BUS_AREA) = 4;
    elseif mpc.bus(i, BUS_AREA) == 11
        mpc.bus(i, BUS_AREA) = 5;
    elseif mpc.bus(i, BUS_AREA) == 12
        mpc.bus(i, BUS_AREA) = 1;
    elseif mpc.bus(i, BUS_AREA) == 13
        mpc.bus(i, BUS_AREA) = 6;
    elseif mpc.bus(i, BUS_AREA) == 14
        mpc.bus(i, BUS_AREA) = 3;
    elseif mpc.bus(i, BUS_AREA) == 15
        mpc.bus(i, BUS_AREA) = 8;
    elseif mpc.bus(i, BUS_AREA) == 16
        mpc.bus(i, BUS_AREA) = 5;
    elseif mpc.bus(i, BUS_AREA) == 17
        mpc.bus(i, BUS_AREA) = 6;
    end
        
        
    
end


%% modify base case gen
%mpcm.gen(:, GEN_STATUS) = 1;

% change the generator cost to linear (removing c2 in mpc.gencost)
mpc.gencost(:,4) = 2;

%% params
% Start with 1/31 0:00
day_skipped = 1; % Feb 12
hour_skipped = 6;
row_num = day_skipped * 24 + hour_skipped + 1;

% fetch and match gen
for gen_type_i = 1:7
    gen_type = genmix_header(gen_type_i);

    type_ind = find(strcmp(mpc.genfuel, gen_type) == 1);
    base_gen = sum(mpc.gen(type_ind, PG));
    real_gen = gen_val(row_num, gen_type_i);

    % use supply curve to rank non-renewable gens
    

    % supply-curve dispath for non renewables

    % set pmin/max if renewable
    if gen_type_i < 4
        mpc.gen(type_ind, PG) = mpc.gen(type_ind, PG) * real_gen / base_gen;
        mpc.gen(type_ind, QG) = mpc.gen(type_ind, QG) * real_gen / base_gen;
        mpc.gen(type_ind, PMIN) = mpc.gen(type_ind, PG);
        mpc.gen(type_ind, PMAX) = mpc.gen(type_ind, PG);
        mpc.gen(type_ind, QMIN) = mpc.gen(type_ind, QG);
        mpc.gen(type_ind, QMAX) = mpc.gen(type_ind, QG);
    else
        mpc.gen(type_ind, PG) = supply_curve(mpc, real_gen,type_ind);
    end
end

% fetch and match load
for load_area_i = 1:8
    load_ind = find(mpc.bus(:, BUS_AREA) == load_area_i);
    base_load = sum(mpc.bus(load_ind, PD));
    real_load = load_rearranged(row_num, load_area_i);
    
    disp(real_load / base_load);
    % scale load
    mpc.bus(load_ind, PD) = mpc.bus(load_ind, PD) * real_load / base_load;
    mpc.bus(load_ind, QD) = mpc.bus(load_ind, QD) * real_load / base_load;
    
end
