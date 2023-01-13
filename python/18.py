def is_key(c): return 'a'<=c<='z'
def is_door(c): return 'A'<=c<='Z'

class Node():
    def __init__(self, name, parent, loc):
        self.name = name
        self.loc = loc  # (x,y) location TODO needed?
        self.parent = parent # (name,dist)
        self.children = [] # list of (name,dist).
        self.keys = None # Keys hidden below this node (only relevant for doors and start)

    def find_keys(self, nodes): # All keys below me in the tree that are not behind doors
        if self.keys is None:
            keys = [self.name] if is_key(self.name) else []
            for child,_dist in self.children:
                child_keys = nodes[child].find_keys(nodes) # Calculate for all keys
                if not is_door(child): keys += child_keys  # but only add non-hidden ones
            self.keys = keys
        return self.keys

    def __repr__(self):
        parent = self.parent[0] # Name
        if parent is not None:
            return "({})->{}".format(parent, self.name)
        else:
            return self.name

def parse_input(s: str):
    world = {}
    for row,line in enumerate(s.split('\n')):
        for col,c in enumerate(line):
            if c not in '#\n': world[(row,col)] = c
            if c=='@': start = (row,col)
    #print(world)

    def candidates(point):
        x,y = point
        return [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]

    visited = set()
    nodes = {}
    def search_from(point, prev: Node, dist: int):
        visited.add(point)
        c = world[point]
        #print("sf",c, point, prev, dist)
        moves = [p for p in candidates(point) if p in world] #TODO and p not in visited]
        is_chr = c=='@' or is_key(c) or is_door(c)
        if is_chr or len(moves) > 2:  # New key, door or junction - a new node.
            name = c if is_chr else "{}-{}".format(point[0],point[1])
            node = Node(name, (prev,dist), point)
            nodes[name] = node
            if prev is not None: prev.children.append( (name, dist) )
            dist = 0
        else:
            node = prev

        moves = [m for m in moves if m not in visited]
        for move in moves:
            search_from(move, node, dist+1)

    search_from(start, None, 0)  # Create dict of nodes
    nodes['@'].find_keys(nodes)  # Find out which keys are hidden behind each node
    keys = [node.name for node in nodes.values() if is_key(node.name)]

    return nodes, keys

def precalc_distances(nodes):
    # Return double-dict of all keys to all other keys : d[start][send] = distance
    keys = [node.name for node in nodes.values() if is_key(node.name)]
    dists = {}
    for s in ['@']+keys:
        dists[s] = dijk(nodes, s)
    return dists

def dijk(nodes, source):
    print("dijk",source,":",nodes.keys())
    Q = []
    dist = {}
    for v in nodes.keys():
        dist[v] = 1000000000 # infinity
        Q.append(v)
    dist[source] = 0

    while Q:
        Q = sorted(Q, key=lambda x: dist[x])
        u = Q.pop(0)
        node_u = nodes[u]
        neighbours = node_u.children
        if node_u.parent[0] is not None: neighbours.append(node_u.parent)
        for v,vd in [n for n in neighbours if n[0] not in Q]:
            alt = dist[u] + vd
            if alt < dist[v]:
                dist[v] = alt
    return dist

def solve(nodes):
    dists = precalc_distances(nodes)
    visible_keys = set(nodes['@'].get_keys())

    dist = 0
    loc = '@'
    while visible_keys:
        next_key = visible_keys.pop() # Arbitrary
        dist += dists[loc][next_key]
        loc = next_key
        visible_keys.add(nodes[next_key.upper()].get_keys())
    return dist

if __name__ == "__main__":
    maze1 = """#########
#b.A.@.a#
#########"""
    maze2 = """#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################"""

    maze = maze1
    nodes, keys = parse_input(maze)
    print(keys)
    #print(nodes)
    #for name, node in nodes.items(): print(name, node.keys)
    print(solve(nodes))
