clear;
define_constants;
case_path = "..\..\bte2k\case_Mar3_5pm.mat";

mpc = load(case_path);
mpc = mpc.mpc;
mpc_orig = mpc;

mpopt = mpoption('pf.nr.max_it', 50);
mpopt = mpoption(mpopt,'out.all',0);
mpopt = mpoption(mpopt,'verbose',0); 

new_hvdc_max = 2500;
new_hvdc_bus = 1934;
%new_hvdc_bus = 1979;

base_case = rundcopf(mpc, mpopt);

eta = 0.01;

% relax the line around PCC 
% find lines within distance N
N = 5;
all_brn = explore_node(mpc.branch, mpc.bus(new_hvdc_bus, 1), 0, N);


% find the line flow in orig case
base_flow = zeros(N, 100);
for i = 1:N
    flows = abs(base_case.branch(nonzeros(all_brn(i, :))', 14)) ./ base_case.branch(nonzeros(all_brn(i, :))', 6);
    base_flow(i, 1:size(flows, 1)) = flows';
end
all_brn(base_flow==0) = 0;

all_brn_flat = nonzeros(all_brn);
base_flow_flat = nonzeros(base_flow);
% gradually increase HVDC cap
for cap = 50:50:new_hvdc_max
    mpc.bus(new_hvdc_bus, PD) = -cap;
    curr_case = rundcopf(mpc, mpopt);
    if ~curr_case.success
        disp(cap);
    end
    mpc.branch(all_brn_flat, 6) = abs(curr_case.branch(all_brn_flat, 14)) ./ base_flow_flat;
end
mpc_orig.branch = mpc.branch;
