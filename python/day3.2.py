import re,time

def closest_crossing (wire1, wire2):
    start = time.time()
    crossings = get_crossings(wire1, wire2)
    manhattens = map(lambda pos: abs(pos[0]) + abs(pos[1]), crossings)
    distances = [cross[2] for cross in crossings]

    print(crossings)
    print(distances)
    print("%3.2f\tclosest_crossing" %(time.time()-start))
    return sorted(manhattens)[0], sorted(distances)[0]

def get_crossings (wire1, wire2):
    t1 = time.time()
    minX = min(wire1.minx, wire2.minx)
    maxX = max(wire1.maxx, wire2.maxx)
    minY = min(wire1.miny, wire2.miny)
    maxY = max(wire1.maxy, wire2.maxy)

    width = maxX - minX +1   # +1 - allow for the origin
    height = maxY - minY +1

    originX = 0 -minX
    originY = 0 -minY

    print("Grid size:", width, height, "(%d..%d | %d..%d)" %(minX,maxX, minY,maxY), "origin [%d,%d]"%(originX, originY))

    t2 = time.time()

    grid = Grid(width, height, originX, originY)

    t3 = time.time()

    wire1.track(grid)
    wire2.track(grid)

    t4 = time.time()

    #grid.grid[originY][originX] = 'O'
    if max(width, height) < 20:
        grid.display()

    #common = wire1.key * wire2.key
    #for y in range(height):
    #    for x in range(width):
    #        if grid.grid[y][x] % common == 0:
    #            crossings.append( (x - grid.oX, y - grid.oY, grid.d_grid[y][x]) )

    now = time.time()
    print("%3.2f, %3.2f, %3.2f, %3.2f = %3.2f\tget_crossings" %(t2-t1, t3-t2, t4-t3, now-t4, now-t1))
    return grid.crossings

class Grid():
    def __init__ (self, width, height, oX=0, oY=0):
        t0 = time.time()
        self.grid = {} #[[1]*width for _ in range(height)]
        t1 = time.time()
        self.d_grid = {} #[[0]*width for _ in range(height)]  # distances
        t2 = time.time()
        self.oX = oX
        self.oY = oY
        self.crossings = []
        now = time.time()
        print("%3.2f, %3.2f, %3.2f = %3.2f\tGrid.__init__" %(t1-t0, t2-t1, now-t2, now-t0))

    def step (self, x, y, key, dist):
        #self.grid[y][x] *= key
        #self.d_grid[y][x] += dist
        self.grid[(x,y)] = self.grid.get( (x,y), 1 ) * key
        self.d_grid[(x,y)] = self.d_grid.get( (x,y), 0 ) + dist

        if self._other_prime_factor(self.grid[(x,y)], key):
            # Someone's been here before! Remember it. (Also - check distance
            # is a cross as well!)
            total_d = self.d_grid[(x,y)]
            #print x,y, self.grid[y][x], key, dist, total_d
            assert(total_d != dist)
            self.crossings.append( (x - self.oX, y - self.oY, total_d) )

    @staticmethod
    def _other_prime_factor (value, factor):
        # Determine if value has more prime factors than 'factor'
        test = value
        for x in range(1,10):
            test //= factor
            #print value, test, factor, x
            if test == 1:
                break
            elif test == 0:
                return True

        assert(x < 9) # don't go on forever...
        return not (factor**x == value)

    def display (self):
        #print "\n".join(["".join([str(x if x is not 1 else '.') for x in row]) for row in self.grid][::-1])
        #print
        #print "\n".join(["".join([str(x if x is not 1 else '.') for x in row]) for row in self.d_grid][::-1])
        #print
        pass


class Wire():
    KEYS = [2,3,5,7]
    keys = list(KEYS)
    instruction_re = re.compile("(?P<direction>[UDLR])(?P<len>\d+)")

    def __init__ (self, path_str):
        start = time.time()
        self.key = Wire._get_key()

        rpath = []
        for instr in path_str.split(','):
            m = self.instruction_re.match(instr)
            rpath.append( (m.group('direction'), int(m.group('len'))) )

        self.rpath = rpath
        self._find_extremes()

        self.d = 1 # Total distance tracked so far
        print("%3.2f\tWire.__init__" %(time.time()-start))

    @staticmethod
    def _get_key ():
        return Wire.keys.pop(0)

    @staticmethod
    def reset_keys ():
        Wire.keys = list(Wire.KEYS)

    def _find_extremes (self):
        start = time.time()
        minx = 0
        maxx = 0
        curx = 0

        miny = 0
        maxy = 0
        cury = 0

        for ins in self.rpath:
            if ins[0] == 'R':
                curx += ins[1]
                maxx = max(maxx, curx)
            elif ins[0] == 'L':
                curx -= ins[1]
                minx = min(minx, curx)
            elif ins[0] == 'U':
                cury += ins[1]
                maxy = max(maxy, cury)
            elif ins[0] == 'D':
                cury -= ins[1]
                miny = min(miny, cury)

            #print ins, minx,curx,maxx, "|", miny,cury,maxy

        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        print("%3.2f\tWire._find_extremes" %(time.time()-start))

    def track (self, grid):
        start = time.time()
        # Fill in positions in the grid tracked by this wire
        x = grid.oX
        y = grid.oY

        # Don't fill in the starting location (0,0)
        for instr in self.rpath:
            x, y = self._track_instruction(instr, grid, x, y)

        print("%3.2f\tWire.track" %(time.time()-start))

    def _track_instruction (self, instr, grid, x, y):
        # Fill out positions covered by this instruction, starting from x,y
        # Return new x, y positions
        direction = instr[0]
        distance = instr[1]
        nextX, nextY = x, y

        for _ in range(distance):
            nextX, nextY = self.move(nextX, nextY, direction)

            grid.step(nextX, nextY, self.key, self.d)

            self.d += 1
            #grid.display()

        return nextX, nextY

    def move (self, x, y, direction):
        if direction == 'R':
            return x+1, y
        elif direction == 'L':
            return x-1, y
        elif direction == 'U':
            return x, y+1
        elif direction == 'D':
            return x, y-1
        else:
            print("Invalid direction:", direction)
            exit(1)


def test (wire1_string, wire2_string, em=None, ed=None):
    print()

    print(wire1_string)
    print(wire2_string)
    wire1 = Wire(wire1_string)
    wire2 = Wire(wire2_string)

    m,d = closest_crossing(wire1, wire2)
    if em is not None: assert(m == em)
    if ed is not None: assert(d == ed)

    Wire.reset_keys()

def tests ():
    # Example 1
    test("R8,U5,L5,D3", "U7,R6,D4,L4", em=6, ed=30)

    # Test negative numbers
    test("L2,U2,R5", "D3,L1,U7,R2,D6", em=1)

    # Example 2
    test("R75,D30,R83,U83,L12,D49,R71,U7,L72", "U62,R66,U55,R34,D71,R55,D58,R83", em=159, ed=610)

    # Example 3
    test("R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
         "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7",
         em=135, ed=410)

    print("All tests passed\n")

tests()

wire1 = Wire("R991,U77,L916,D26,R424,D739,L558,D439,R636,U616,L364,D653,R546,U909,L66,D472,R341,U906,L37,D360,L369,D451,L649,D521,R2,U491,R409,U801,R23,U323,L209,U171,L849,D891,L854,U224,R476,D519,L937,U345,R722,D785,L312,D949,R124,U20,R677,D236,R820,D320,L549,D631,R42,U621,R760,U958,L925,U84,R914,U656,R598,D610,R397,D753,L109,U988,R435,U828,R219,U583,L317,D520,L940,D850,R594,D801,L422,U292,R883,U204,L76,U860,L753,U483,L183,U179,R441,U163,L859,U437,L485,D239,R454,D940,R689,D704,R110,D12,R370,D413,L192,D979,R990,D651,L308,U177,R787,D717,R245,U689,R11,D509,L680,U228,L347,D179,R508,D40,L502,U689,L643,U45,R884,D653,L23,D918,L825,D312,L691,U292,L285,D183,R997,U427,L89,U252,R475,U217,R16,U749,L578,D931,L273,U509,L741,U97,R407,U275,L605,U136,L558,U318,R478,U505,R446,U295,R562,D646,R988,D254,L68,U645,L953,U916,L442,D713,R978,U540,R447,U594,L804,U215,R95,D995,R818,D237,R212,U664,R455,D684,L338,U308,R463,D985,L988,D281,R758,U510,L232,U509,R289,D90,R65,D46,R886,D741,L327,U755,R236,U870,L764,U60,R391,U91,R367,U587,L651,D434,L47,U954,R707,D336,L242,D387,L410,D19,R203,D703,L228,U292,L19,U916,R411,U421,L726,U543,L240,U755,R157,U836,L397,U71,L125,D934,L723,D145,L317,D229,R863,U941,L926,D55,L2,D452,R895,D670,L216,U504,R66,U696,L581,U75,L235,U88,L609,U415,L850,U21,L109,U416,R408,D367,R823,D199,L718,U136,L860,U780,L308,D312,R230,D671,R477,D672,L94,U307,R301,D143,L300,D792,L593,D399,R840,D225,R680,D484,L646,D917,R132,D213,L779,D143,L176,U673,L772,D93,L10,D624,L244,D993,R346")
wire2 = Wire("L997,U989,L596,U821,L419,U118,R258,D239,R902,D810,R553,D271,R213,D787,R723,D57,L874,D556,R53,U317,L196,D813,R500,U151,R180,D293,L415,U493,L99,U482,R517,U649,R102,U860,R905,D499,R133,D741,R394,U737,L903,U800,R755,D376,L11,U751,R539,U33,R539,U30,L534,D631,L714,U190,L446,U409,R977,D731,R282,U244,R29,D212,L523,D570,L89,D327,R178,U970,R435,U250,R213,D604,R64,D348,R315,D994,L508,D261,R62,D50,L347,U183,R410,D627,L128,U855,L803,D695,L879,U857,L629,D145,L341,D733,L566,D626,L302,U236,L55,U428,R183,U254,R226,D228,R616,U137,L593,U204,R620,U624,R605,D705,L263,D568,R931,D464,R989,U621,L277,U274,L137,U768,L261,D360,L45,D110,R35,U212,L271,D318,L444,D427,R225,D380,L907,D193,L118,U741,L101,D298,R604,D598,L98,U458,L733,U511,L82,D173,L644,U803,R926,D610,R24,D170,L198,U766,R656,D474,L393,D934,L789,U92,L889,U460,L232,U193,L877,D380,L455,D526,R899,D696,R452,U95,L828,D720,R370,U664,L792,D204,R84,D749,R808,U132,L152,D375,R19,U164,L615,D121,R644,D289,R381,U126,L304,U508,L112,D268,L572,D838,L998,U127,R500,D344,R694,U451,L846,D565,R158,U47,L430,U214,R571,D983,R690,D227,L107,U109,L286,D66,L544,U205,L453,U716,L36,U672,L517,U878,L487,U936,L628,U253,R424,D409,R422,U636,R412,U553,R59,D332,R7,U495,L305,D939,L428,D821,R749,D195,R531,D898,R337,D303,L398,D625,R57,D503,L699,D553,L478,U716,R897,D3,R420,U903,R994,U864,L745,U205,R229,U126,L227,D454,R670,U605,L356,U499,R510,U238,L542,D440,R156,D512,L237,D341,L439,U642,R873,D650,R871,D616,R322,U696,R248,D746,R990,U829,R812,U294,L462,U740,R780")

print(closest_crossing(wire1, wire2))

