DEBUG=False
import copy, random

class Dungeon():
    def __init__(self, map_str):
        self.map_str = map_str
        self.parse_map(map_str)
        self.create_tree()  # All the examples & puzzle are trees, not looping graphs.

    def parse_map(self, map_str):
        # Read in the text.
        # Record locations of floor, doors, keys, and entrance.
        # Figure out nodes and build a graph view of the map.
        rows = map_str.split('\n')
        self.width = len(rows[0])
        self.height = len(rows)

        floor_map = {}

        # 0,0 is top left. x increases rightwards, y increases downwards
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c=='#':
                    # Wall - skip
                    continue
                else:
                    assert(('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c in '@.'))
                    floor_map[(x,y)] = c
                    if c=='@':
                        self.entrance = x,y

        # Now build graph - find nodes & edges.
        # "Flood fill" from entrance.
        # Nodes are all locations with 3+ routes in/out, plus all doors and keys.
        # Most doors & keys will only have 2 connected edges. They can possibly be removed from the graph once they've
        # been collected/ opened.

        self.floor_map = floor_map
        self.doors = set()
        self.keys = set()
        self.nodes = set()

        self.node_names_to_node = {}

        x,y = self.entrance
        entrance_node = Node(x, y, "@")
        self.add_node(entrance_node)

        self.explore_from_node(entrance_node)

    def create_tree(self):
        # Having parsed the map ad built a graph, now instead create a tree version of the graph.
        # If the graph is not a tree, assert.
        # We have: self.nodes (all the nodes, including connecting edges); self.entrance (x,y coords of the root)
        # as well as self.find_node('@') (the root node).
        # We want to build a set of TreeNodes starting at the root. Each TreeNode has a parent (None for the root),
        # a list of children, and a cost (distance to parent). Also a name.
        # For each node in our graph, create a mirror tree node for it and add it to the tree.
        # Check that no node is added twice - if it is, this isn't a tree after all.
        nodes_visited = set()
        edges_used = set()
        root = self.find_node('@')
        nodes_visited.add(root)
        self.tree = TreeNode(None, 0, root.x, root.y, name=root.name)
        self.create_child_nodes(root, self.tree, nodes_visited, edges_used)

    def create_child_nodes(self, node, tree_node, nodes_visited, edges_used):
        # Add the children of this node, recursively
        # 'node' is the regular-graph node that we're copying from.
        # 'tree_node' is the node in the tree we're adding to.
        # 'nodes_visited' is a list of regular nodes that have already been added.
        # If we're trying to add the same node twice then there's a loop and this is not a tree. Assert.
        # 'edges_used' is a list of edges we've already traversed - need because otherwise an added node
        # will try to add its parent unless we skip edges already used.
        for edge in node.edges:
            if edge in edges_used:
                # We've already gone this way - skip
                continue
            else:
                edges_used.add(edge)

            child_node = edge.other_node(node)
            if child_node in nodes_visited:
                print("Graph has a loop?", child_node.name)
                import pdb; pdb.set_trace()
                assert(False)
            else:
                nodes_visited.add(child_node)

            if isinstance(child_node, Door):
                child_tree_node = TreeDoor(tree_node, edge.weight, child_node.x, child_node.y, child_node.name)
            elif isinstance(child_node, Key):
                child_tree_node = TreeKey(tree_node, edge.weight, child_node.x, child_node.y, child_node.name)
            else:
                child_tree_node = TreeNode(tree_node, edge.weight, child_node.x, child_node.y)

            self.create_child_nodes(child_node, child_tree_node, nodes_visited, edges_used)

    def add_node(self, node):
        self.nodes.add(node)
        self.node_names_to_node[node.name] = node

    def del_node(self, node):
        self.nodes.remove(node)
        del self.node_names_to_node[node.name]

    def explore_from_node(self, node):
        x, y = node.x, node.y

        # First remove current location so we don't backtrack to it.
        del self.floor_map[(x,y)]

        available_directions = self.neighbouring_paths(x,y)
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
            node = Key(x, y, tile)
            self.keys.add(node)
        elif 'A' <= tile <= 'Z':
            node = Door(x, y, tile)
            self.doors.add(node)

        available_directions = self.neighbouring_paths(x, y)

        if (len(available_directions) > 1) or (node is not None):
            # Either a door or key (where we've just made the node), or it's a real node - create it.
            if node is None:
                node = Node(x, y)
            self.add_node(node)
            self.add_edge(prev_node, node, distance)
            self.explore_from_node(node)
        elif len(available_directions) == 0:
            # Dead end - nothing to do
            return
        elif len(available_directions) == 1:
            # We're in the middle of an edge. Remove current point (so we don't backtrack) and continue exploring.
            del self.floor_map[(x, y)]
            next_loc = available_directions.pop()
            assert(len(available_directions) == 0)  # There should've only been one option if we're in this branch
            self.follow_edge(prev_node, distance+1, next_loc[0], next_loc[1])
        else:
            assert(False)

    def neighbouring_paths(self, x, y):
        possibles = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]

        return [loc for loc in possibles if loc in self.floor_map]

    def add_edge(self, node_a, node_b, distance):
        edge = Edge(node_a, node_b, distance)

    def remove_node(self, node_to_remove, node_is_door=False):
        # Remove this node from the graph.  If it's a door, then we may need to replace it with another regular node.
        # Otherwise join the 2 edges together.
        number_of_edges = len(node_to_remove.edges)
        if number_of_edges > 2:
            assert(node_is_door)  # Can't cut out a node if it's a connector node
            # Replace the door with a regular node.
            self.replace_node(node_to_remove)
        elif number_of_edges == 2:
            # Remove this node and join the two cut edges together
            edge_a, edge_b = node_to_remove.edges
            node_a = edge_a.other_node(node_to_remove)
            node_b = edge_b.other_node(node_to_remove)
            new_edge = Edge(node_a, node_b, edge_a.weight + edge_b.weight)
            for node, edge in zip([node_a, node_b], [edge_a, edge_b]):
                node.add_edge(new_edge)
                node.remove_edge(edge)

            self.del_node(node_to_remove)
        else:
            # This node is a dead end.  We need to replace rather than remove it (we
            # don't want to leave a key, and we dont' want to cut out a node that 
            # pacman is currently sitting on)
            self.replace_node(node_to_remove)

    def replace_node(self, node_to_replace):
        x, y = node_to_replace.x, node_to_replace.y
        new_node = Node(x, y)
        for old_edge in list(node_to_replace.edges):
            other_node = old_edge.other_node(node_to_replace)
            new_edge = Edge(other_node, new_node, old_edge.weight)
            new_node.add_edge(new_edge)
            other_node.add_edge(new_edge)
            other_node.remove_edge(old_edge)

        self.add_node(new_node)
        self.del_node(node_to_replace)

    def find_node(self, name):
        # return the node with this name. Returns None if the door can't be found.
        # nodes = [node for node in self.nodes if node.name==name]

        # if len(nodes) == 0:
        #     return None

        # assert(len(nodes)==1)
        # return nodes[0]
        return self.node_names_to_node.get(name, None)

    def visible_doors(self, from_node):
        # Return a list of door-nodes visible from this node.
        # 'Visible' means not hidden behind a door - i.e. treat each door as a dead-end.
        return [node for node in self.visible_nodes(from_node) if isinstance(node, Door)]

    def visible_keys(self, from_node, stop_on_keys=False):
        # Return a list of key-nodes visible from this node.
        # 'Visible' means not hidden behind a door.
        return [node for node in self.visible_nodes(from_node, stop_on_keys=stop_on_keys) if isinstance(node, Key)]
    
    def visible_nodes(self, from_node, used_edges=None, visited_nodes=None, stop_on_keys=False):
        # Return a list of all nodes visible from this node.
        # 'Visible' means not hidden behind a door.
        # Current node is *not* returned.
        if used_edges is None:
            used_edges = set()

        if visited_nodes is None:
            visited_nodes = set()

        visited_nodes.add(from_node)

        visible_nodes = set()
        for edge in from_node.edges:
            if edge in used_edges:
                continue

            used_edges.add(edge)
            next_node = edge.other_node(from_node)

            if next_node in visited_nodes:
                # We've already dealt with that one
                continue

            visible_nodes.add(next_node)

            if isinstance(next_node, Door):
                continue
            elif stop_on_keys and isinstance(next_node, Key):
                continue
            else:
                visible_nodes.update(self.visible_nodes(next_node, used_edges=used_edges, visited_nodes=visited_nodes, stop_on_keys=stop_on_keys))

        return visible_nodes

    def minimum_distance(self, start, dest, treat_doors_as_blocked=True):
        # Calculate the shortest distance to get from A to B across the network
        # Let's get some Dijkstra up in here!
        # Set start node distance to 0.
        # visited nodes = empty set.
        # set tentative distance to all directly-reachable nodes from current.
        # mark current as visited
        # set new current = lowest tentative and continue
        visited = set()
        distances = {}
        distances[start] = 0
        current_node = start

        while True:
            for edge in current_node.edges:
                next_node = edge.other_node(current_node)
                if (next_node in visited) or (isinstance(next_node, Door) and treat_doors_as_blocked):
                    # Don't go that way.
                    continue

                tentative_distance = distances[current_node] + edge.weight
                if (next_node not in distances) or (tentative_distance < distances[next_node]):
                    distances[next_node] = tentative_distance

            if current_node == dest:
                return distances[dest]

            visited.add(current_node)
            current_node = sorted([node for node in distances.keys() if node not in visited], key=lambda k: distances[k]).pop(0)


class Node():
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y

        if name is None:
            self.name = "N{}.{}".format(x,y)
        else:
            self.name = name

        self.edges = set()  # Edges that connect to this node

    def add_edge(self, edge):
        self.edges.add(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)


# Door and Key are just special types of node
class Door(Node):
    def __init__(self, x, y, name):
        super().__init__(x, y, name=name)
        assert(len(self.name)==1)
        assert('A'<=self.name<='Z')

    def key_name(self):
        return chr(ord(self.name)^ord(' '))  # ASCII : bit-6 (0x20 = ' ') toggles upper/lower case

class Key(Node):
    def __init__(self, x, y, name):
        super().__init__(x, y, name=name)
        assert(len(self.name)==1)
        assert('a'<=self.name<='z')

    def door_name(self):
        return chr(ord(self.name)^ord(' '))  # ASCII : bit-6 (0x20 = ' ') toggles upper/lower case


class Edge():
    # Edge is bi-directional.
    def __init__(self, node_a, node_b, weight):
        self.nodes = set([node_a, node_b])
        self.weight = weight
        node_a.add_edge(self)
        node_b.add_edge(self)

        self.other_nodes = {node_a: node_b, node_b: node_a}

    def other_node(self, node):
        # Return the node at the other end of this edge
        # assert(node in self.nodes)
        # return [n for n in self.nodes if n != node].pop()

        # speedup following profiling
        return self.other_nodes[node]


class TreeNode():
    # A node in a tree.
    def __init__(self, parent, cost, x, y, name=None, children=None):
        self.parent = parent  # None if this is the root
        self.cost = cost  # Distance to parent
        self.x = x
        self.y = y

        self.name = name if name else "T{}.{}".format(x,y)
        self.children = children if children else []


class TreeDoor(TreeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert(len(self.name)==1)
        assert('A'<=self.name<='Z')

    def key_name(self):
        return chr(ord(self.name)^ord(' '))  # ASCII : bit-6 (0x20 = ' ') toggles upper/lower case


class TreeKey(TreeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert(len(self.name)==1)
        assert('a'<=self.name<='z')

    def door_name(self):
        return chr(ord(self.name)^ord(' '))  # ASCII : bit-6 (0x20 = ' ') toggles upper/lower case


# Main functions #
def create_dungeon(mapp):
    return Dungeon(mapp)

def solve_the_dungeon(dungeon, quiet=False):
    pacman_is_at = dungeon.find_node('@')
    remaining_keys = set(dungeon.keys)
    distance_travelled = 0
    choices = 1

    # Would be good to modify this to not affect the underlying graph - then it would be faster to do repeats
    try:
        while remaining_keys:
            # visible_doors = dungeon.visible_doors(pacman_is_at)
            visible_keys = dungeon.visible_keys(pacman_is_at, stop_on_keys=True)  # Not necessarily correct - perhaps we shouldn't show keys that are hidden behind outher keys (since we must pick up the first key on the way to the second)
            if DEBUG: print([x.name for x in visible_doors+visible_keys])
            choices *= len(visible_keys)

            # Pick up a key, then 'open' the relevant door - i.e. remove that door node.
            next_key = random.choice(visible_keys)
            distance_travelled += dungeon.minimum_distance(pacman_is_at, next_key)
            pacman_is_at = next_key
            newly_opened_door = dungeon.find_node(next_key.door_name())
            if DEBUG: print("Travelled: {}, key: {}, door: {}".format(distance_travelled, next_key.name, newly_opened_door.name if newly_opened_door else 'none'))
            if newly_opened_door is not None:  # Some keys have no corresponding door
                dungeon.remove_node(newly_opened_door)
            # Once we've collected a key, remove it from the dungeon
            remaining_keys.remove(next_key)
            dungeon.replace_node(next_key)
    except:
        import traceback
        print(traceback.format_exc())
        import pdb; pdb.set_trace()
        raise

    if not quiet: print("Had {} choices; picked a route of length {}".format(choices, distance_travelled))
    return distance_travelled


def solve_dungeon(mapp, quiet=True, repeats=1):
    lowest_distance = None
    for repeat in range(repeats):
        # test_dungeon = copy.deepcopy(dungeon)  # Slower than create_dungeon()
        dungeon = create_dungeon(mapp)
        distance = solve_the_dungeon(dungeon, quiet=quiet)

        if lowest_distance is None or distance < lowest_distance:
            lowest_distance = distance

    return lowest_distance

# Best is 8
example_1 = """#########
#b.A.@.a#
#########"""
print(solve_dungeon(example_1, repeats=10), "vs", 8)

# Best is 86
example_2="""########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################"""
print(solve_dungeon(example_2, repeats=10), "vs", 86)

# Best is 132
example_3 = """########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################"""
print(solve_dungeon(example_3, repeats=10), "vs", 132)

# Best is 136
example_4 = """#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################"""
print(solve_dungeon(example_4, repeats=10), "vs", 136)

# Best is 81
example_5 = """########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################"""
print(solve_dungeon(example_5, repeats=10), "vs", 81)

# Part 1 puzzle
puzzle = """#################################################################################
#.............#.#..g..........#t........#...#...................#.....#.....#...#
#W#########.#.#.#.#########.#.#.#####.###.#.#############.#####.###.#.#.#.#.###.#
#.#...#.....#...#.#...#...#.#.#.#...#...#.#.#....s..#..o#...#.#...#.#...#.#.#...#
#.###.#.#######.#.###.#.#.#.###.#.#.#.#.#.#.#.#####.#.#.#.#.#.###.###.###.#.#.###
#.....#.#.....#.#.#...#.#.#.....#.#.#.#.#.#...#...#.#.#.#.#.#...#...#...#.#.#...#
###.###.#.#.###.#.#.###.#.#######.#I###.#.#####.#.#.#.#.###.###.###.#.###.#.###.#
#.#.#...#.#.....#.#.#...#.....#...#.....#n..#...#.#...#...#.#...#.#.#.#...#...#.#
#.#.#.#####.#####.#.#.#####.###.###########.#.###########.#.#.#.#.#X###.#####.#.#
#.#.#x..Y.#.....#.#...#.....#...#.......#...#.#.............#.#...#.....#...#...#
#.#.#####.#######.#.###.#.###.###.#####.#.###.#.#############.###########.#.###.#
#...#...#.....#...#...#.#.#.E.#......j#.#.#...#.#.#.K.......#.#.....#.....#...#.#
#.###.#.#####.#.#######.###.#.#.#######.#.###.#.#.#.#######.#.#.#.#.#.###.#####.#
#.#...#.#.....#.#.....#.#...#.#.#.#.....#...#.....#.#b..#...#...#.#...#.#.#.....#
#.#.#.###.###.#.#.###.#.#.#####V#.#.#####.#.#######.#.#.#.###.###.#####.#Z#.#####
#.#.#.#...#.#.#...#...#.#.........#.....#.#...........#.#...#.#.#...#...#.#...#.#
#.#.###.###.#.#.#####.#.#########.#####.#.#################.#.#.###.###.#.###.#.#
#...#...#.....#.#...#.....#..q#.......#.#.......#...#.......#.#.#...#...#...#...#
#.###.###.#####.#.#.#######.#.#########.#########.#.#.#######.#.#.###.#####.###.#
#.#...#...#.....#.#.F.#.....#.........#.#.........#.#.#.........#...#.H...#...#.#
###.#######.#####.###.#.#############U#.#.###.#####.#.#########.###.#.###.#.###.#
#...#.....#.#...#...#.#.#...#.......#...#.#...#...#.#.....#...#...#.#...#...#...#
#.###.###.#.###.###.###.###.#.###.#.#####.#####.#.#.#####.#.#######.#########.###
#.....#...#.....#...#.....#...#...#.....#.....#.#.#.......#.#.......#.....#...#.#
#.#####.#######.#.###.###.#.###.#######.#.###.#.#.#######.#.#.###.###.###J#.###.#
#.....#.....#...#...#.#.#.#...#.....#...#...#...#.#.#.....#.#...#.#...#...#.#...#
#####.#####.#.#####.#.#.#.###.#####.#.###.#####.#.#.#.#####.#.#.#.#.###.#.#.###.#
#.....#...#.#.#.....#...#.#.#.#...#.#.#.#.#...#.#.#.....#...#.#.#.#..u#.#.#.....#
#.#######.#.#.#.#######.#.#.#.#.#.#.#.#.###.#.###.#######.###.#.###.###.#.#####.#
#.#.......#...#h#.......#.#...#.#.#.#.#c#...#...#...#.L.#...#.#...#.#...#.#.....#
#.###.#.#######.#.#######.#####.#.#.#.#.#.#####.###.#.#.###.#.###.#.#.#####.#####
#...#.#.....#...#...#...P.#.....#...#.#.#.#.........#.#.....#...#...#.....#.#...#
###.#####.#.#.#######.#####.#########.#.#.#.#########.#########.#########.#.#.#.#
#.#.....#.#.#.....#...#.....#.#.....#.#.#.#.#.....#...#...#...#.#..p..#.#.#...#.#
#.#####.#.#.#####.#.#####.###.#.#.###.#.#.###.###.#.###.###.#.#Q#.###.#.#.#####.#
#.......#.#.....#..z#.....#.#...#.....#.#...#...#.#.#...#...#.#...#.#.#.#..v..#.#
#.#######.#.###.#####.#.###.#.#########.###.###.#.#.#.#.#.###.#####.#.#.###.###.#
#.#.......#...#.#.....#.#.#...#...#...#.#...#...#.#.#.#.#.#.#.........#...#...#.#
#.###########.#.#######.#.#.###.#.#.#.#.#.###.###.#.#.#.#.#.#############.###.#.#
#.............#.........#.......#...#...........#...#.#....................f#...#
#######################################.@.#######################################
#.........#.....#.........#.....#.............#...............#.........#.......#
#.#####.###.###.#.#####.###.###.#.#.###.#.#.###.#########.###.#.#####.#.###.###.#
#.#.....#...#...#.....#...#.#.#...#...#.#.#.....#.......#.#...#.#.....#...#...#.#
###.#####.###.#.#####.###.#.#.#######.#.#.#######.###.###.###.#.#.#.#####.###.#.#
#...#.....#...#...#.#.#.#.#...#.....#.#.#.#...#...#.#...#...#.#.#.#.#...#.....#.#
#.###.#####.#####.#.#.#.#.###.#####.#.###.###.#.###.###.###.###.#.#.#.#.#.#######
#.#...#...#.....#.#.#.#.#...#.....#.#...#.#...#...#...#...#.....#.#.#.#.#.#.....#
#.#.###.#.#####.#.#.#.#.###.#####.#.###.#.#.#####.#.#.#.#.#######.###.#.###.###.#
#.#.#...#...#...#...#.#...#.....#.....#.#.#.........#.#.#.....#.#..d..#...#.#.#.#
#.#.#.#.###.#.#######.#.#.###.###.#####.#.#.#########.#.#####.#.#########.#.#A#.#
#...#.#.#.#.#...#.....#.#...#.#...#.....#.#.#...#.....#.#.#..m#.......#...#.#.#r#
#.#####.#.#.###.#.#######.#.#.#.###.###.#.###.#C#######.#.#.#########.#.###.#.#.#
#...#...#.#...#...#.......#.#...#l..#.#.#.....#.........#...#.........#.......#.#
###.#.###.###.#####.#####.#####.#.###.#.#################.###.###############.#.#
#.#.#.#.............#.....#...#.#...#...#.......#.........#...#.......#...#...#.#
#.#.#.###################.#.#.#####.#.###.#####.#.#########.###.#####.#.#.#####.#
#...#...#a..#...........#.#.#.......#...#.....#.#.....#.....#...#.......#.......#
#.#####.#.#.#.#########.#.#.#.###########.###.#.#####.###.#.#.###.#############.#
#...#...#.#.D.#...#...#.#.#.#.#.........#.#...#.#...#...#.#.#...#.....#.....#...#
###.#.#.#.###.#.#.#.#.#M###.###.#######.###.###.#.#.###.#.#####.###.###.###.#.###
#.....#.#.#...#.#...#.#...#.#...#.....#.#...#...#.#.......#..e#...#.#...#.#.#...#
#######.#.###.#.#########.#.#.###.###.#.#.#######.#########.#####.#.#.###.#.#####
#.....#.#...#.#.......#.....#.#...#...#.#.........#...#.....#...#.#.#.#...#.....#
#.###.#####.#########.#.#####.#####.#.#.#.#########.#.#.#####.#.#.###.#.#.#####.#
#.#.#.#...#.........#.#.#.....#.....#.#.#.#...#.....#.#i#.....#...#...#.#...#...#
#.#.#.#.#.###.#####.#.###.#####.#####.#.#.#.###.###.#.#.#.#########.#######.#.#.#
#.#.#...#.#...#.#...#.....#...#...#...#.#.#.#...#...#.#.#.............#.....#.#.#
#.#.#####.#.###.#.#########.###.#.#####.#.#.#.###.#####.#.###########.#.#####.###
#.#.....#.#.#.....#.......#.#...#...#...#.#.....#...#...#.#......w..#...#...#...#
#.#.#.###R#.#.#########.#.#.#.#####.#.###.#########.#.#####.#######.#####.#.###.#
#.#.#.......#.#.......#.#...#.#...#...#.#...........#...#...#.....#.......#...#.#
#.###########.#.#.###.#.#.###.#.#.#####.###.###########T#.#######.###########.#.#
#.#.....#.....#.#.#.#...#.#...#.#...#...#...#...........#.#.....#.........#.#...#
#.#.###.###.#####.#.#####.#.#####.#.#.#.#.###.###########.#.#.#.#.#####.#.#.#####
#.#.#.#...#...#...#.......#.....#.#...#.#.#.#.#...........#.#.#.#...#...#...#...#
#.#.#.###.###.#.#.#############.#####.#.#.#.#.###.###########.#.#####.#####.###.#
#.#.#...#.#.....#.#.S.........#.#...#.#y#..k#.G...#.........B.#.....#.....#...#.#
#.#.#.#.#.#########.#########.#.#.#.###.###.###########.###########.#####.###.#.#
#.....#.#...................#.O...#.....#...............#...........N.....#.....#
#################################################################################"""
print(solve_dungeon(puzzle, repeats=10))

import time, sys
import cProfile
N=10
# cProfile.run('run_for_N(N)')
cProfile.run('solve_dungeon(puzzle, quiet=True, repeats=N)')

# Interestingly: copy.deepcopy(dungeon) is slower than dungeon=Dungeon(parse)
# cProfile:
# 4.543    0.045 copy.py:128(deepcopy)
# 3.294    0.033 day18.py:301(create_dungeon)