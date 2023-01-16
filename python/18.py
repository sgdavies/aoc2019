INF = 1000000000 # infinity - for use in various algos

def is_key(c): return 'a'<=c<='z'
def is_door(c): return 'A'<=c<='Z'

class Node():
    def __init__(self, name, parent, parent_dist):
        self.name = name
        self.parent = parent if parent is None else (parent.name, parent_dist) # (name,dist)
        self.children = [] # list of (name,dist).
        self._keys = None # Keys hidden below this node (only relevant for doors and start)
        self._doors = None # As above, but for doors

    # Call this to calculate self._keys, self._doors for this node and all below it
    def find_hidden(self, nodes):
        if self._keys is None:
            assert(self._doors is None) # Both get calculated at the same time
            keys = [self.name] if is_key(self.name) else []
            doors = [self.name] if is_door(self.name) else []
            for child,_dist in self.children: # Calculate for all nodes, even if we can't see them
                child_keys,child_doors = nodes[child].find_hidden(nodes)
                if not is_door(child): keys += child_keys  # but only add non-hidden ones
                if is_door(child):
                    doors += [child]
                else:
                    doors += child_doors
            self._keys = keys
            self._doors = doors
        return self._keys, self._doors

    def get_keys(self, nodes):
        if self._keys is None:
            self.find_hidden(nodes)
        return self._keys

    def __repr__(self):
        if self.parent is not None:
            return "({})->{}".format(self.parent[0], self.name)
        else:
            return "*"+self.name

class Maze():
    def __init__(self, s: str):
        self.nodes = self.parse_input(s)
        self.nodes['@'].find_hidden(self.nodes)  # Find out which keys are hidden behind each node
        self.precalc_distances()

    def parse_input(self, s: str):
        world = {}
        for row,line in enumerate(s.split('\n')):
            for col,c in enumerate(line):
                if c not in '#\n': world[(row,col)] = c
                if c=='@': start = (row,col)

        def candidates(point):
            x,y = point
            return [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]

        visited = set()
        nodes = {}
        def search_from(point, prev: Node, dist: int):
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
                search_from(move, node, dist+1)

        search_from(start, None, 0)  # Create dict of nodes
        return nodes

    def precalc_distances(self):
        # Return double-dict of all keys to all other keys : d[start][send] = distance
        ## TODO enhance: each x-y, also return list of keys picked up enroute, and list of doors(?)
        ## With keys: then when chosing to go to a key, automatically collect the enroute ones.
        ## This should reduce (a lot?) the number of subsequent choices.
        keys = [node.name for node in self.nodes.values() if is_key(node.name)]
        dists = {}
        prevs = {}
        for s in ['@']+keys:
            #dists[s] = dijk(nodes, s)
            d,p = self.dijk(s)
            dists[s] = d
            prevs[s] = p
        self.dists = dists
        self.keys_on_route = prevs
        #print(self.dists)
        #print(self.keys_on_route)

    def dijk(self, source):
        Q = []
        dist = {}
        for v in self.nodes.keys():
            dist[v] = INF
            Q.append(v)
        dist[source] = 0
        xprev = {}
        xprev[source] = []

        while Q:
            Q = sorted(Q, key=lambda x: dist[x])
            u = Q.pop(0)
            node_u = self.nodes[u]
            neighbours = node_u.children
            if node_u.parent is not None: neighbours.append((node_u.parent[0], node_u.parent[1]))
            for v,vd in [n for n in neighbours if n[0] in Q]:
                alt = dist[u] + vd
                if alt < dist[v]:
                    dist[v] = alt
                    xprev[v] = xprev[u]+ ([v] if is_key(v) else [])
        return dist, xprev

    def solve(self, order=None):
        all_keys = [name for name in self.nodes.keys() if is_key(name)]
        vis_keys, vis_doors = self.nodes['@'].find_hidden(self.nodes)

        best,best_order = self.solve_from(len(all_keys), vis_keys, vis_doors, '@', 0, '', order)
        #print(best_order)
        return best

    def solve_from(self, n_keys, vis_keys, vis_doors, loc, dist, collected_keys, order=None):
        if len(collected_keys) == n_keys: return dist, collected_keys
        #if len(collected_keys) < 3 or order is not None: print(loc,dist,collected_keys,vis_keys,vis_doors)

        best = None
        best_order = "FAILED"
        if order:
            choices = [order[0]]
            order = order[1:]
            #print("oc",choices, order)
        else:
            choices = vis_keys
        for next_key in choices:
            #if order is not None: print("->", next_key)
            new_keys = self.keys_on_route[loc][next_key]
            new_vk = set(vis_keys)
            new_vk -= set(new_keys)
            new_coll = collected_keys + "".join([k for k in new_keys if k not in collected_keys])
            new_vd = set(vis_doors)

            if True:
                new_vk, vew_vd = self.open_doors(new_keys, new_vk, new_vd, new_coll)
            else:
              dfk = next_key.upper() # door for this key
              if dfk in self.nodes and dfk in vis_doors:  # this key that unlocks a visible door
                newkeys,newdoors = self.nodes[dfk].find_hidden(self.nodes)
                new_vk.update(newkeys)
                doors_to_check = set(newdoors)
                while doors_to_check:
                    door_to_check = doors_to_check.pop()
                    new_vd.add(door_to_check) # It's visible
                    if door_to_check.lower() in collected_keys: # We already have a key for it
                        newkeys,newdoors = self.nodes[door_to_check].find_hidden(self.nodes)
                        new_vk.update(newkeys)
                        doors_to_check.update(newdoors)
                        doors_to_check.discard(door_to_check)

            this_dist,this_order = self.solve_from(n_keys, new_vk, new_vd, next_key, dist+self.dists[loc][next_key], new_coll, order)

            if this_dist is not None and (best is None or this_dist < best):
                best = this_dist
                best_order = this_order

        return best, best_order

    def open_doors(self, new_keys, vis_keys, vis_doors, collected_keys):
        # ---A-B-C-D   Already have: bce,agk  (collected_keys)
        # *  *-E-F     Of which we just picked up: agk  (new_keys)
        # *            After: should be able to see D,F,H,J (and not I,K)
        # *--G-H-I 
        #    *-J-K     Return updated vis_keys, vis_doors
        for k in new_keys:
            d = k.upper()
            if d in self.nodes and d in vis_doors:  # key opens an accessible door
                ks,ds = self.nodes[d].find_hidden(self.nodes)
                vis_keys.update([nk for nk in ks if nk not in collected_keys])
                ds = set(ds)
                while ds:
                    dd = ds.pop()
                    vis_doors.add(dd)
                    if dd.lower() in collected_keys:
                        kis,dis = self.nodes[dd].find_hidden(self.nodes)
                        vis_keys.update([nk for nk in kis if nk not in collected_keys])
                        ds.update(dis)
                        ds.discard(dd)  # unnecessary? but safe (dd=ds.pop())
        return vis_keys, vis_doors

maze1 = """#########
#b.A.@.a#
#########"""
maze2 = """########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################"""
maze3 = """########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################"""
maze4 = """#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################"""
maze5 = """########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################"""

if __name__ == "__main__":
    assert(Maze(maze1).solve() == 8)
    assert(Maze(maze2).solve() == 86)
    assert(Maze(maze3).solve() == 132)
    assert(Maze(maze5).solve() == 81)
    exit()
    import time
    o="afbjgnhdloepcikm"
    maze=Maze(maze4)
    for i in range(9,12):
        to=o[:-i]
        print("#{}#".format(to))
        start=time.time()
        ans = maze.solve(order=to)
        t = time.time()-start
        print(ans,'\t',len(to),'\t',"%.2f"%t)
    #print(Maze(maze4).solve(order="")) # takes too long # ==136
    #print(Maze(maze4).solve()) # takes too long # ==136
