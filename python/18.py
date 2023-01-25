INF = 1000000000 # infinity - for use in dijkstra's algorithm

def is_key(c): return 'a'<=c<='z'
def is_door(c): return 'A'<=c<='Z'

# Build the graph.
# Main algo is to maintain list of states, ordered by distance covered so far.
# Take shortest-distance state and create new states based on neighbiours from
# that state.  Stop when the top state has all the keys -- it's guaranteed to
# be the shortest way to get there.
# Part one is built back from part two (replacing previous very slow part one
# algo).  Easiest to understand how part two works and then look at the
# modifications for part one.

class Node():
    def __init__(self, name, parent, parent_dist):
        self.name = name
        self.parent = parent if parent is None else (parent.name, parent_dist) # (name,dist)
        self.children = [] # list of (name,dist)

class MiniMaze():
    def __init__(self, world:dict, start_point:tuple):
        def candidates(point):
            x,y = point
            return [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
        def search_from(point, prev: Node, dist: int, world: dict, nodes=None, visited=None):
            if nodes is None: nodes = {}
            if visited is None: visited = set()
            visited.add(point)
            c = world[point]
            moves = [p for p in candidates(point) if p in world]
            is_chr = c=='@' or is_key(c) or is_door(c)
            if is_chr or len(moves) > 2:  # New key, door or junction - a new node.
                name = c if is_chr else "{}-{}".format(point[0],point[1])
                node = Node(name, prev, dist)
                nodes[name] = node
                if prev is not None: prev.children.append( (name, dist) )
                dist = 0
            else:
                node = prev

            moves = [m for m in moves if m not in visited]
            for move in moves:
                search_from(move, node, dist+1, world, nodes, visited)
            return nodes # slight hack - nodes is modified anyway
        
        self.nodes = search_from(start_point, None, 0, world)
        self.keys = [name for name in self.nodes.keys() if is_key(name)]
        self.dists, self.doors = self.precalc_distances()

    def precalc_distances(self):
        # Return double-dict of all keys to all other keys : d[start][end] = distance
        dists = {}
        doors = {}
        for s in ['@']+self.keys:
            d,k = self.dijk(s)
            dists[s] = d
            doors[s] = k
        return dists, doors

    def dijk(self, source):
        Q = []
        dist = {}
        doors = {}
        for v in self.nodes.keys():
            dist[v] = INF
            doors[v] = ""
            Q.append(v)
        dist[source] = 0

        while Q:
            Q = sorted(Q, key=lambda x: dist[x])
            u = Q.pop(0)
            node_u = self.nodes[u]
            neighbours = list(node_u.children)
            if node_u.parent is not None: neighbours.append((node_u.parent[0], node_u.parent[1]))
            for v,vd in [n for n in neighbours if n[0] in Q]:
                alt = dist[u] + vd
                if alt < dist[v]:
                    dist[v] = alt
                    keys_needed = doors[u]
                    if is_door(v): keys_needed += v.lower()
                    doors[v] = keys_needed
        return dist, doors

    # pretty-print the tree
    def show_tree(self):
        # Print a summarized tree view of the maze
        # @-*-A-b
        # | |-a
        # | |-g
        # |-c-D-e
        #   |-d
        out_str = self._build_show_tree('@', True, "", "")
        print(out_str)

    def _build_show_tree(self, node_name, first, stem, out_str):
        # node - the node to add (and its descendents)
        # first - true if this is the first child of its parent (so don't add the stem)
        # stem - left padding (to offset children)
        node = self.nodes[node_name]
        name = node_name if len(node_name)==1 else '*'

        if first: out_str += '-' + name
        else: out_str += stem + '-' + name

        if node.children:
            for i, child in enumerate(node.children):
                if i == len(node.children) -1:
                    # Last node - don't put in the vertical bar
                    next_stem = stem + "  "
                else:
                    next_stem = stem + " |"
                out_str = self._build_show_tree(child[0], i==0, next_stem, out_str)
        else:
            out_str += '\n'

        return out_str

class Maze():
    def __init__(self, s: str, part_one: bool):
        self.part_one = part_one
        self.mazes = self.parse_input(s) # 4 separate nodes lists
        self.n_keys = sum([len(maze.keys) for maze in self.mazes])

    def parse_input(self, s: str):
        world = {}
        for row,line in enumerate(s.split('\n')):
            for col,c in enumerate(line):
                if c not in '#\n': world[(row,col)] = c
                if c=='@': centre = (row,col)
        # split into 4 quadrants
        cr,cc = centre
        starts = [(cr-1,cc-1), (cr+1,cc-1), (cr-1,cc+1), (cr+1,cc+1)]
        new_walls = [(cr,cc-1),(cr,cc+1), (cr,cc), (cr-1,cc),(cr+1,cc)]
        for r,c in starts: world[(r,c)] = '@'
        for r,c in new_walls:
            if (r,c) in world: del world[(r,c)]

        mazes = [MiniMaze(world, start) for start in starts]

        if self.part_one:
            # Join the four mazes together into a megamaze.
            class DummyMaze: pass
            megamaze = DummyMaze()
            megamaze.keys = []
            for maze in mazes: megamaze.keys += maze.keys
            megamaze.dists = {k:{} for k in megamaze.keys+['@', '*']}
            megamaze.doors = {k:{} for k in megamaze.keys+['@', '*']}
            # Add up dists.  When traversing the center, cost is 2 unless
            # crossing from NE to SW or NW to SE (or vice versa), in which case it's 4.
            for ix in range(len(mazes)):
                for jx in range(ix, len(mazes)):
                    if ix==jx: continue  # Next jx. For keys within a quadrant they don't cross the center.

                    if (ix==0 and jx==3) or (ix==1 and jx==2): cross = 4
                    else: cross = 2
                    for k1 in mazes[ix].keys:
                        for k2 in mazes[jx].keys:
                            dist = mazes[ix].dists['@'][k1] + cross + mazes[jx].dists['@'][k2]
                            doors = mazes[ix].doors['@'][k1] + mazes[jx].doors['@'][k2]
                            megamaze.dists[k1][k2] = dist
                            megamaze.dists[k2][k1] = dist
                            megamaze.doors[k1][k2] = doors
                            megamaze.doors[k2][k1] = doors

                # Add keys within the same quadrant - dists are just the same
                for k1 in mazes[ix].keys:
                    for k2 in mazes[ix].keys:
                        megamaze.dists[k1][k2] = mazes[ix].dists[k1][k2]
                        megamaze.doors[k1][k2] = mazes[ix].doors[k1][k2]

                # Add the starting distance - from dead center to first key
                for k in mazes[ix].keys:
                    megamaze.dists['*'][k] = mazes[ix].dists['@'][k] + 2
                    megamaze.doors['*'][k] = mazes[ix].doors['@'][k] 
            return [megamaze]
        else:
            return mazes

    def new_solve(self, show_progress=False):
        if self.part_one:
            state = (0, ('*',), "")
        else:
            state = (0, ('@', '@', '@', '@'), "") # dist first, for easy sorting
        try:
            from sortedcontainers import SortedSet
            states = SortedSet()
            add_state = states.add
        except ModuleNotFoundError:
            print("Warning: using slower list type.  Try installing sortedcontainers.")
            states = []
            def add_state(state):
                states.append(state)
                states.sort()
        add_state(state)

        best = None
        if show_progress:
            best_path = ""
            import time
            last_t = time.time()

        while s := states.pop(0):
            d,locs,keys = s
            if show_progress and len(keys) > len(best_path): # Debugging - show progress
                best_path = keys
                spaces = " "*(self.n_keys - len(best_path))
                next_t = time.time()
                print(best_path, spaces, "\t%0.2f"%(next_t-last_t), "\t", len(states), "\t", d)
                last_t = next_t

            if len(keys) == self.n_keys:
                best = d
                break

            for maize in range(len(self.mazes)):
                maze = self.mazes[maize]
                loc = locs[maize]
                for key in maze.keys:
                    if key in keys: continue  # Already been there
                    if not all([k in keys for k in maze.doors[loc][key]]): continue  # Can't get there yet

                    new_keys = "".join(sorted(keys+key))  # sorted so we match similar states
                    new_state = (d+maze.dists[loc][key], locs[:maize]+(key,)+locs[maize+1:], new_keys)
                    add_state(new_state)

        assert best is not None
        return best

maze1="""#######
#a.#Cd#
##...##
##.@.##
##...##
#cB#Ab#
#######"""
maze2="""###############
#d.ABC.#.....a#
######...######
######.@.######
######...######
#b.....#.....c#
###############"""
maze3="""#############
#DcBa.#.GhKl#
#.###...#I###
#e#d#.@.#j#k#
###C#...###J#
#fEbA.#.FgHi#
#############"""
maze4="""#############
#g#f.D#..h#l#
#F###e#E###.#
#dCba...BcIJ#
#####.@.#####
#nK.L...G...#
#M###N#H###.#
#o#m..#i#jk.#
#############"""
maze_slow="""###################
#i.G..c..#..e..H.p#
########.#.########
#j.A..b..#..f..D.o#
########.@.########
#k.E..a..#..g..B.n#
########.#.########
#l.F..d..#..h..C.m#
###################"""
with open('18.txt') as f: maze = f.read()

if __name__ == "__main__":
    if True: # tests
        assert(Maze(maze1, False).new_solve() == 8)
        assert(Maze(maze2, False).new_solve() == 24)
        assert(Maze(maze3, False).new_solve() == 32)
        assert(Maze(maze4, False).new_solve() == 72)

        # part one - values by inspection, then by running working code
        assert(Maze(maze1, True).new_solve() == 26)  # 26
        assert(Maze(maze2, True).new_solve() == 50) # acbd 50
        assert(Maze(maze3, True).new_solve() == 127) # 127
        assert(Maze(maze4, True).new_solve() == 114) # 114

        print("Tests passed")

    if True:
        print(Maze(maze, True).new_solve())
        print(Maze(maze, False).new_solve())