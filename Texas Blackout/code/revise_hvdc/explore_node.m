function brn_list = explore_node(brn, root, last, N)
%EXPLORE_NODE FIND ALL BRANCHES WITHIN DISTANCE N
%   Return mat with size N x ?
%   
all_N = zeros(N, 100);
all_B = zeros(N, 100);
brn_num = size(brn, 1);

% find all neighbours
for n = 1:N
    if n == 1
        roots = root;
    else
        roots = nonzeros(all_N(n-1,:));
    end
    if n > 2
        last = all_N(n-2,:);
    end
    curr_N = [];
    curr_B = [];
    for r = roots'
        % find all roots
        for i = 1:brn_num
            if brn(i, 1) == r && ~ismember(brn(i, 2), last)
                curr_N = [curr_N, brn(i, 2)];
                curr_B = [curr_B, i];
            elseif brn(i, 2) == r && ~ismember(brn(i, 1), last)
                curr_N = [curr_N, brn(i, 1)];
                curr_B = [curr_B, i];
            end
        end
    end
    all_N(n,1:size(curr_N, 2)) = curr_N;
    all_B(n,1:size(curr_B, 2)) = curr_B;
end

brn_list = all_B;