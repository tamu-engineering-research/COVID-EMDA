function curr_dispatch = supply_curve(mpc, P_total, genind)
%SUPPLY_CURVE Implement the supply curve ranking and find corresponding
%dispatch

gen_cost = mpc.gencost(genind, :);
gen_flag = mpc.gen(genind, 8);
gen_max = mpc.gen(genind, 9);

gen_num = size(gen_cost, 1);
increment = 1; % MW

% check feasibility
assert(sum(gen_max) >= P_total);
max_output = sum(mpc.gen(genind, 9) .* gen_flag);
assert(max_output > P_total);

% start with all gen @ Pmin 
curr_dispatch = mpc.gen(genind, 10) .* gen_flag; % initial dispatch
allocated_P = sum(curr_dispatch); % initial value
remaining_P = P_total - allocated_P;

% maintain a list of marginal price
curr_prices = zeros(gen_num, 1);
for i = 1:gen_num
    if gen_flag(i) == 1
        curr_prices(i) = get_gen_marginal_cost(gen_cost(i,:), curr_dispatch(i), increment);
    else
        curr_prices(i) = hex2dec('FFFFFFFF');
    end
end

while remaining_P > increment
    [~, cheapest_ind] = min(curr_prices);
    % if will be maxed out after this iter
    if gen_max(cheapest_ind) - curr_dispatch(cheapest_ind) < increment
        actural_increment = gen_max(cheapest_ind) - curr_dispatch(cheapest_ind);
        curr_prices(cheapest_ind) = hex2dec('FFFFFFFF');
    else 
        actural_increment = increment;
    end
    curr_dispatch(cheapest_ind) = curr_dispatch(cheapest_ind) + actural_increment;
    allocated_P = sum(curr_dispatch);
    remaining_P = P_total - allocated_P;
end