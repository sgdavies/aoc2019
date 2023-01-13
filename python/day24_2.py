# Game of life!
# Part 2 - recursive space (so different code to part 1)
import logging, pdb, copy

logging.basicConfig()
log = logging.getLogger()

class Eris():
    def __init__ (self, initial_state):
        self.step_count = 0

        rows = initial_state.split('\n')
        self.height = len(rows)
        self.width = len(rows[0])
        log.debug(initial_state)

        self.layers = {}  # dict, keyed by layer number
        state=set()
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c=='#':
                    state.add((x,y))
        log.debug(state)
        self.layers[0] = state
        # self.get_layer(-1)
        # self.get_layer(1)

    # def get_layer(self, layer_number):
    #     if layer_number not in self.layers:
    #         # Create the new layer.  Check that we're adding it immediately above or beyond an existing one though.
    #         min_layer = min(self.layers.keys())
    #         max_layer = max(self.layers.keys())
    #         assert(layer_number==min_layer-1 or layer_number==max_layer+1), "New layer {} not adjacent ({}, {})".format(layer_number, min_layer, max_layer)

    #         new_layer = set()
    #         self.layers[layer_number] = new_layer

    #     return self.layers[layer_number]

    def biodiversity_value(self):
        assert(False), "update to account for layers"
        return sum([2**(x + self.width*y) for x, y in self.state])

    def biodiversity_value_for_state(self, state):
        return sum([2**(x + self.width*y) for x, y in state])

    def bug_count(self):
        return sum([len(layer) for layer in self.layers.values()])

    def step(self, number):
        for i in range(number):
            self._step()

    def _step(self):
        # if bottom layer is not empty - add layer below
        # if top layer is not empty - add layer above
        min_layer_number = min(self.layers.keys())
        if self.biodiversity_value_for_state(self.layers[min_layer_number]) > 0:
            self.layers[min_layer_number - 1] = set()

        max_layer_number = max(self.layers.keys())
        if self.biodiversity_value_for_state(self.layers[max_layer_number]) > 0:
            self.layers[max_layer_number + 1] = set()

        next_layers = {}

        for layer_number in self.layers.keys():
            next_layer = set()
            for y in range(self.height):
                for x in range(self.width):
                    if x==2 and y==2:
                        # magic central square - ignore
                        continue

                    neighbours = self._neighbours(layer_number, x, y)

                    if (x,y) in self.layers[layer_number]:
                        if neighbours==1:
                            next_layer.add((x,y))
                    else:
                        if neighbours==1 or neighbours==2:
                            next_layer.add((x,y))

            next_layers[layer_number] = next_layer
            log.debug("New state for layer {}:\n".format(layer_number) + self.state_str(next_layer))

        self.layers = next_layers

    def _neighbours(self, layer_number, x, y):
        # Count how many neighbours this square has.
        #   1  |  2  |    3    |  4  |  5  
        #      |     |         |     |     
        # -----+-----+---------+-----+-----
        #      |     |         |     |     
        #   6  |  7  |    8    |  9  |  10 
        #      |     |         |     |     
        # -----+-----+---------+-----+-----
        #      |     |A|B|C|D|E|     |     
        #      |     |-+-+-+-+-|     |     
        #      |     |F|G|H|I|J|     |     
        #      |     |-+-+-+-+-|     |     
        #  11  | 12  |K|L|?|N|O|  14 |  15 
        #      |     |-+-+-+-+-|     |     
        #      |     |P|Q|R|S|T|     |     
        #      |     |-+-+-+-+-|     |     
        #      |     |U|V|W|X|Y|     |     
        # -----+-----+---------+-----+-----
        #      |     |         |     |     
        #  16  | 17  |    18   |  19 |  20 
        #      |     |         |     |     
        # -----+-----+---------+-----+-----
        #      |     |         |     |     
        #  21  | 22  |    23   |  24 |  25 

        # 1. Find the neighbouring squares
        neighbours = set()  # Contains (layer, x, y) tuples

        # 1.1 Up/down a level
        if x==0:  # AFJPU -> 12
            neighbours.add((layer_number-1, 1, 2))
        elif x==4:  # EJOTY -> 14
            neighbours.add((layer_number-1, 3, 2))
        elif x==1 and y==2:  # 12 -> AFJPU
            for yy in range(5):
                neighbours.add((layer_number+1, 0, yy))
        elif x==3 and y==2:  # 14 -> EJOTY
            for yy in range(5):
                neighbours.add((layer_number+1, 4, yy))

        if y==0:  # ABCDE -> 8
            neighbours.add((layer_number-1, 2, 1))
        elif y==4:  # UVWXY -> 18
            neighbours.add((layer_number-1, 2, 3))
        elif x==2 and y==1:  # 8 -> ABCDE
            for xx in range(5):
                neighbours.add((layer_number+1, xx, 0))
        elif x==2 and y==3:  # 18 -> UVWXY
            for xx in range(5):
                neighbours.add((layer_number+1, xx, 4))

        # 1.2 All neighbours (includes off-grid & magic central square, but that's ok - they won't be in the set anyway)
        for xx,yy in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
            neighbours.add((layer_number, xx, yy))

        # 2. Return a count of how many of those are occupied.
        return len([1 for ll,xx,yy in neighbours if ll in self.layers and (xx,yy) in self.layers[ll]])

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

    def state_str (self, state):
        out = []
        for y in range(self.height):
            x_str = ""
            for x in range(self.width):
                if x==2 and y==2:
                    x_str += '?'
                elif (x,y) in state:
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
    assert(eris.biodiversity_value() == 25719471)

    log.critical("All tests passed")

if __name__ == "__main__":
    # tests()

    # Part two
    eris = Eris(puzzle_input)
    eris.step(200)
    print(eris.bug_count())
    # 1916
