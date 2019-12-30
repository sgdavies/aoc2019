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

        self.state=[]
        for row in rows:
            self.state.append([1 if c=='#' else 0 for c in row])
        log.debug(initial_state)
        log.debug(self.state)

    def biodiversity_value(self):
        total = 0
        linear = []
        for row in self.state: linear += row

        for i, val in enumerate(linear):
            if val:
                total += 2**i

        return total

    def step(self, number):
        for i in range(number):
            self._step()

    def _step(self):
        next = [[0]*self.width for x in range(self.height)]
        #next = copy.deepcopy(self.state)

        n_str=""
        for y in range(self.height):
            x_str=""
            for x in range(self.width):
                neighbours = self._neighbours(x,y)

                if self.state[y][x]:
                    if neighbours==1:
                        val = 1
                    else:
                        val = 0
                else:
                    if neighbours==1 or neighbours==2:
                        val = 1
                    else:
                        val = 0

                next[y][x] = val
                x_str += "{}".format(val)
            n_str += x_str + "\n"

        log.debug("Neighbours:\n" + n_str)
        self.state = next
        log.debug("New state:\n" + self.state_str())

    def _neighbours(self, x, y):
        # Count how many neighbours this square has
        ns = 0
        xys = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for tx, ty in xys:
            if (0 <= tx < self.width) and (0 <= ty < self.height):
                ns += self.state[ty][tx]

        log.debug("{},{}: {}".format(x, y, ns))
        return ns

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
        return "\n".join(["".join(['#' if x else '.' for x in row]) for row in self.state])


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

puzzle_input="""#.#..
.#.#.
#...#
.#..#
##.#."""

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
    assert(eris.biodiversity_value() == 25719471)

    log.critical("All tests passed")

if __name__ == "__main__":
    tests()
