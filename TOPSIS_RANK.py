#get weighted normalized matirx
weighted_nor_mx = [[0, 0, 0, 0, 0, 0] for i in range(len(self.network))]
for i in range(len(self._perf_mx)):
  for k in range(len(weight_mx)):
    weighted_nor_mx[i][k] = self._perf_mx[i][k] * weight_mx[k]

# get max and min of column matrix
max_list = list(map(max, zip(*weighted_nor_mx)))
min_list = list(map(min, zip(*weighted_nor_mx)))

## max_list - weighted_nor_mx
max_weight_nor_mx = [[0, 0, 0, 0, 0, 0] for i in range(len(self.network))]
min_weight_nor_mx = [[0, 0, 0, 0, 0, 0] for i in range(len(self.network))]
for i in range(len(weighted_nor_mx)):
  for k in range(len(max_list)):
    max_weight_nor_mx[i][k] = max_list[k] - weighted_nor_mx[i][k]
    min_weight_nor_mx[i][k] = min_list[k] - weighted_nor_mx[i][k]

s_plus_mx = [[] for i in range(len(self.network))]
for _idx in range(len(max_weight_nor_mx)):
  s_plus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
                                  max_weight_nor_mx[_idx]))]
s_minus_mx = [[] for i in range(len(self.network))]
for _idx in range(len(min_weight_nor_mx)):
  s_minus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
                                    min_weight_nor_mx[_idx]))]
## s_plus_mx + s_minus_mx
s_plus_plus = [[0] for i in range(1, len(self.network)+1)]
for i in range(len(s_plus_mx)):
  for k in range(len(s_plus_plus[i])):
    s_plus_plus[i][k] = s_plus_mx[i][k] + s_minus_mx[i][k]
s_plus_plus_dict = {}
for idx, k in enumerate(self.vertices):
  s_plus_plus_dict[k] = s_plus_plus[idx][0]

## get rank values
rank_dict = {}
for idx, k in enumerate(self.vertices):
  # rank_dict[k] = s_minus_mx[idx][0]/s_plus_plus[idx][0]
  rank_dict[k] = 0 if (s_minus_mx[idx][0] == 0 and s_plus_plus[idx][0] ==
                        0) else s_minus_mx[idx][0]/s_plus_plus[idx][0]
## generate rank for nodes
node_rank = {key: rank for rank, key in enumerate(sorted(rank_dict,
                                                          key=rank_dict.get, reverse=True), 1)}
print ('+' * 50 + '\n')
print ('Rank generation value for nodes \n%s'% rank_dict)
print
print ('Rank generated for nodes')
for i in node_rank:
  print( 'Node %s Rank is %s' % (i,node_rank[i]))
return node_rank
