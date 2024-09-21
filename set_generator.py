import itertools


a = list(itertools.combinations(range(4), 2))

print(a)
mask = [False, False, False, False, True, True, True, False, False, False, False, False]


print(list(itertools.compress(a, mask)))
