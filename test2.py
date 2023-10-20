import numpy as np
import time
import random
n = 10
arr = np.empty((n, 3, 2), dtype = np.uint8) 
rang = 30
for x in range(n):
    arr[x] = np.array([(random.randint(0, rang), random.randint(0, rang)), (random.randint(0, rang), random.randint(0, rang)), (random.randint(0, rang), random.randint(0, rang))], dtype = np.uint8)

#arr = arr.tolist()

print(arr)

def box(tri):
    tri = np.array(tri)
    
    #min y x, max y x
    bounds = [(np.min(tri[:, 0]), np.min(tri[:, 1])), (np.max(tri[:, 0]), np.max(tri[:, 1]))]
    output = []

    for y in range(bounds[0][0], bounds[1][0]+1):
        print(y, 'whooo')
        for x in range(bounds[0][1], bounds[1][1]+1):
            print(y, x)
    print(bounds[0][0], bounds[1][0], bounds[0][1], bounds[1][1])
    print(bounds, tri)

box(arr[0])

def oskad():
    pass
