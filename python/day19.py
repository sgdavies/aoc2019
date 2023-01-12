from computer import Computer

program = [109,424,203,1,21102,1,11,0,1106,0,282,21101,0,18,0,1106,0,259,1202,1,1,221,203,1,21101,0,31,0,1105,1,282,21102,38,1,0,1105,1,259,20102,1,23,2,21201,1,0,3,21102,1,1,1,21101,0,57,0,1105,1,303,2101,0,1,222,20102,1,221,3,21002,221,1,2,21101,0,259,1,21101,0,80,0,1106,0,225,21102,1,152,2,21101,91,0,0,1106,0,303,1201,1,0,223,21001,222,0,4,21101,0,259,3,21102,225,1,2,21101,0,225,1,21102,1,118,0,1105,1,225,20101,0,222,3,21102,61,1,2,21101,133,0,0,1106,0,303,21202,1,-1,1,22001,223,1,1,21102,148,1,0,1105,1,259,2101,0,1,223,21001,221,0,4,21001,222,0,3,21101,0,14,2,1001,132,-2,224,1002,224,2,224,1001,224,3,224,1002,132,-1,132,1,224,132,224,21001,224,1,1,21101,0,195,0,105,1,109,20207,1,223,2,20101,0,23,1,21102,-1,1,3,21102,214,1,0,1105,1,303,22101,1,1,1,204,1,99,0,0,0,0,109,5,2101,0,-4,249,21202,-3,1,1,21202,-2,1,2,21201,-1,0,3,21102,1,250,0,1106,0,225,22101,0,1,-4,109,-5,2106,0,0,109,3,22107,0,-2,-1,21202,-1,2,-1,21201,-1,-1,-1,22202,-1,-2,-2,109,-3,2105,1,0,109,3,21207,-2,0,-1,1206,-1,294,104,0,99,22102,1,-2,-2,109,-3,2105,1,0,109,5,22207,-3,-4,-1,1206,-1,346,22201,-4,-3,-4,21202,-3,-1,-1,22201,-4,-1,2,21202,2,-1,-1,22201,-4,-1,1,21202,-2,1,3,21101,343,0,0,1106,0,303,1105,1,415,22207,-2,-3,-1,1206,-1,387,22201,-3,-2,-3,21202,-2,-1,-1,22201,-3,-1,3,21202,3,-1,-1,22201,-3,-1,2,22101,0,-4,1,21101,0,384,0,1106,0,303,1105,1,415,21202,-4,-1,-4,22201,-4,-3,-4,22202,-3,-2,-2,22202,-2,-4,-4,22202,-3,-2,-3,21202,-4,-1,-2,22201,-3,-2,1,21201,1,0,-4,109,-5,2106,0,0]

SIZE=50

def test_point(point):
    if point not in pulled:
        x,y = point
        pulled[point] = Computer(program, inputs=[x,y]).run().pop()
    return pulled[point]

# Not all rows contain scan points at the start:
# 10000000000
# 00000000000
# 00000000000
# 00100000000
# 00000000000
# 00010000000
# 00001000000
# 00000000000
# 00000100000
# 00000010000
# 00000010000
start=11
pulled={}
for x in range(start):
    for y in range(start):
        pulled[(x,y)] = test_point((x,y))

#print("\n".join(["".join([str(pulled[(x,y)]) for x in range(start)]) for y in range(start)]))

initial_points = sum(pulled.values())
xs = [p[0] for p in pulled.keys() if p[1] == start-1 and pulled[p] == 1]
xl = min(xs)
xr = max(xs)
#print(xl,xr)
for y in range(start,SIZE):
    # xl (left) is either directly below, or somewhere over to the right
    while not test_point((xl,y)):
        xl+=1
    # xr - the first point that could be outside the beam is one down & right.
    while test_point((xr+1,y)):
        xr+=1
    initial_points += 1+min(xr,SIZE-1)-xl
    #print(y,xl,xr,initial_points, 1+min(xr,SIZE-1)-xl)

print(initial_points)
#print("Starting scan...")
assert(xl < SIZE)  # If not beam is at a different angle and the sums above are incorrect
bottom_edge_point = (xl, SIZE-1)
assert(test_point(bottom_edge_point))
x,y = bottom_edge_point
while True:
    if test_point((x+99,y-99)):
        #print(x,y-99)
        print(10000*x + y-99)
        exit(0)
    # increment point
    y += 1
        
    while not test_point((x,y)):
        x+=1

print("Failed to find an answer")
exit(1)
