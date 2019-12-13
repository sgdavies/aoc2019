import itertools
import re
import operator

DEBUG=0  # 0=none, 1=info, 2=debug

class World:
    def __init__ (self, initial_positions):
        self.moons = []
        self.step_number = 0
        for line in initial_positions.split('\n'):
            self.moons.append(Moon(line))

        self.previous_worlds = {}
        self.previous_energies = []

        if DEBUG: self.print_world()

    def step (self):
        key = self._prev_world_key()
        self.previous_worlds[key] = self.step_number

        # For all pairs of moons, calculate velocity adjustments
        for a,b in itertools.combinations(self.moons, 2):
            for axis in range(3): # 0=x, 1=y, 2=z
                if a.pos[axis] > b.pos[axis]:
                    a.vel[axis] -= 1
                    b.vel[axis] += 1
                elif a.pos[axis] < b.pos[axis]:
                    a.vel[axis] += 1
                    b.vel[axis] -= 1

        for moon in self.moons:
            moon.move()

        self.step_number += 1

        self.previous_energies.append(self.total_energy())

        key = self._prev_world_key()
        if DEBUG and self.step_number < 5:
            print "\tKey:", self.step_number, key
            print self.previous_worlds.keys()
            self.print_world()

        if key in self.previous_worlds:
            if DEBUG: print "Last key:", self.step_number, key
            return self.previous_worlds[key]
        else:
            return None

    def total_energy (self):
        return sum([moon.tot() for moon in self.moons])

    def print_world (self):
        out = "After {} steps:".format(self.step_number)
        if DEBUG > 1:
            for moon in self.moons:
                out += "\n" + str(moon)
            out += "\n"

        out += "Total energy: {}".format(self.total_energy())
        print out

    def _prev_world_key(self):
        #return ", ".join([moon.short_str() for moon in self.moons])
        return tuple([(tuple(moon.pos), tuple(moon.vel)) for moon in self.moons])

class Moon:
    initial_re = re.compile(r"<x=(?P<x>[-]?\d+),\s*y=(?P<y>[-]?\d+),\s*z=(?P<z>[-]?\d+)>")

    def __init__ (self, initial_positions):
        # Initial_positions is a string like <x=2, y=-10, z=-7>
        match = Moon.initial_re.match(initial_positions)
        if not match:
            print "Didn't recognise input:", initial_positions

        self.pos = [int(match.group('x')), int(match.group('y')), int(match.group('z'))]
        self.vel = [0,0,0]

    def move (self):
        for axis in range(len(self.pos)):
            self.pos[axis] += self.vel[axis]

    def _pot (self):
        return sum([abs(x) for x in self.pos])

    def _kin (self):
        return sum([abs(x) for x in self.vel])

    def tot (self):
        return self._pot() * self._kin()

    def short_str (self):
        return "[{} {} {}|{} {} {}]".format(self.pos[0],self.pos[1],self.pos[2],self.vel[0],self.vel[1],self.vel[2])

    def __str__ (self):
        out = "pos=<x={}, y={}, z={}>, vel=<x={}, y={}, z={}>.".format(self.pos[0],self.pos[1],self.pos[2],self.vel[0],self.vel[1],self.vel[2])
        if DEBUG: out += "  pot={}; kin={}; tot={}".format(self._pot(), self._kin(), self.tot())
        return out


def tests():
    example_input = """<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>"""

    world = World(example_input)
    for ix in range(10): world.step()
    assert(world.total_energy() == 179)

    example_input = """<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>"""

    world = World(example_input)
    for ix in range(100): world.step()
    assert(world.total_energy() == 1940)

    real_input = """<x=1, y=2, z=-9>
<x=-1, y=-9, z=-4>
<x=17, y=6, z=8>
<x=12, y=4, z=2>"""

    world = World(real_input)
    for ix in range(1000): world.step()
    assert(world.total_energy() == 7471)

    print "All tests passed"

tests()


# Part Two

example_one_input = """<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>"""

world = World(example_one_input)
while world.step() is None:
    pass

if DEBUG: print "Done after {} iterations".format(world.step_number)
assert(world.step_number == 2772)

# Conclusion: each axis-position loops after a small number of steps (<100)
# if position loops - that axis-velocity must loop at the same rate (so ignore it)
# Method then:
# - run world for 2xMinLoop
# - for each moon
#   - for each axis, find loop size
#   - find rcd (or minproduct?- something) that is that moon's whole loop
# - find rcd-thingy for all 4 planet's loops (or is it just the same? probably,
#   or the other planet's axes wouldn't loop at the same rate)
MAX_LOOP_LENGTH = 100
import time
def find_loop_length (initial_state):
    start = time.time()
    world = World(initial_state)

    for ix in xrange(2*MAX_LOOP_LENGTH):
        world.step()

    # One tuple per moon.
    # Each tuple contains one array per axis
    moons = [([],[],[]),
             ([],[],[]),
             ([],[],[]),
             ([],[],[])]
    for k,v in sorted(world.previous_worlds.items(), key=lambda item: item[1]):
        # k is the key: 4-tuple of moons, and each moon is a 2-tuple of (pos),(vel)
        for moonx in range(4):
            moon = moons[moonx]
            for axis in range(3):
              try:
                moon[axis].append(k[moonx][0][axis])
              except:
                print k
                print moonx
                print axis
                raise

    axis_loops=[0,0,0]
    for axis in range(3):
        longest = 0
        for moonx, moon in enumerate(moons):
            #print "Moon {}: x {}={}, y {}={}, z {}={}".format(moonx+1, min(moon[0]), max(moon[0]), min(moon[1]), max(moon[1]), min(moon[2]), max(moon[2]))
            #print "x:", moon[0]
            for ix in xrange(1, MAX_LOOP_LENGTH+1):
                success = True
                for jx in xrange(ix):
                    if moon[axis][jx] != moon[axis][jx + ix]:
                        success = False
                        break

                if success:
                    if ix > longest:
                        longest = ix
                    break

        axis_loops[axis] = longest

    if any([x==0 for x in axis_loops]):
        print "Failed to find a loop (searched up to {})!".format(MAX_LOOP_LENGTH)
        print axis_loops

    if DEBUG or True:
        print axis_loops
        print axis_loops[0]*axis_loops[1]*axis_loops[2]
        import sys;sys.stdout.flush()

    # lowest common multiple
    def lcm (numbers):
        #return reduce(lambda x,y: (lambda a,b: next(i for i in xrange(max(a,b),a*b+1) if i%a==0 and i%b==0))(x,y), numbers)
        def gcd (numbers):
            from fractions import gcd
            return reduce(gcd, numbers)

        def llcm (a,b):
            return (a*b) // gcd([a,b])

        return reduce(llcm, numbers, 1)

    answer = lcm(axis_loops)
    print "Found answer {} in {:.1f} seconds".format(answer, time.time()-start)
    return answer

example_one_loop = find_loop_length(example_one_input)
print example_one_loop
assert(example_one_loop == 2772)

MAX_LOOP_LENGTH = 7000
example_two_input="""<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>"""
example_two_loop = find_loop_length(example_two_input)
print "Answer:", example_two_loop
assert(example_two_loop == 4686774924)

puzzle_part_two_input="""<x=1, y=2, z=-9>
<x=-1, y=-9, z=-4>
<x=17, y=6, z=8>
<x=12, y=4, z=2>"""

MAX_LOOP_LENGTH = 200000
length = find_loop_length(puzzle_part_two_input)
print "Answer:", length
