import random
import json
from perlin_noise import PerlinNoise

n = 70
corners = [[53.85405444949857, 20.840097270351063], [56.60326420819254, 27.22864675471188]]
y = [corners[0][1], corners[1][1]]
x = [corners[0][0], corners[1][0]]

ky = abs(y[0] - y[1])
kx = abs(x[0] - x[1])

k = n/(ky+kx)
nx = round(k*kx)
ny = round(k*ky)

kkx = kx/nx
kky = ky/ny
arr = []

my = min(y)
mx = min(x)


noise = PerlinNoise(octaves=7, seed=986792)

for xi in range(nx):
    for yi in range(ny):
        arr.append({"GPS": [str(mx+kkx*xi), str(my+kky*yi)], "Value": int((noise([xi/nx, yi/ny])+1)*50)})
        #print([mx+kkx*xi, my+kky*yi])
with open('data.json', 'w') as f:
    json.dump(arr, f, indent=2)
print(nx, ny, "\n", kx, ky, nx*ny)

