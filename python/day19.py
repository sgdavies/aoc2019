from computer import Computer
import pickle, sys

program = [109,424,203,1,21102,1,11,0,1106,0,282,21101,0,18,0,1106,0,259,1202,1,1,221,203,1,21101,0,31,0,1105,1,282,21102,38,1,0,1105,1,259,20102,1,23,2,21201,1,0,3,21102,1,1,1,21101,0,57,0,1105,1,303,2101,0,1,222,20102,1,221,3,21002,221,1,2,21101,0,259,1,21101,0,80,0,1106,0,225,21102,1,152,2,21101,91,0,0,1106,0,303,1201,1,0,223,21001,222,0,4,21101,0,259,3,21102,225,1,2,21101,0,225,1,21102,1,118,0,1105,1,225,20101,0,222,3,21102,61,1,2,21101,133,0,0,1106,0,303,21202,1,-1,1,22001,223,1,1,21102,148,1,0,1105,1,259,2101,0,1,223,21001,221,0,4,21001,222,0,3,21101,0,14,2,1001,132,-2,224,1002,224,2,224,1001,224,3,224,1002,132,-1,132,1,224,132,224,21001,224,1,1,21101,0,195,0,105,1,109,20207,1,223,2,20101,0,23,1,21102,-1,1,3,21102,214,1,0,1105,1,303,22101,1,1,1,204,1,99,0,0,0,0,109,5,2101,0,-4,249,21202,-3,1,1,21202,-2,1,2,21201,-1,0,3,21102,1,250,0,1106,0,225,22101,0,1,-4,109,-5,2106,0,0,109,3,22107,0,-2,-1,21202,-1,2,-1,21201,-1,-1,-1,22202,-1,-2,-2,109,-3,2105,1,0,109,3,21207,-2,0,-1,1206,-1,294,104,0,99,22102,1,-2,-2,109,-3,2105,1,0,109,5,22207,-3,-4,-1,1206,-1,346,22201,-4,-3,-4,21202,-3,-1,-1,22201,-4,-1,2,21202,2,-1,-1,22201,-4,-1,1,21202,-2,1,3,21101,343,0,0,1106,0,303,1105,1,415,22207,-2,-3,-1,1206,-1,387,22201,-3,-2,-3,21202,-2,-1,-1,22201,-3,-1,3,21202,3,-1,-1,22201,-3,-1,2,22101,0,-4,1,21101,0,384,0,1106,0,303,1105,1,415,21202,-4,-1,-4,22201,-4,-3,-4,22202,-3,-2,-2,22202,-2,-4,-4,22202,-3,-2,-3,21202,-4,-1,-2,22201,-3,-2,1,21201,1,0,-4,109,-5,2106,0,0]

SIZE=50
MAX=SIZE-1

if True:
    pulled={}

    for x in range(SIZE):
        for y in range(SIZE):
            tractor_detector = Computer(program, inputs=[x,y])
            out_arr = tractor_detector.run()
            out=out_arr[0]

            pulled[(x,y)] = out

    print(len([p for p in pulled if pulled[p]]))

    with open("day19.pickle", 'wb') as pickle_file:
        pickle.dump(pulled, pickle_file)

with open("day19.pickle", 'rb') as pickle_file:
    pulled = pickle.load(pickle_file)

print(len([p for p in pulled if pulled[p]]))

for x in range(SIZE):
    if (x,MAX) in pulled:
        print("Top:", x, MAX)
        top_slope = x/MAX
        break

assert(not pulled[(MAX,MAX)])  # Slope misses y-end of box
for x in range(SIZE, 0, -1):
    if (x, MAX) in pulled:
        print("Bottom:", x, MAX)
        bottom_slope = x/MAX
        break

print("{:.2f} / {:.2f}".format(top_slope, bottom_slope))

# top_slope is 0.57
# bottom slope is 0.69
# so y(top) = 0.57*x and y(bottom) = 0.69*x
# We want y(top) - y(bottom) >= 100
# (0.69 - 0.57)*x >= 100
# 0.122*x >= 100
# x >= 816
# But: actually need to fit triangular shape containing (100x100), so need x>=200
# so x >= 1633 (right-hand end of box), x ~= 1534 (left-hand end of box)
#
# ..............##############............
# ...............###############..........
# ................###############.........
# ................#################.......
# .................########AOOOOOOOOB.....
# ..................#######OOOOOOOOOO#....
# ...................######OOOOOOOOOO###..
# ....................#####OOOOOOOOOO#####
# .....................####OOOOOOOOOO#####
# .....................####OOOOOOOOOO#####
# ......................###OOOOOOOOOO#####
# .......................##OOOOOOOOOO#####
# ........................#OOOOOOOOOO#####
# .........................COOOOOOOOD#####
# ..........................##############
# ..........................##############
# ...........................#############
# ............................############
# .............................###########
# coords are:
# A (x, y)  B (x+99, y)  C (x, y+99)  D (x+99, y+99)
# Where x ~= 1534 - so 877 < y < 1064

def test_point(x,y):
    if (x,y) not in pulled:
        pulled[(x,y)] = Computer(program, inputs=[x,y]).run().pop()

    return pulled[(x,y)]

def test(x,y):
    # B and C should just be inside
    # x,y are the coords of A
    # Returns Au..Bu
    #       Al A..B Br
    #          .  .
    #       Cl C..D Dr
    #         Cd..Dd
    row=y
    b = test_point(x+99, row)
    
    row=y+99
    c = test_point(x, row)
    
    return b and c

def test_slow(x,y):
    # B and C should just be inside
    # x,y are the coords of A
    # Returns Au..Bu
    #       Al A..B Br
    #          .  .
    #       Cl C..D Dr
    #         Cd..Dd
    row = y-1
    au = test_point(x, row)
    bu = test_point(x+99, row)

    row=y
    al = test_point(x-1, row)
    a = test_point(x, row)
    b = test_point(x+99, row)
    br = test_point(x+99+1, row)

    row=y+99
    cl = test_point(x-1, row)
    c = test_point(x, row)
    d = test_point(x+99, row)
    dr = test_point(x+99+1, row)

    row=y+99+1
    cd = test_point(x, row)
    dd = test_point(x+99, row)

    print(" {}..{}\n{}{}..{}{}\n .  .\n{}{}..{}{}\n {}..{}".format(au,bu,al,a,b,br,cl,c,d,dr,cd,dd))

    return a and b and c and d

# 877, 1473 is just inside:
# test(877, 1473)
#  1..1
# 11..11
#  .  .
# 01..11
#  1..1
x=877
y=1473

going_up = True

# Need to go up
while True:
    if going_up:
        if test(x, y-1):
            y -= 1
        else:
            # That would go over the edge at the top.
            if test(x-1, y):
                # We can go left
                going_up = False
                print("top", x, y); sys.stdout.flush()
            else:
                # We've hit the limit
                print(x,y)
                print(10000*x + y)
                break
    else:
        # going left
        if test(x-1, y):
            x -= 1
        else:
            # That would go over at the left
            if test(x, y-1):
                # We can go up
                going_up = True
                print("left", x, y); sys.stdout.flush()
            else:
                # We've hit the limit
                print(x,y)
                print(10000*x + y)
                break

# Ran - got 672/1105 - but 6721105 was 'too high'
# But - can iterate in&up (at the same time) and do better - which the above can't handle.
# Manually got to:
# 667-1097

import pdb; pdb.set_trace()
