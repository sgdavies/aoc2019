from computer import Computer
import random, sys

MAX_STEPS=100
solution = None

def draw_the_map(mapp, dx=None, dy=None):
    drawn_map = []
    minx = min([x for x,y in mapp.keys()])
    maxx = max([x for x,y in mapp.keys()])
    miny = min([y for x,y in mapp.keys()])
    maxy = max([y for x,y in mapp.keys()])

    if dx is not None and dy is not None:
        current_square = mapp[(dx,dy)]
        if current_square != 'O': mapp[(dx,dy)] = 'D'

    for y in range(miny, maxy+1):
        row = ""
        for x in range(minx, maxx+1):
            row += (mapp.get((x,y), " "))
        row = row.rstrip()
        if len(row) > 0: drawn_map.append(row)

    print("\n".join(drawn_map))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")
    sys.stdout.flush()

    if dx is not None and dy is not None:
        mapp[(dx,dy)] = current_square

def move(direction, x, y):
    if direction==1:
        # North (y increases downwards)
        return x, y-1
    elif direction==2:
        # South
        return x, y+1
    elif direction==3:
        # West
        return x-1, y
    elif direction==4:
        # East
        return x+1, y
    else:
        print(direction)
        assert(False)

def find_best_direction(x,y, mapp):
    directions = [1,2,3,4]
    random.shuffle(directions)
    while directions:
        direction = directions.pop()
        x1, y1 = move(direction, x, y)
        if (x1,y1) not in mapp:
            # Virgin territory!
            return x1, y1, direction
        elif mapp[(x1,y1)] == "#":
            # Known dead end - don't bother
            pass
        else:
            # We've been here before - save off this as worth trying if there's no virgin option
            okx, oky, okdir = x1,y1, direction

    return okx, oky, okdir

def attempt_move(direction, x, y):
    droid.inputs.append(direction)
    out, halted = droid.run()
    assert(not halted)

    x1, y1 = move(direction, x, y)

    if out==2:
        # Move
        x,y = x1,y1
        mapp[(x,y)] = "O"
    elif out==1:
        # Move
        x,y = x1,y1
        mapp[(x,y)] = "."
    elif out==0:
        # Don't move
        mapp[(x1,y1)] = '#'
    else:
        print(mapp)
        print(out)
        draw_the_map(mapp)
        assert(False)

    global solution
    if out == 2:
        # Finished!
        if solution is None:
            print("Found solution at ({},{})".format(x,y))
            solution = (x,y)
        return x, y, out, True
    else:
        # didn't finish - draw final robot position
        # mapp[(x,y)] = "D"
        return x, y, out, False

def rotate(direction, which_way):
    # direction - which way you're currently headed
    # which_way - "left" or "right" - which way to turn
    # return - direction to head next
    LEFT  = {1:3, 2:4, 3:2, 4:1}
    RIGHT = {1:4, 2:3, 3:1, 4:2}
    ROTATE={"left":LEFT, "right":RIGHT}

    return ROTATE[which_way][direction]

def flood(mapp, start):
    # Flood the map from the start point. Return how many steps it took.
    mapp[(0,0)] = '.'
    mapp[start] = '.'
    active = [start]
    for step in range(1000):
        num_to_write = str(((step+9)//10)%10)  # 0=0, 1..10=1, 11..20=2, etc # str(step%10) #
        new_active = []
        # import pdb; pdb.set_trace()
        #for active_point in list(active):
        for active_point in active:
            #active.remove(active_point)
            print("=",active_point)
            mapp[active_point] = num_to_write
            if active_point == (0,0): steps_to_end = step

            for direction in ([1,2,3,4]):
                potential_next = move(direction, active_point[0], active_point[1])
                if mapp.get(potential_next,'') == '.' and potential_next not in new_active:
                    new_active.append(potential_next)

        #active += new_active
        active += new_active

        if not active:
            return steps_to_end, step

OTHER_WAY = {"left":"right", "right":"left"}

program=[3,1033,1008,1033,1,1032,1005,1032,31,1008,1033,2,1032,1005,1032,58,1008,1033,3,1032,1005,1032,81,1008,1033,4,1032,1005,1032,104,99,1001,1034,0,1039,1002,1036,1,1041,1001,1035,-1,1040,1008,1038,0,1043,102,-1,1043,1032,1,1037,1032,1042,1106,0,124,1001,1034,0,1039,102,1,1036,1041,1001,1035,1,1040,1008,1038,0,1043,1,1037,1038,1042,1105,1,124,1001,1034,-1,1039,1008,1036,0,1041,102,1,1035,1040,1002,1038,1,1043,101,0,1037,1042,1105,1,124,1001,1034,1,1039,1008,1036,0,1041,102,1,1035,1040,1001,1038,0,1043,101,0,1037,1042,1006,1039,217,1006,1040,217,1008,1039,40,1032,1005,1032,217,1008,1040,40,1032,1005,1032,217,1008,1039,33,1032,1006,1032,165,1008,1040,33,1032,1006,1032,165,1101,0,2,1044,1106,0,224,2,1041,1043,1032,1006,1032,179,1102,1,1,1044,1105,1,224,1,1041,1043,1032,1006,1032,217,1,1042,1043,1032,1001,1032,-1,1032,1002,1032,39,1032,1,1032,1039,1032,101,-1,1032,1032,101,252,1032,211,1007,0,42,1044,1106,0,224,1102,0,1,1044,1106,0,224,1006,1044,247,1001,1039,0,1034,1001,1040,0,1035,1001,1041,0,1036,1001,1043,0,1038,102,1,1042,1037,4,1044,1106,0,0,6,28,51,33,63,27,52,11,53,13,96,8,87,11,23,65,43,11,13,9,37,66,68,40,19,41,6,90,28,19,38,86,38,22,7,44,36,23,17,1,16,54,36,74,14,79,2,14,83,10,38,19,62,66,27,56,33,52,47,98,41,39,77,83,48,29,49,15,80,59,9,72,79,55,24,66,50,24,27,56,37,41,13,72,35,13,64,70,5,66,78,37,78,24,43,93,22,41,30,58,14,45,6,27,44,48,40,52,31,12,3,72,7,14,59,35,17,63,34,79,93,17,54,98,35,21,91,25,32,77,10,31,88,17,35,79,96,11,83,15,48,9,19,64,24,65,86,32,71,22,88,55,31,18,88,68,34,40,94,1,71,24,40,44,28,43,4,98,21,80,17,53,2,94,6,43,59,23,66,63,12,30,45,39,93,41,85,43,51,18,99,59,86,40,36,26,94,33,41,28,66,79,81,11,61,46,32,72,71,47,39,22,69,60,36,50,12,44,28,41,79,17,6,74,8,56,39,33,67,23,20,51,12,7,26,57,1,92,80,11,52,19,5,54,13,41,56,37,22,57,43,18,97,27,83,30,3,77,85,66,64,17,99,27,25,95,40,81,97,13,35,46,14,25,63,36,72,87,20,96,29,2,69,90,27,27,91,52,14,14,73,55,4,73,19,85,39,84,23,23,90,40,5,88,53,77,8,92,11,82,66,6,27,84,53,38,93,34,37,58,20,43,25,73,78,30,17,92,54,38,26,67,16,30,28,79,77,26,3,15,82,59,34,34,18,44,34,33,83,35,90,31,58,44,16,18,65,8,70,90,32,46,21,41,54,39,43,93,23,99,11,43,50,98,33,34,53,54,53,16,39,88,53,36,69,85,26,44,38,62,98,6,79,26,35,49,67,22,11,74,35,80,4,50,18,54,4,10,4,58,4,46,20,15,77,73,11,41,58,85,39,87,37,73,36,36,67,28,12,17,34,53,38,89,96,34,39,67,64,33,81,37,74,88,20,84,94,53,39,57,73,13,76,1,35,14,73,29,29,23,73,52,16,85,87,33,48,13,2,93,78,7,17,60,49,13,36,89,40,25,44,55,26,81,37,31,84,31,62,2,66,77,23,88,11,81,9,63,46,19,35,54,17,85,24,1,86,28,72,1,1,61,27,38,81,8,67,82,3,11,77,35,62,83,20,28,61,37,37,92,22,72,76,37,52,17,62,68,38,53,2,57,82,67,25,11,59,3,49,97,1,40,91,75,7,85,98,33,90,1,37,57,14,34,67,65,20,85,10,18,86,20,52,84,24,20,70,10,64,16,64,2,15,85,36,28,7,87,47,44,9,29,54,83,28,37,81,68,18,12,80,26,98,97,25,86,69,39,70,22,23,72,15,56,94,27,14,13,8,50,73,90,24,95,14,41,57,22,67,25,80,46,39,84,80,19,22,63,53,45,62,21,84,36,69,41,44,96,38,92,21,23,64,35,11,75,57,88,6,7,90,10,36,19,68,78,23,62,34,49,4,80,38,2,70,48,39,55,20,22,39,8,90,64,38,39,47,41,63,72,5,10,72,88,35,50,5,66,30,80,74,23,97,39,98,19,17,85,38,34,62,37,25,58,15,93,37,13,71,72,72,4,84,40,92,61,88,9,7,62,59,87,17,36,39,43,21,11,16,58,16,58,20,66,18,83,33,66,62,90,32,74,15,58,62,43,16,66,22,90,2,68,30,54,18,59,22,50,12,60,35,66,77,51,36,64,89,82,21,85,0,0,21,21,1,10,1,0,0,0,0,0,0]
droid = Computer(program, pause_on_output=True)
out=0

mapp={}
x=0
y=0
mapp[(x,y)] = 'X' # Origin

if False:
    # This doesn't work - need to drive the robot around in order to search
    # Replace with: drive until there is a junction; from the junction recurse
    # choose a direction, drive until there is a junction but remember your steps.
    # on reaching a dead end, retrace your steps.
    # don't go down junctions that have already been visited.
    # Reaching an already-visited square is equivalent to reaching a dead end.
    visited = set()
    candidates = set([(x,y)])
    while candidates:
        can = candidates.pop()
        visited.add(can)
        nx,ny=can
        for pair in [(1,2),(2,1),(3,4),(4,3)]:
            there,back = pair
            tx,ty,out,_ = attempt_move(there,nx,ny)
            if out == 2:
                oxygen = (tx,ty)
            if out != 0:
                if (tx,ty) not in visited: candidates.add((tx,ty))
                bx,by,_,_ = attempt_move(back,tx,ty)
                assert(nx==bx and ny==by) # We should be back where we were
    draw_the_map(mapp)
    steps, minutes = flood(mapp, oxygen)
    print("Shortest origin->oxygen is {} steps".format(steps))
    print("Flooded in {} minutes".format(minutes))
    exit()

else:
  while True:
    user_input = " "
    while user_input not in "xdslrf":
        user_input = input("Enter instruction: list of (d)irections, run for number of (s)teps, hug the (l)eft or (r)ight wall, or (f)lood current map, or e(x)it): ")

    if user_input == 'x':
        break
    elif user_input == 'd':
        # get directions
        ii = input("Enter directions (1N,2S,3W,4E) separated by spaces: ")
        try:
            directions = [int(d) for d in ii.split(" ")]
        except:
            print("Bad input: <{}>".format(ii))
            continue

        for direction in directions:
            x, y, out, found = attempt_move(direction, x, y)
            #if found: break

    elif user_input == 's':
        # get number of steps
        ii = input("Enter number of steps to run: ")
        try:
            steps = int(ii)
        except:
            print("Bad input: <{}>".format(ii))
            continue

        for ix in range(steps):
            x_ignore, y_ignore, direction = find_best_direction(x, y, mapp)
            x, y, out, found = attempt_move(direction, x, y)
            #if found: break

    elif user_input in "lr":
        wall = "left" if user_input=='l' else "right"
        # get number of steps
        ii = input("Hold the {} wall - for how many steps? : ".format(wall))
        try:
            steps = int(ii)
        except:
            print("Bad input: <{}>".format(ii))
            continue
        if True:
            facing = 1  # Start going North
            direction = 1  # Start going North

            for step in range(steps):
                # Keep trying to walk to the left; on failing rotate right and try again; until we manage a forward step
                out = 0

                while not out:
                    try_direction = rotate(direction, wall)
                    x, y, out, found = attempt_move(try_direction, x, y)

                    if not out:
                        # Rotate right
                        direction = rotate(direction, OTHER_WAY[wall])
                    else:
                        direction = try_direction


    elif user_input=='f':
        # Flood the map from the oxygen tank and see how long it takes to fill completely
        # global solution
        steps, minutes = flood(mapp, solution)
        draw_the_map(mapp)
        print("Shortest origin->oxygen is {} steps".format(steps))
        print("Flooded in {} minutes".format(minutes))
        exit()

    draw_the_map(mapp, dx=x, dy=y)


# Path to exit (on one line):
# 2 2 3 3 1 1 3 3 2 2 3 3 1 1 1 1 1 1 3 3 1 1 3 3 1 1 4 4 4 4 2 2 4 4 2 2 4 4 2 2 4 4 1 1 4 4 2 2 4 4 2 2 3 3 2 2 2 2 3 3 3 3 3 3 2 2 4 4 2 2 3 3 2 2 2 2 4 4 4 4 4 4 1 1 1 1 4 4 4 4 1 1 1 1 1 1 1 1 4 4 1 1 4 4 1 1 4 4 2 2 2 2 2 2 4 4 1 1 4 4 4 4 2 2 2 2 3 3 2 2 4 4 2 2 2 2 3 3 1 1 3 3 3 3 3 3 3 3 2 2 3 3 3 3 2 2 2 2 2 2 4 4 2 2 4 4 4 4 1 1 4 4 2 2 4 4 1 1 4 4 2 2 4 4 1 1 1 1 1 1 3 3 3 3 2 2 3 3 3 3 1 1 1 1 4 4 2 2
