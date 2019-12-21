example_1 = """#########
#b.A.@.a#
#########"""

UP=0
DOWN=1
LEFT=2
RIGHT=3

class Pacman():
    def __init__(self, map_str):
        self.map_str = map_str
        self.parse_map(map_str)

    def parse_map(self, map_str):
        # Read in the text.
        # Record locations of floor, doors, keys, and entrance.
        # Figure out nodes and build a graph view of the map.
        rows = map_str.split('\n')
        self.width = len(rows[0])
        self.height = len(rows)

        floor_map = {}
        doors = set()
        keys = set()

        # 0,0 is top left. x increases rightwards, y increases downwards
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c=='#':
                    # Wall - skip
                    continue
                else:
                    assert(('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c in '@.'))

                    floor_map[(x,y)] = c

                floor_map.add((x,y))  # TODO - replace with dict & char.  Then create door/key nodes while mapping later on.

                # if c=='@':
                #     self.entrance = (x,y)
                # elif 'a' <= c <= 'z':
                #     keys.add((x,y))
                # elif 'A' <= c <= 'Z':
                #     doors.add((x,y))
                # else:
                #     assert(c=='.')

        # Now build graph - find nodes & edges.
        # "Flood fill" from entrance?
        # nodes are all locations with 3+ routes in/out, plus all doors and keys.
        # Most doors & keys will only have 2 connected edges. They can possibly be removed from the graph once they've
        # been collected/ opened.

        self.floor_map = floor_map

        nodes = set()
        edges=set()
        x,y = self.entrance
        entrance_node = Node(x,y,"@")
        nodes.add(entrance_node)

        # First remove current location so we don't backtrack to it.
        del floor_map[(x,y)]
        self.explore_from_node(entrance_node)


    def explore_from_node(self, node):
        # node has already been removed from map.
        x, y = node.x, node.y
        available_directions = [loc for loc in self.neighbouring_squares(x,y) if loc in self.floor_map]
        for new_x, new_y in available_directions:
            self.follow_edge(node, 1, new_x, new_y)

    def follow_edge(self, prev_node, distance, x, y):
        # 1. Check this route is still live - we may be iterating over an edge that has been covered from
        # another node in the meantime.
        # 2. Look at the character under the cursor. If it's a door or key, add it as a node.
        # 3. Otherwise count routes out - if >1, add this as a node.
        # 4. Otherwise continue along the edge.
        # Handle dead ends (for this puzzle we'll just throw them away)
        tile = self.floor_map.get((x, y), None)
        if tile is None:
            # Node has already been covered
            assert(distance==1)
            return

        node = None

        if 'a' <= tile <= 'z':
            # Key
            node = Node(x, y, tile)
            self.keys.add(node)
        elif 'A' <= tile <= 'Z':
            # Key
            node = Node(x, y, tile)
            self.doors.add(node)

        available_directions = [loc for loc in self.neighbouring_squares(x, y) if loc in self.floor_map]
        if len(available_directions) > 1 and node is None:
            node = Node(x, y)

        # Remove current point and continue exploring
        del self.floor_map[(x, y)]

        if node is not None:
            self.nodes.add(node)
            self.add_edge(prev_node, node, distance)
            self.explore_from_node(node)
        elif len(available_directions) == 0:
            # Dead end - nothing to do
            return
        else:
            next_loc = available_directions[0]
            self.follow_edge(prev_node, distance+1, next_loc[0], next_loc[1])

    def neighbouring_squares(self, x, y):
        # TODO implement
        assert(False)


class Node():
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y

        self.outgoing_edges = set()  # Edges that connect to this node - outgoing edges only

    def add_edge(self, edge):
        self.outgoing_edges.add(edge)

    def remove_edge(self, edge):
        self.outgoing_edges.remove(edge)


# Door and Key are just special types of node
class Door(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        assert(len(self.name)==1)
        assert('A'<=self.name<='Z')

    def key_name(self):
        return chr(ord(self.name)^ord(' '))  # ASCII : bit-6 (0x20 = ' ') toggles upper/lower case

class Key(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        assert(len(self.name)==1)
        assert('a'<=self.name<='z')

    def door_name(self):
        return chr(ord(self.name)^ord(' '))  # ASCII : bit-6 (0x20 = ' ') toggles upper/lower case


class Edge():
    # Edge is one-directional.  Add 2 edges (one each way) for bidirectional link.
    def __init__(self, start_node, end_node, weight):
        self.start = start_node
        self.end = end_node
        self.length = weight

        self.start.add_edge(self)