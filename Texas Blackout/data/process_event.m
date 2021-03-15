load_shed_path = "load_shed_processed.csv";
capacity_out_path = "capacity_out_processed.csv";
ercot_cap_path = "ercot_capacity.csv";

[shed_val, shed_ts, ~] = xlsread(load_shed_path);
shed_ts(1,:) = [];
[out_val, out_ts, ~] = xlsread(capacity_out_path);
out_ts(1,:) = [];
[cap_val, cap_ts, ~] = xlsread(ercot_cap_path);
cap_ts(1,:) = [];


% rearrangel capacity out columns
genmix_header = ["wind", "solar", "hydro", "other", "ng", "coal", "nuclear"];
out_rearranged = zeros(size(out_val,1),7);
out_rearranged(:,1) = out_val(:,5);
out_rearranged(:,2) = out_val(:,4);
out_rearranged(:,5) = out_val(:,2);
out_rearranged(:,6) = out_val(:,1);
out_rearranged(:,7) = out_val(:,3);


shed_mat = zeros(432, 3);
out_mat = zeros(432, 8);
cap_mat = zeros(432, 2);
ind_start = 313;
ct = 0;
for i = 1:size(shed_ts,1)
    if mod(i,6) == 1
        shed_mat(ind_start + ct, :) = shed_val(i,[1,2,4]);
        out_mat(ind_start + ct, 1:7) = out_rearranged(i, :);
        ct = ct + 1; 
    end 
end
cap_mat(1:264, :) = NaN;
cap_mat(265:end, :) = cap_val(:, :);
shed_mat(433:end,:) = [];
out_mat(433:end,:) = [];

