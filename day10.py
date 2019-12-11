class AsteroidMap:
    def __init__ (self, map_str):
        self._best_location = None
        self._best_value = None
        self.height = None
        self.width = None

        self.the_map = {} # Map of (x,y) to <number visible>
        x=0; y=0
        for cc in map_str:
            if cc == "#":
                self.the_map[(x,y)] = 0

            if cc == "\n":
                if not self.width:
                    self.width = x

                y += 1
                x = 0
            else:
                x += 1

        self.height = y+1
        #print self.width, self.height

    def display (self):
        out = ""
        for y in range(self.height):
            for x in range(self.width):
                out += str(self.the_map.get((x,y), "."))

            out += '\n'

        # Remove the final newline
        out = out[:-1].strip()

        #print (out)
        #print
        return out

    def calculate_numbers (self):
        # For each asteroid
        # create a copy of the map (or a set of the keys?)
        # remove any that are shadowed from the set
        # find size of remaining set and save the value
        for asteroid in self.the_map.keys():
            visibles = set(self.the_map.keys())
            visibles.remove(asteroid)

            self.remove_shadowed(asteroid, visibles)

            self.the_map[asteroid] = len(visibles)

        # Now we've calculated everything, set the best values
        self._best_value = 0

        for location in self.the_map.items():
            if location[1] > self._best_value:
                self._best_location = location[0]
                self._best_value = location[1]

    def remove_shadowed(self, asteroid, visible_set):
        # Remove any asteroids from the visible set that are not visible to
        # this asteroid
        # Modifies the passed-in set
        for other_asteroid in self.the_map.keys():
            if asteroid == other_asteroid:
                continue   # Don't remove yourself!

            if other_asteroid not in visible_set:
                continue   # Don't bother counting shadows for something
                           # that's already in a shadow

            ox, oy = other_asteroid[0], other_asteroid[1]
            dx = ox - asteroid[0]
            dy = oy - asteroid[1]
            ldx, ldy = self.shrink_vector(dx, dy)

            x = ox + ldx
            y = oy + ldy

            while (0 <= x < self.width) and (0 <= y < self.height):
                if (x,y) in visible_set: visible_set.remove((x,y))

                x += ldx
                y += ldy

    def shrink_vector(self, x, y):
        # Reduce vecxtor to its minimal representation
        # e.g. (10,5) -> (2,1) or (-3,0) -> (-1,0)
        if y==0:
            return ((1 if x>0 else -1), 0)
        elif x==0:
            return (0, (1 if y>0 else -1))

        def gcd(a,b):
            while(b):
                a,b = b, a%b
            return a

        px = x if x>0 else -x
        py = y if y>0 else -y
        gd = gcd(px,py)
        return (x/gd, y/gd)

    def best_location (self):
        if self._best_location is None:
            self.calculate_numbers()

        return self._best_location

    def best_value (self):
        if self._best_value is None:
            self.calculate_numbers()

        return self._best_value



def tests ():
    # internal functions
    dummy = AsteroidMap("#..##")
    assert(dummy.shrink_vector(1,0) == (1,0))
    assert(dummy.shrink_vector(10,0) == (1,0))
    assert(dummy.shrink_vector(-5,0) == (-1,0))
    assert(dummy.shrink_vector(0,1) == (0,1))
    assert(dummy.shrink_vector(0,10) == (0,1))
    assert(dummy.shrink_vector(0,-5) == (0,-1))
    assert(dummy.shrink_vector(48,40) == (6,5))
    assert(dummy.shrink_vector(10,-5) == (2,-1))
    assert(dummy.shrink_vector(-6,2) == (-3,1))
    assert(dummy.shrink_vector(-24,-18) == (-4,-3))

    # Basic examples
    example=""".#..#
.....
#####
....#
...##"""

    my_map = AsteroidMap(example)

    assert(my_map.display() == """.0..0
.....
00000
....0
...00""")

    my_map.calculate_numbers()
    assert(my_map.display() == """.7..7
.....
67775
....7
...87""")

    assert(my_map.best_location() == (3,4))
    assert(my_map.best_value() == 8)

    # Larger example 1
    map_1 = AsteroidMap("""......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####""")

    assert(map_1.best_location() == (5,8))
    assert(map_1.best_value() == 33)

    # Larger example 2
    map_2 = AsteroidMap("""#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.""")

    assert(map_2.best_location() == (1,2))
    assert(map_2.best_value() == 35)

    # Larger example 3
    map_3 = AsteroidMap(""".#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..""")

    assert(map_3.best_location() == (6,3))
    assert(map_3.best_value() == 41)

    # Larger example 4
    map_4 = AsteroidMap(""".#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##""")

    assert(map_4.best_location() == (11,13))
    assert(map_4.best_value() == 210)

    input_data="""##.##..#.####...#.#.####
##.###..##.#######..##..
..######.###.#.##.######
.#######.####.##.#.###.#
..#...##.#.....#####..##
#..###.#...#..###.#..#..
###..#.##.####.#..##..##
.##.##....###.#..#....#.
########..#####..#######
##..#..##.#..##.#.#.#..#
##.#.##.######.#####....
###.##...#.##...#.######
###...##.####..##..#####
##.#...#.#.....######.##
.#...####..####.##...##.
#.#########..###..#.####
#.##..###.#.######.#####
##..##.##...####.#...##.
###...###.##.####.#.##..
####.#.....###..#.####.#
##.####..##.#.##..##.#.#
#####..#...####..##..#.#
.##.##.##...###.##...###
..###.########.#.###..#."""

    asteroids = AsteroidMap(input_data)
    assert(asteroids.best_location() == (14,17))
    assert(asteroids.best_value() == 260)

    print("All tests passed")

tests()

