import math, time
DEBUG=0

def ore_for_recipe(recipe):
    source_dict = {}

    for line in recipe.split("\n"):
    	# line is "aAA, bB, cCCC => xXXX"
    	ingredients, output = [elem.strip() for elem in line.split("=>")]
    	out_num, out_name = output.split(" ")
    	assert(out_name not in source_dict)
    	out_num = int(out_num)

    	ingred_list = []
    	for ingredient in ingredients.split(", "):
    		ni, ing = ingredient.split(" ")
    		ni = int(ni)
    		ingred_list.append((ni, ing))
    	source_dict[out_name] = (out_num, ingred_list)

    if DEBUG: print(source_dict)

    suggested_order = get_order(source_dict)
    if DEBUG: print(suggested_order)

    unused = set(source_dict.keys())
    unused.add("ORE")
    states = []

    try:
        ore, ok = ore_for_list([(1,"FUEL")], 0, unused, source_dict, suggested_order, states)
    except Exception as ex:
        import traceback; print(traceback.format_exc())
        import pdb; pdb.set_trace()
        raise
    assert(ok)

    if DEBUG: print(ore)
    return ore

def ore_for_list(numbered_list, depth, unused, source_dict, suggested_order, states):
    # Work out how much ore is needed to create this ingredient list
    # numbered_list is e.g. [(2,A), (3,B), (4,ORE)]
    # Return (_, False) if we try to deconstruct an ingredient that's already been used
    # Otherwise return (ore_needed, True)
    if DEBUG>1:
        next_state = "{}\t{}\t{}\t{}".format(str(numbered_list).replace(' ',''), depth, str(unused).replace(' ',''), str(suggested_order).replace(' ',''))
        states.append(next_state)
        print(next_state)

    # Start by combining similar ingredients
    numbered_list = combine(numbered_list)

    # # Exit condition - satisfied! -- but - what about checking `unused`?
    if len(numbered_list)==1 and numbered_list[0][1]=="ORE":
        return numbered_list[0][0], True

    # Work out required components
    ingredients = set([ingredient for _, ingredient in numbered_list])
    components = set()
    for ingredient in ingredients:
        if ingredient=="ORE":
            components.add(ingredient)
        else:
            recipe = source_dict[ingredient][1]  # Just the numbered_list of components
            components.update([ing for _,ing in recipe])

    # Try each path down the list in turn, until one succeeds or we've failed
    ore, ok = None, False
    for try_number, try_ingredient in numbered_list:
        # Avoid going down rabbit holes
        if try_ingredient not in suggested_order[0]:
            continue

        # If we've already collected this ingredient, we're in a dead end - abort
        if try_ingredient not in unused:
            continue
        # Replace that ingredient in the list
        next_unused = set(unused)
        next_unused.remove(try_ingredient)

        next_list = list(numbered_list)
        next_list.remove((try_number, try_ingredient))
        added_ingredients = ingredients_for_ingredient(try_number, try_ingredient, source_dict)
        next_list += added_ingredients
        next_suggested_order = list(suggested_order)
        next_suggested_order[0].remove(try_ingredient)
        if len(next_suggested_order[0])==0: next_suggested_order.pop(0)
        ore, ok = ore_for_list(next_list, depth+1, next_unused, source_dict, next_suggested_order, states)

        if ok:
            # suggested_order[0].remove(try_ingredient)
            # if len(suggested_order[0]) == 0:
            #     suggested_order.pop(0)
            break

    return ore, ok

def ingredients_for_ingredient(how_many, ingredient, source_dict):
    # find minimum number of each component required to make that ingredient
    if ingredient=="ORE":
        return [(how_many, ingredient)]

    number, components = source_dict[ingredient]
    number = math.ceil(how_many/number)

    return [(number*n, component) for n,component in components]

def combine(numbered_list):
    # Take a list like [(2,A), (3,B), (4,A)] and return [(6,A) (3,B)]
    counting_dict = {}
    for n, component in numbered_list:
        counting_dict[component] = counting_dict.get(component, 0) + n

    return [(n, component) for component,n in counting_dict.items()]

def get_order(source_dict):
    # Work out longest path to get to FUEL from ORE
    # Return ingredients sorted into lists based on furthest distance from ORE
    # So e.g. {A:(10,[(10,ORE)]),B:(1,[(1,ORE)]),C:(1,[(7,A),(1,B)]),D:(1,[(7,A),(1,C)]),E:(1,[(7,A),(1,D)]),FUEL:(1,[(7,A),(1,E)])}
    # turns to:
    # FUEL-A-ORE
    # FUEL-E-A-ORE
    # FUEL-E-D-A-ORE
    # FUEL-E-D-C-A-ORE
    # FUEL-E-D-C-B-ORE
    # resulting in
    # [ [FUEL], [E], [D], [C], [A, B], [ORE] ]
    try:
        lists = []
        first_list = ['FUEL']
        lists += get_more_order(first_list, source_dict)

        lists = sorted(lists, key=lambda x: len(x), reverse=True)
        if DEBUG: print("Lists:", lists)
        unused_components = set(source_dict.keys())
        unused_components.add("ORE")

        longest = lists.pop(0)
        from_ore = []
        for component in longest[::-1]:  # Work back from ORE
            from_ore.append([component])
            unused_components.remove(component)

        for a_list in lists:
            for ix, component in enumerate(a_list[::-1]):
                if component in unused_components:
                    from_ore[ix].append(component)
                    unused_components.remove(component)
    except Exception as ex:
        import traceback; print(traceback.format_exc())
        import pdb; pdb.set_trace()
        raise

    if DEBUG: print("from_ore:", from_ore)

    # Return in order, starting from FUEL
    return from_ore[::-1]

def get_more_order(a_list, source_dict):
    new_lists = []
    ingredient = a_list[-1]
    _, components = source_dict[ingredient]

    for component in [component for _,component in components]:
        new_list = list(a_list) + [component]
        if component=="ORE":
            new_lists.append(new_list)
        else:
            new_lists += get_more_order(new_list, source_dict)

    return new_lists

# def ore_for_ingredient(ingredient, how_many, source_dict, known_recipes):
#     # This is wrong - it rounds up each time you want e.g. 7A->10, but instead we
#     # want to work out total A needed for everything, then map 28A -> 3*10

# 	# recursively find the ore needed to make the ingredients to make the ingredients to make ... &c
# 	# Handle the fact that some recipes make more than one output (eg. 1A + 2B = 5C)
# 	# Examples
# 	# 9 ORE => 2 A so A:(2,[(9,ORE)])
#     # 8 ORE => 3 B so B:(3,[(8,ORE)])
#     # 7 ORE => 5 C so C:(5,[(7,ORE)])
#     # 3 A, 4 B => 1 AB so AB:(1,[(3,A), (4,B)])
#     # Or (example 1)
#     # 10 ORE => 10 A so A:(10,[(10,ORE)])
#     # <...>
#     # 7 A, 1 E => 1 FUEL so FUEL:(1,[(7,A), (1,E)])
#     #import pdb; pdb.set_trace()
#     if ingredient=="ORE":
#         return how_many
#     elif (how_many, ingredient) in known_recipes:
#         return known_recipes[(how_many, ingredient)]

#     number, ingredients = source_dict[ingredient]  # e.g. 10, [(10,ORE)]

#     sum_ore = 0
#     for num, ing in ingredients:
#         ore = ore_for_ingredient(ing, num, source_dict, known_recipes)
#         sum_ore += ore

#     repeats = math.ceil(how_many / number)

#     ore_needed = sum_ore*repeats
#     if DEBUG: print(ore_needed, ingredient, how_many)
#     known_recipes[(how_many, ingredient)] = ore_needed
#     return ore_needed

def test_recipe(recipe, expected_ore):
    start = time.time()
    ore_needed = ore_for_recipe(recipe)
    if DEBUG or True: print("Test: {} vs {} - took {:.1f}s".format(ore_needed, expected_ore, time.time()-start))
    assert(ore_needed == expected_ore)

def tests():
    test_recipe("""10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 FUEL""", 11)

    test_recipe("""10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL""", 31)

    test_recipe("""9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL""", 165)

    test_recipe("""157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""", 13312)

    test_recipe("""2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF""", 180697)

    test_recipe("""171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX""", 2210736)

    part_one_recipe="""1 BNZK => 2 NMDF
3 KPQPD => 4 GSRWZ
2 ZRSFC => 7 SRGL
5 XNPDM, 1 FGCV => 7 HMTC
18 LHTNC, 1 WGXGV => 9 CDKF
24 BMQM => 5 FKHRJ
2 LFPNB => 6 XNSVC
9 ZKFRH, 4 XGPLN, 17 SPQP, 2 GVNTZ, 1 JMSCN, 9 SHQN, 1 DZLWC, 18 MSKQ => 7 TXDQK
2 QFTW => 9 JPZT
1 KJCK, 1 TFKZ, 2 XNSVC => 7 GQRB
16 JPZT, 3 DCPW => 7 KJCK
24 LGKPJ, 11 CDKF, 2 HVZQM => 7 RNXJ
1 NMDF, 16 DBLGK, 1 HVZQM => 7 ZKFRH
4 TXDQK, 55 TNZT, 39 KDTG, 6 NVBH, 15 SDVMB, 53 XVKHV, 28 FKHRJ => 1 FUEL
3 CDKV, 11 FGCV => 1 NVBH
3 SPNRW, 7 JMSCN => 9 XMCNV
14 FGCV, 3 CQLRM, 1 TFKZ => 6 PQVBV
5 KJCK, 10 DCPW => 7 DSKH
5 NMDF, 1 TFKZ => 5 DZLWC
1 TNZT => 6 RTSBT
178 ORE => 6 XVLBX
1 SPNRW => 5 CWKH
15 ZRSFC, 2 PQVBV, 2 SRGL => 3 SPNRW
1 SHQN, 7 XNSVC => 4 QWMZQ
5 NVBH, 41 SHQN => 4 BNZK
1 CDKV, 6 KJCK => 4 TNZT
5 ZTBG, 1 HVZQM, 27 CDKV, 1 LHTNC, 2 RTSBT, 2 SHQN, 26 DZLWC => 9 KDTG
11 CDKV => 7 SHQN
13 QWMZQ, 19 FCFG => 7 GVNTZ
1 SHQN, 4 XNSVC => 9 ZRSFC
2 ZKFRH, 9 HVZQM, 1 KJCK, 3 GQRB, 11 DBLGK, 8 DZLWC, 2 SPQP, 5 RNXJ => 8 SDVMB
5 SPNRW => 7 JMSCN
2 XVLBX, 19 KPQPD => 7 XNPDM
2 JPZT => 8 CDKV
1 GQRB => 7 MSKQ
1 SHQN, 13 DSKH => 3 MHQVS
9 JPZT => 8 LFPNB
15 SPNRW, 4 GQRB => 9 SPQP
1 JPZT => 3 TFKZ
1 BMQM => 6 FGCV
24 FKHRJ => 9 DCPW
2 GSRWZ => 8 XGPLN
5 QPSDR, 1 XVLBX => 6 BMQM
128 ORE => 7 QPSDR
2 LHTNC, 6 FCFG, 5 GVNTZ => 7 ZTBG
9 KJCK, 6 MHQVS, 5 NVBH => 6 KRDGK
3 HMTC, 4 QWMZQ => 2 FCFG
4 WGXGV, 5 PQVBV => 1 LGKPJ
42 XVLBX => 5 CQLRM
1 CWKH => 9 DBLGK
1 KRDGK, 2 GQRB, 12 TFKZ => 5 LHTNC
1 CQLRM, 1 HMTC => 8 WGXGV
116 ORE => 1 QFTW
13 XMCNV => 5 XVKHV
12 LGKPJ, 8 FKHRJ => 9 HVZQM
5 QPSDR => 6 KPQPD"""

    test_recipe(part_one_recipe, 198984)

    print("All tests passed")

tests()
