# Game of life!
import logging, pdb, copy

logging.basicConfig()
log = logging.getLogger()

class Eris():
    def __init__ (self, initial_state):
        self.step_count = 0

        rows = initial_state.split('\n')
        self.height = len(rows)
        self.width = len(rows[0])

        self.state=set()
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c=='#':
                    self.state.add((x,y))
        log.debug(initial_state)
        log.debug(self.state)

    def biodiversity_value(self):
        return sum([2**(x + self.width*y) for x, y in self.state])

    def step(self, number):
        for i in range(number):
            self._step()

    def _step(self):
        next = set()

        for y in range(self.height):
            for x in range(self.width):
                neighbours = self._neighbours(x,y)

                if (x,y) in self.state:
                    if neighbours==1:
                        next.add((x,y))
                else:
                    if neighbours==1 or neighbours==2:
                        next.add((x,y))

        self.state = next
        log.debug("New state:\n" + self.state_str())

    def _neighbours(self, x, y):
        # Count how many neighbours this square has
        return len([1 for a,b in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)] if (a,b) in self.state])

    def run_until_dupe(self):
        self.prev_states = set()
        self.prev_states.add(self.biodiversity_value())

        while True:
            self._step()
            bio = self.biodiversity_value()
            if bio in self.prev_states:
                return bio
            else:
                self.prev_states.add(bio)

    def state_str (self):
        out = []
        for y in range(self.height):
            x_str = ""
            for x in range(self.width):
                if (x,y) in self.state:
                    x_str += '#'
                else:
                    x_str += '.'
            out.append(x_str)

        return "\n".join(out)


def test(start, steps, end):
    eris = Eris(start)
    eris.step(steps)
    log.debug(eris.state_str())
    assert(end==eris.state_str())

test_input="""....#
#..#.
#..##
..#..
#...."""

puzzle_input=""".##.#
###..
#...#
##.#.
.###."""

def tests():
    #log.setLevel(logging.DEBUG)
    eris = Eris(""".....
.....
.....
#....
.#...""")
    assert(eris.biodiversity_value() == 2129920)

    test(test_input, 1, """#..#.
####.
###.#
##.##
.##..""")

    test(test_input, 2, """#####
....#
....#
...#.
#.###""")

    test(test_input, 3, """#....
####.
...##
#.##.
.##.#""")

    test(test_input, 4, """####.
....#
##..#
.....
##...""")

    eris = Eris(test_input)
    eris.run_until_dupe()
    log.debug(eris.step_count)
    log.debug(eris.biodiversity_value())
    assert(eris.state_str() == """.....
.....
.....
#....
.#...""")
    assert(eris.biodiversity_value() == 2129920)

    # Part one
    eris = Eris(puzzle_input)
    eris.run_until_dupe()
    log.debug(eris.step_count)
    log.debug(eris.biodiversity_value())
    #assert(eris.biodiversity_value() == 25719471)
    print(eris.biodiversity_value())

    log.critical("All tests passed")

if __name__ == "__main__":
    tests()
