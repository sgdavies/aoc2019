DEBUG=False
import copy, random, sys, collections

class Dungeon():
    def __init__(self, map_str):
        self.map_str = map_str
        self.parse_map(map_str)
        self.create_tree()  # All the examples & puzzle are trees, not looping graphs.
        self.count_doors_keys_and_depth(self.tree)

        self.pacman_location = self.name_to_tree_node['@']
        self.pacman_distance = 0

        def no_keys_here(node):
            # Split out for the debugger
            if isinstance(node, TreeKey):
                ret = False
            elif node.keys_below==0:
                ret = True
            else:
                ret = False

            if DEBUG: print("{}: {} ({}, {})".format(node.name, ret, isinstance(node, TreeKey), node.keys_below))
            return ret

        if False and DEBUG:
            import pdb; pdb.set_trace()
        self.tree.prune(no_keys_here)

        def boring_node(tree_node):
            if len(tree_node.children) == 1:
                if not isinstance(tree_node, TreeDoor) and not isinstance(tree_node, TreeKey):
                    tree_node.remove()
                elif isinstance(tree_node, TreeKey) and self.find_tree_node(tree_node.door_name()) is None and tree_node.keys_below > 0:
                    # Although it's a key, it's not a leaf and it doesn't open any doors, so change to a regular node
                    # (It must be picked up at some point when collecting the leaf)
                    tree_node.remove()

        self.tree.consolidate(boring_node)
        self.count_doors_keys_and_depth(self.tree)

        self.keys_collected = set()

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
        # For each node in our graph, create an equivalent tree node for it and add it to the tree.
        # Check that no node is added twice - if it is, this isn't a tree after all.
        nodes_visited = set()
        edges_used = set()
        root = self.find_node('@')
        nodes_visited.add(root)
        self.tree = TreeNode(None, 0, root.x, root.y, name=root.name)
        self.name_to_tree_node = {self.tree.name: self.tree}
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

            self.name_to_tree_node[child_tree_node.name] = child_tree_node
            self.create_child_nodes(child_node, child_tree_node, nodes_visited, edges_used)

    def show_tree(self, mode=None):
        # Print a summarized tree view of the dungeon
        # @-*-A-b
        # | |-a
        # | |-g
        # |-c-D-e
        #   |-d
        out_str = self._build_show_tree(self.tree, True, "", "", mode)

        print(out_str)  # cut off first '-'

    def _build_show_tree(self, node, first, stem, out_str, mode):
        # node - the node to add (and its descendents)
        # first - true if this is the first child of its parent (so don't add the stem)
        # stem -
        name = node.name if len(node.name)==1 else '*'

        if mode is None:
            extra_len = ""
        elif mode=="cost":
            extra_len = "  "
            name = "{:->2}".format(node.cost) + name
        elif mode=="keys":
            extra_len = "  "
            name += "{: <2}".format(node.keys_below)

        if first:
            out_str += '-' + name
        else:
            out_str += stem + '-' + name

        if node.children:
            for i, child in enumerate(node.children):
                if i == len(node.children) -1:
                    # Last node - don't put in the vertical bar
                    next_stem = stem + extra_len + "  "
                else:
                    next_stem = stem + extra_len + " |"
                out_str = self._build_show_tree(child, i==0, next_stem, out_str, mode)
        else:
            out_str += '\n'

        return out_str

    def count_doors_keys_and_depth(self, node):
        # Find out the number of keys below this node, the number of
        # doors beneath this node, and the maximum distance to the
        # lowest key (i.e. the farthest leaf) below this node.
        total_doors = 0
        total_keys = 0
        max_depth = 0
        for child in node.children:
            self.count_doors_keys_and_depth(child)
            total_doors += child.doors_below
            if isinstance(child, TreeDoor): total_doors += 1

            total_keys += child.keys_below
            if isinstance(child, TreeKey): total_keys += 1

            if child.max_depth_below + child.cost > max_depth:
                max_depth = child.max_depth_below + child.cost

        node.doors_below = total_doors
        node.keys_below = total_keys
        node.max_depth_below = max_depth

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

    def find_tree_node(self, name):
        return self.name_to_tree_node.get(name, None)

    def go_to_node(self, dest_node):
        # Travel from current location to the specified node.
        # Pick up all keys traversed en route, and keep track of distance travelled.
        route_up, route_down = self.pacman_location.find_route(dest_node)

        for node in route_up[:-1]:
            self.pacman_distance += node.cost
            if isinstance(node, TreeKey):
                self.pick_up_key(node)

        for node in route_down[1:]:
            self.pacman_distance += node.cost
            if isinstance(node, TreeKey):
                self.pick_up_key(node)

        self.pacman_location = dest_node

    def pick_up_key(self, key_node):
        if key_node in self.keys_collected:
            # Don't double-open doors, or the costs will get out of whack
            return

        # open the door, and add the key to our list of collected keys
        if door := self.find_tree_node(key_node.door_name()):
            door.remove()

        self.keys_collected.add(key_node)

    def visible_tree_nodes(self, from_node=None, acc=None, stop_at_keys=False):
        # 'visible' means not hidden behind a door
        # Because it's a tree, and we start at the root, from wherever we are we can see the same as the root can see.
        if from_node is None: from_node = self.tree
        if acc is None: acc = []

        acc.append(from_node)

        for child in from_node.children:
            if stop_at_keys and isinstance(child, TreeKey):
                acc.append(child)
            elif not isinstance(child, TreeDoor):
                self.visible_tree_nodes(child, acc, stop_at_keys=stop_at_keys)

        return acc

    def visible_tree_keys(self, stop_at_keys=False):
        return [node for node in self.visible_tree_nodes(stop_at_keys=stop_at_keys) if (isinstance(node, TreeKey) and node not in self.keys_collected)]

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

        # Filled out later (when whole tree exists) by count_doors_keys_and_depth()
        self.doors_below = 0
        self.keys_below = 0
        self.max_depth_below = 0

        self.name = name if name else "T{}.{}".format(x,y)
        self.children = children if children else []
        if self.parent: self.parent.add_child(self)

    def __str__ (self):
        return str(self.__class__) + "-<" + self.name + ">"

    def __repr__ (self):
        return self.__str__()

    def add_child(self, child):
        self.children.append(child)

    def remove(self):
        # Remove this node from the tree, by joining the children to the parent
        # a-(*)-b  ==>  a-b
        # and a-(*)-b  ==>  a-b
        #         \-c       \-c
        if not self.parent:
            # Don't remove the root node
            # log.debug("Can't remove the root node")
            return

        for child in self.children:
            child.parent = self.parent
            child.cost += self.cost
            child.parent.add_child(child)

        try:
            self.parent.children.remove(self)
        except ValueError:
            # Slight hack: during pruning, we may have taken a dead-end door
            # out of the tree.  In that case, we still know about the door (we
            # currently don't remove it from the nodes dict), but it's no
            # longer connected to anything.  That's OK - just carry on.
            if isinstance(self, TreeDoor):
                pass
            else:
                import traceback
                traceback.print_stack()
                print(traceback.format_exc())
                import pdb; pdb.set_trace()

    def consolidate(self, predicate):
        # Join together boring nodes below here - nodes that aren't doors, keys, or junctions
        # (or rather, nodes that satisfy the passed-in predicate)
        # I.e. a-*-*-b-*-c ==> a-b-*-c
        #              \-d         \-d
        if predicate(self):
            self.remove()

        for child in list(self.children):
            child.consolidate(predicate)

    def prune(self, predicate):
        # Remove all children that satisfy `predicate` from the tree
        for child in list(self.children):  # list necessary?
            if predicate(child):
                self.children.remove(child)
            else:
                child.prune(predicate)

    def distance(self, other_node):
        # find the common parent, then add the two legs
        # one may be an ancestor of the other
        my_ancestors = self._ancestor_distances()
        thy_ancestors = other_node._ancestor_distances()

        # print([(k.name, v) for k,v in my_ancestors.items()])
        # print([(k.name, v) for k,v in thy_ancestors.items()])

        if other_node in my_ancestors:
            return my_ancestors[other_node]

        # import pdb;pdb.set_trace()
        for ancestor, dist in my_ancestors.items():
            if ancestor in thy_ancestors:
                return dist + thy_ancestors[ancestor]

    def _ancestor_distances(self, acc=None):
        # return an OrderedDict of ancestors, and total distance to those ancestors
        # (root)-1-A-2-B-3-C-4-(this) ==> {(C,4), (B,7), (A,9), (root,10)}
        if acc is None:
            acc = collections.OrderedDict()
            acc[self] = 0

        if self.parent:
            acc[self.parent] = list(acc.values())[-1] + self.cost
            self.parent._ancestor_distances(acc)

        return acc

    def _ancestors(self):
        # Returns a list of nodes from this up to the root
        # Could calculate at start-of-day but would need to handle removal
        if not self.parent: return []

        ancestor = self
        ancestors = []
        while next_ancestor := ancestor.parent:
            ancestors.append(next_ancestor)
            ancestor = next_ancestor

        return ancestors

    def find_route(self, other_node):
        # Finds the unique route from this to the other node.
        # Returns two lists - the route up the tree, and the route back down again.
        # If the other node is above this one in the tree, those lists will be:
        # [this, ..., other], []
        # If the other node is below this one in the tree, the lists will be:
        # [], [this, ..., other]
        # If the nodes are in different branches of the tree, the lists will be:
        # [this, ..., common_parent], [common_parent, ..., other]
        my_ancestors = self._ancestors()

        if other_node in my_ancestors:
            # Just need to go up
            end = my_ancestors.index(other_node)
            return [self] + my_ancestors[:end+1], []

        thy_ancestors = other_node._ancestors()

        if self in thy_ancestors:
            # Just need to go down
            end = thy_ancestors.index(self)
            return [], ([other_node] + thy_ancestors[:end+1])[::-1] # Reverse order

        # We have a common ancestor.
        for node in my_ancestors:
            if node in thy_ancestors:
                common = node
                break

        route_up = [self] + my_ancestors[: my_ancestors.index(common)+1]
        route_down = ([other_node] + thy_ancestors[: thy_ancestors.index(common)+1])[::-1]
        return route_up, route_down


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

def solve_tree_dungeon(dungeon, starting_order="", debug=False):
    distance_travelled = 0
    key_path = "@"
    choices = 1
    current = dungeon.find_tree_node('@')
    #import pdb; pdb.set_trace()

    # TODO: for some reason following this exact path gives a higher number
    # (6976) than when random choice found this path (6328).  So something is
    # borked with the calcs ... somewhere.
    preferred_order = [c for c in starting_order]

    while keys_available := dungeon.visible_tree_keys(): #stop_at_keys=True):
        choices *= len(keys_available)

        # Choose where to go next
        # next_key = keys_available[0]  # Arbitrary

        # Try the preferred order first
        available_key_names = [k.name for k in keys_available]
        next_key = None

        for preferred in preferred_order:
            if preferred in available_key_names:
                next_key = dungeon.name_to_tree_node[preferred]
                available_key_names.remove(preferred)
                break

        if next_key is None:
            next_key = random.choice(keys_available)  # default choice method

        key_path += next_key.name
        dungeon.go_to_node(next_key)  # travel from here to there, and pick up all keys on the way

        current = next_key
        if debug:
            print (dungeon.pacman_distance, current.name, key_path); sys.stdout.flush()

    # print(choices)
    # print(key_path)
    # print(distance_travelled)
    #return distance_travelled, key_path, choices
    return dungeon.pacman_distance, key_path, choices

def solve_the_dungeon(dungeon, quiet=False):
    # Returns best_distance, path, choices
    pacman_is_at = dungeon.find_node('@')
    remaining_keys = set(dungeon.keys)
    distance_travelled = 0
    choices = 1
    key_path="@"

    # Would be good to modify this to not affect the underlying graph - then it would be faster to do repeats
    try:
        while remaining_keys:
            # visible_doors = dungeon.visible_doors(pacman_is_at)
            visible_keys = dungeon.visible_keys(pacman_is_at, stop_on_keys=True)  # Not necessarily correct - perhaps we shouldn't show keys that are hidden behind outher keys (since we must pick up the first key on the way to the second)
            if DEBUG: print([x.name for x in visible_doors+visible_keys])
            choices *= len(visible_keys)

            # Pick up a key, then 'open' the relevant door - i.e. remove that door node.
            next_key = random.choice(visible_keys)
            key_path += next_key.name
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
    return distance_travelled, key_path, choices


def solve_dungeon(mapp, solver, quiet=True, repeats=1, *args, **kwargs):
    # dungeon = create_dungeon(mapp)
    # solve_tree_dungeon(dungeon)

    lowest_distance = None
    best_path = None
    for repeat in range(repeats):
        # test_dungeon = copy.deepcopy(dungeon)  # Slower than create_dungeon()
        dungeon = create_dungeon(mapp)
        distance, key_path, choices = solver(dungeon, args, kwargs) # TODO, quiet=quiet)

        if lowest_distance is None or distance < lowest_distance:
            lowest_distance = distance
            best_path = key_path

    if True or  not quiet: print(lowest_distance, key_path, choices)
    return lowest_distance

def show_tree(mapp):
    print(mapp)
    print()
    dungeon = Dungeon(mapp)
    dungeon.show_tree()
    dungeon.show_tree(mode="cost")

# Best is 8
example_1 = """#########
#b.A.@.a#
#########"""
print(solve_dungeon(example_1, solve_tree_dungeon, repeats=10), "vs", 8)
show_tree(example_1)

# Best is 86
example_2="""########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################"""
print(solve_dungeon(example_2, solve_tree_dungeon, repeats=10), "vs", 86)
# show_tree(example_2)

# Best is 132
example_3 = """########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################"""
print(solve_dungeon(example_3, solve_tree_dungeon, repeats=10), "vs", 132)
# show_tree(example_3)

# Best is 136
# Approx 2e11 choices...
example_4 = """#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################"""
# Example 4 is quite slow
if False:
    print(solve_dungeon(example_4, solve_tree_dungeon, repeats=1000), "vs", 136)
    show_tree(example_4)

# Best is 81
example_5 = """########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################"""
print(solve_dungeon(example_5, solve_tree_dungeon, repeats=10), "vs", 81)
# show_tree(example_5)

# exit()

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
# print(solve_dungeon(puzzle, repeats=10))

# import time, sys
# import cProfile
# N=10
# # cProfile.run('run_for_N(N)')
# cProfile.run('solve_dungeon(puzzle, quiet=True, repeats=N)')

# Interestingly: copy.deepcopy(dungeon) is slower than dungeon=Dungeon(parse)
# cProfile:
# 4.543    0.045 copy.py:128(deepcopy)
# 3.294    0.033 day18.py:301(create_dungeon)
# DEBUG=True
dungeon = Dungeon(puzzle)
dungeon.show_tree(mode="keys")
dungeon.show_tree(mode="cost")
dungeon.show_tree()

all_lowest = []

solve_tree_dungeon(dungeon, starting_order="wlgtcekobayxvjuqfh", debug=True)

exit()

for _ in range(5):
    all_lowest.append(solve_dungeon(puzzle, solve_tree_dungeon, repeats=100))

print()

print( min(all_lowest) )

import timeit

#print(timeit.timeit("solve_dungeon(puzzle, solve_tree_dungeon, repeats=100)", number=1, globals=globals()))            ; sys.stdout.flush()
