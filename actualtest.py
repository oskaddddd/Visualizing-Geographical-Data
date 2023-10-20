import math

def calculate_triangle_area(a, b, c):

    # Check if the sides form a valid triangle
    if a + b <= c or a + c <= b or b + c <= a:
        return "Invalid input: These sides cannot form a triangle."

    # Calculate the semi-perimeter (half the perimeter)
    s = (a + b + c) / 2

    # Calculate the area using Heron's formula
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))

    return area

c1 = [float(x) for x in input().split()]
c2 = [float(x) for x in input().split()]
c3 = [float(x) for x in input().split()]
c4 = [float(x) for x in input().split()]

distances = [((c1[0]-c2[0])**2+(c1[1]-c2[1])**2)**0.5, ((c1[0]-c3[0])**2+(c1[1]-c3[1])**2)**0.5, ((c3[0]-c2[0])**2+(c3[1]-c2[1])**2)**0.5, ((c1[0]-c4[0])**2+(c1[1]-c4[1])**2)**0.5, ((c4[0]-c3[0])**2+(c4[1]-c3[1])**2)**0.5, ((c4[0]-c2[0])**2+(c4[1]-c2[1])**2)**0.5]
print(calculate_triangle_area(distances[0],distances[1], distances[2]))
print(calculate_triangle_area(distances[1],distances[2], distances[3]))
print(calculate_triangle_area(distances[2],distances[3], distances[4]))
print(calculate_triangle_area(distances[3],distances[4], distances[5]))
