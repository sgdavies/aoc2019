import logging, pdb, copy, sys
from day20_data import *

sys.setrecursionlimit(3000)
print(sys.getrecursionlimit())
# exit()

logging.basicConfig()
log = logging.getLogger("day20")

class Donut():
    def __init__(self, map_str, n_layers=30):
        self.network = Network()
        self.parse_map(map_str)

        self.build_layers(n_layers)
        log.info(self.network.show_graph())

    def parse_map(self, map_str):
        rows = [[c for c in row] for row in map_str.split('\n')]
        self.width = len(rows[0])
        self.height = len(rows)

        # Find and sort out all the portal locations.
        # These are written top down or LtR, and either aobve/below or left/right of a path ('.')
        # Find the portals, and relabel their locations (so [ ,A,B,.,.] becomes [ , ,AB,.,.])
        # We're going to end up with single node representing both ends of the portal, but we also
        # know that there's a cost of 1 for going through a portal. Hack that by putting the outside
        # end of the portal over the adjacent path:
        # (1) A........A' -> (2)  A.......A (single node 'A' drawn in 2 locations but is a single logical node)
        #     0123456789         0123456789
        # (1) Cost to go from 2->7 is 3 (2>1, 1>8, 8>7)
        # (2) Cost to go from 2->7 is still 3 (2>A, A>8, 8>7)
        node_locations = {}
        floor_map = {}
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if len(c) > 1:  # This is an already-relabelled node
                    continue

                if c.isalpha():  # Part of a node name
                    outside = (x==0 or x==len(row)-2 or y==0 or y==len(rows)-2)  # -2 because the label is 2 chars wide

                    if row[x+1].isalpha():
                        # "AB..." or "...CD" - we are at 'A' or 'C' (as we're scanning LtR)
                        #  01234      01234
                        # maps to
                        #  'AB'*.. or ..*'CD'
                        # 0 1  234    012 3  4
                        # where '*' is the last . on the path adjacent to the node
                        name = "{}{}".format(c, row[x+1])
                        if x>0 and row[x-1]=='.':
                            label_x, label_y = x, y
                            path_x, path_y = x-1, y
                            blank_x, blank_y = x+1, y
                        elif x < (len(row)-2) and row[x+2]=='.':
                            label_x, label_y = x+1, y
                            path_x, path_y = x+2, y
                            blank_x, blank_y = x, y
                        else:
                            pdb.set_trace()
                            assert(False), "Row calculations are wrong"
                    elif rows[y+1][x].isalpha():
                        # As above, but now top-to-bottom rather than left-to-right
                        name = "{}{}".format(c, rows[y+1][x])
                        if y>0 and rows[y-1][x]=='.':
                            label_x, label_y = x, y
                            path_x, path_y = x, y-1
                            blank_x, blank_y = x, y+1
                        elif y < (len(rows)-2) and rows[y+2][x]=='.':
                            label_x, label_y = x, y+1
                            path_x, path_y = x, y+2
                            blank_x, blank_y = x, y
                        else:
                            pdb.set_trace()
                            assert(False), "Column calculations are wrong"
                    else:
                        pdb.set_trace()
                        assert(False), "Node names must be length 2"

                    # Now do the relabelling
                    rows[blank_y][blank_x] = ' '

                    if outside:
                        # Put the node on the last path tile
                        node_x, node_y = path_x, path_y
                        rows[label_y][label_x] = ' '
                        name = '0o' + name
                    else:
                        node_x, node_y = label_x, label_y
                        name = '0i' + name

                    rows[node_y][node_x] = name
                    floor_map[(node_x, node_y)] = name

                    if name not in node_locations:
                        # Node doesn't exist yet
                        node_locations[name] = (node_x, node_y)
                    else:
                        # Node already exists
                        assert(False), "Inside/outside nodes are different, so this should be impossible"
                        node_locations[name].append((node_x, node_y))

                elif c=='.':
                    # piece of path. Not a shuffled node piece - because we're iterating top to bottom, left to right so that won't be '.' any more.
                    floor_map[(x,y)] = '.'

        log.info("\n"+map_str)
        log.debug(node_locations)

        # assert(all([len(v)==(1 if k in ['0AA','0ZZ'] else 2) for k,v in node_locations.items()]))
        self.node_locations = node_locations
        self.floor_map = floor_map

        self.explore_map()

        log.info(self.network.show_graph())
        # if not self.network.graph_is_connected():  # Part 2 - no longer expect graph to be connected
        #     pdb.set_trace()
        #     assert(self.network.graph_is_connected()), "Unconnected graph!"

    def explore_map(self):
        # Follow all paths through the map to build a network/graph view of the map.
        # Paths are disjointed, so attempt to search from every node that we know exists (self.node_locations).
        # Eat path dots as we go so we don't double-count any paths.
        # Add new nodes (for junctions) as and when we find them.
        # self.floor_map is a mapping of (x,y) coords to either '.' for path tiles, or '<name>' for named nodes.
        for node_name in self.node_locations:
            x,y = self.node_locations[node_name]
            node = self.network.node_from_name(node_name)
            if node is None:
                log.debug("Creating node " + node_name)
                node = Node(node_name)
                self.network.add_node(node)

            log.debug("Go into the map for {}, from ({}, {})".format(node.name, x,y))
            # pdb.set_trace()
            self.explore_from_node(node, x, y)

    def explore_from_node(self, node, x, y):
        log.debug("Explore from node {} ({}, {})".format(node, x, y))
        if (x,y) not in self.floor_map:
            log.debug("Already been here")
            return

        del self.floor_map[(x,y)]

        available_directions = self.neighbouring_paths(x,y)
        for new_x, new_y in available_directions:
            self.follow_edge(node, 1, new_x, new_y)

    def follow_edge(self, prev_node, distance, x, y):
        # 1. Check this route is still live - we may be iterating over an edge that has been covered from
        # another node in the meantime.
        # 2. Look at the label under the cursor. If it's a node name, add it as a node (if it doesn't already exist)
        # 3. Otherwise count routes out - if >1, add this as a node.
        # 4. Otherwise continue along the edge.
        # Handle dead ends (for this puzzle we'll just throw them away)
        tile = self.floor_map.get((x, y), None)
        if tile is None:
            # Node has already been covered
            log.debug("already traversed edge at {},{}".format(x,y))
            assert(distance==1)
            return

        available_directions = self.neighbouring_paths(x, y)

        node = None
        
        if len(tile) > 1:
            # It's a labelled portal node.
            node = self.network.node_from_name(tile)
            if node is None:
                log.debug("Create a new node " + tile)
                node = Node(tile)
                self.network.add_node(node)
        elif len(available_directions) > 1:
            # A junction in the map - create a node for it
            log.debug("Create a new node at {},{}".format(x,y))
            node = Node('0'+self.network.name(x,y))
            self.network.add_node(node)

        if node is not None:
            self.network.add_edge(prev_node, node, distance)
            self.explore_from_node(node, x, y)
        elif len(available_directions) == 0:
            # Dead end - nothing to do
            log.debug("Dead end at {},{}".format(x,y))
            return
        elif len(available_directions) == 1:
            # We're in the middle of an edge. Remove current point (so we don't backtrack) and continue exploring.
            del self.floor_map[(x, y)]
            assert(len(available_directions) == 1)  # There should've only been one option if we're in this branch
            next_x, next_y = available_directions[0]
            self.follow_edge(prev_node, distance+1, next_x, next_y)
        else:
            assert(False), "Impossible position for map exploration"

    def neighbouring_paths(self, x, y):
        possibles = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]

        return [loc for loc in possibles if loc in self.floor_map]

    def build_layers(self, n_layers=9):
        # Clone the map, update the numbering, then connect the upper-layer inner to the inner-layer outer
        layer_template = copy.deepcopy(self.network)

        for layer_ix in range(1, n_layers):
            current_layer = copy.deepcopy(layer_template)
            for node in current_layer.nodes:
                d, i, name_stem = int(node.name[0]), node.name[1], node.name[2:]
                new_name = "{}{}{}".format(layer_ix, i, name_stem)

                node.name = new_name

                self.network.add_node(node)

                if i=='o':
                    uppper_layer_node_name = "{}{}{}".format(layer_ix-1, 'i', name_stem)
                    uppper_layer_node = self.network.node_from_name(uppper_layer_node_name)
                    if uppper_layer_node is not None:
                        edge = Edge(node, uppper_layer_node, 0)  # zero-cost traversal

    def solve(self, start='0oAA', end='0oZZ'):
        start_node = self.network.node_from_name(start)
        end_node = self.network.node_from_name(end)
        assert(self.network.nodes_are_connected(start_node, end_node))

        return self.network.minimum_distance(start_node, end_node)


class Network():
    # A set of nodes connected by edges
    def __init__(self):
        self.nodes = set()
        self._node_name_to_node = {}

    def add_node(self, node):
        self.nodes.add(node)
        self._node_name_to_node[node.name] = node

    def add_edge(self, node_a, node_b, cost):
        edge = Edge(node_a, node_b, cost)

    def node_from_name(self, name):
        # returns None if the node doesn't exist
        return self._node_name_to_node.get(name, None)

    def minimum_distance(self, start, dest):
        # Calculate the shortest distance to get from A to B across the network
        # Let's get some Dijkstra up in here!
        # Set start node distance to 0.
        # visited nodes = empty set.
        # set tentative distance to all directly-reachable nodes from current.
        # mark current as visited
        # set new current = lowest tentative and continue
        visited = set()
        distances = {}
        distances[start] = 0, ""
        current_node = start

        while True:
            for edge in current_node.edges:
                next_node = edge.other_node(current_node)
                if (next_node in visited):
                    continue

                tentative_distance = distances[current_node][0] + edge.cost
                if (next_node not in distances) or (tentative_distance < distances[next_node][0]):
                    distances[next_node] = tentative_distance, distances[current_node][1] + "->" + current_node.name

            if current_node == dest:
                log.debug(distances[dest][1])
                return distances[dest][0]

            visited.add(current_node)
            current_node = sorted([node for node in distances.keys() if node not in visited], key=lambda k: distances[k][0]).pop(0)

    def graph_is_connected(self):
        # Returns true if all nodes can be reached from any node (i.e. no separate chunks)
        if len(self.nodes)==0: return True

        seen = set()
        self._explore_from_here(fun=lambda cur,next,acc: acc.add(cur), accumulator=seen)
        log.debug(seen)

        return len(seen)==len(self.nodes)

    def nodes_are_connected(self, start, end):
        acc=[False]
        def f(cur,next,acc):
            if next==end:
                acc[0] = True

        self._explore_from_here(start, accumulator=acc, fun=f)
        return acc[0]

    def show_graph(self):
        return "Graph:\n" + '\n'.join(["{}: {}".format(n.name, ','.join([e.other_node(n).name for e in n.edges])) for n in self.nodes])

    def _explore_from_here(self, current_node=None, visited=None, accumulator=None, fun=None):
        # Explore the rest of the graph down from here, returning once the only options are already-visited nodes
        # Optionally pass in 'fun' - a function that is passed the current & next nodes, and stores the result in 'accumulator'
        if current_node is None:
            current_node = next(iter(self.nodes))  # Just want to start somewhere

        if visited is None:
            visited = set()

        visited.add(current_node)
        for edge in current_node.edges:
            next_node = edge.other_node(current_node)
            if fun:
                fun(current_node, next_node, accumulator)

            if next_node in visited:
                continue
            else:
                self._explore_from_here(next_node, visited, accumulator, fun)

    @staticmethod
    def name(x, y):
        return "n{}.{}".format(x,y)


class Node():
    def __init__(self, name):
        self.name = name

        self.edges = set()  # Edges that connect to this node

    def add_edge(self, edge):
        self.edges.add(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def __str__(self):
        return "<node:{}>".format(self.name)

class Edge():
    # Edge is bi-directional.
    def __init__(self, node_a, node_b, cost):
        self.nodes = set([node_a, node_b])
        self.cost = cost
        node_a.add_edge(self)
        node_b.add_edge(self)

        self.other_nodes = {node_a: node_b, node_b: node_a}

    def other_node(self, node):
        # Return the node at the other end of this edge
        # assert(node in self.nodes)
        # return [n for n in self.nodes if n != node].pop()

        # speedup following profiling
        return self.other_nodes[node]

if __name__ == "__main__":
    def test_map(map_str):
        dungeon = Donut(map_str)
        distance = dungeon.solve()
        log.warning(distance)
        return distance

    def tests():
        assert(test_map(EXAMPLE_ONE) == 26)

        # assert(test_map(EXAMPLE_TWO) == 58)  # Impossible with part 2 rules

        assert(test_map(PART_TWO_EXAMPLE) == 396)

        test_map(PUZZLE_INPUT)

        log.critical("All tests passed")

    tests()