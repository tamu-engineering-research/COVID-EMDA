function inc_cost = get_gen_marginal_cost(gencost, Pout, increment)
%GET_COST Summary of this function goes here
%  COMPUT THE MARGINAL COST OF A GEN GIVEN CURRENT OUTPUT
Pnext = Pout + increment;
if gencost(1) == 1 % PW-L model
    %xs = gencost([5,7,9,11,13]);
    %ys = gencost([6,8,10,12,14]);    
    xs = gencost([5,7]);
    ys = gencost([6,8]);
    
    
    % find the corresponding segment
    pos = 0;
    for i = 1:4
        if Pout >= xs(i)
            pos = pos + 1;
        else
            break;
        end
    end
    
    % compute marginal cost using numerical differencing
    curr_cost = ys(pos) + (Pout - xs(pos)) * (ys(pos+1) - ys(pos)) / (xs(pos+1) - xs(pos));
    next_cost = ys(pos) + (Pnext - xs(pos)) * (ys(pos+1) - ys(pos)) / (xs(pos+1) - xs(pos));
    
else
    c = gencost([5,6,7]);
    curr_cost = c(1)*Pout^2 + c(2)*Pout + c(3);
    next_cost = c(1)*Pnext^2 + c(2)*Pnext + c(3);
    
end
inc_cost = next_cost - curr_cost;