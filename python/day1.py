def fuel (mass):
    return max((mass//3) -2, 0)

assert(fuel(12) == 2)
assert(fuel(14) == 2)
assert(fuel(1969) == 654)
assert(fuel(100756) == 33583)
assert(fuel(9) == 1)
assert(fuel(6) == 0)
assert(fuel(4) == 0)
assert(fuel(1) == 0)
assert(fuel(-4) == 0)

def fuel_with_fuel (mass):
    extra = fuel(mass)
    #print(extra)
    return extra + fuel_with_fuel(extra) if extra > 0 else 0


assert(fuel_with_fuel(14) == 2)
assert(fuel_with_fuel(1969) == 966)
assert(fuel_with_fuel(100756) == 50346)

with open("day1.input", "r") as f:
    inputs = [int(x) for x in f.readlines()]
    fuel_one = sum([fuel(x) for x in inputs])
    fuel_for_modules = sum([fuel_with_fuel(x) for x in inputs])

print(fuel_one)
print(fuel_for_modules)
