import logging, pdb, timeit

logging.basicConfig()
log = logging.getLogger()

class Deck():
    def __init__(self, size):
        self.size = size
        self.deck = list(range(size))

    def shuffle(self, instructions):
        for instruction in instructions.split('\n'):
            self.do_instruction(instruction)

    def do_instruction(self, instruction):
        if instruction == "deal into new stack":
            self.deck = self.deck[::-1]
        elif instruction.startswith("cut "):
            self._cut(int(instruction[4:]))
        elif instruction.startswith("deal with increment "):
            self._deal_with_increment(int(instruction[len("deal with increment "):]))
        else:
            log.critical("Didn't understand instruction: '{}'".format(instruction))
            assert(False)

    def _cut(self, N):
        self.deck = self.deck[N:] + self.deck[:N]

    def _deal_with_increment(self, N):
        out = ['x']*self.size
        ix = 0
        while self.deck:
            out[ix] = self.deck.pop(0)
            ix += N
            ix %= self.size

        self.deck = out
        
    def order(self):
        return [self.card_at(i) for i in range(self.size)]

    def card_at(self, index):
        return self.deck[index]

def test(deck_size, instructions, answer):
    deck = Deck(10)
    deck.shuffle(instructions)

    log.debug(deck.order())
    assert(" ".join([str(i) for i in deck.order()]) == answer)

def tests():
    # log.setLevel(logging.DEBUG)
    test(10, "deal into new stack", "9 8 7 6 5 4 3 2 1 0")
    test(10, "cut 3", "3 4 5 6 7 8 9 0 1 2")
    test(10, "cut -4", "6 7 8 9 0 1 2 3 4 5")
    test(10, "deal with increment 3", "0 7 4 1 8 5 2 9 6 3")

    example_one = """deal with increment 7
deal into new stack
deal into new stack"""

    test(10, example_one, "0 3 6 9 2 5 8 1 4 7")

    example_two = """cut 6
deal with increment 7
deal into new stack"""
    test(10, example_two, "3 0 7 4 1 8 5 2 9 6")

    example_three = """deal with increment 7
deal with increment 9
cut -2"""
    test(10, example_three, "6 3 0 7 4 1 8 5 2 9")

    example_four = """deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1"""
    test(10, example_four, "9 2 5 8 1 4 7 0 3 6")

    do_part_one()

    log.critical("All tests passed")

puzzle_input = """deal with increment 31
deal into new stack
cut -7558
deal with increment 49
cut 194
deal with increment 23
cut -4891
deal with increment 53
cut 5938
deal with increment 61
cut 7454
deal into new stack
deal with increment 31
cut 3138
deal with increment 53
cut 3553
deal with increment 61
cut -5824
deal with increment 42
cut -889
deal with increment 34
cut 7128
deal with increment 42
cut -9003
deal with increment 75
cut 13
deal with increment 75
cut -3065
deal with increment 74
cut -8156
deal with increment 39
cut 4242
deal with increment 24
cut -405
deal with increment 27
cut 6273
deal with increment 19
cut -9826
deal with increment 58
deal into new stack
cut -6927
deal with increment 65
cut -9906
deal with increment 31
deal into new stack
deal with increment 42
deal into new stack
deal with increment 39
cut -4271
deal into new stack
deal with increment 32
cut -8799
deal with increment 69
cut 2277
deal with increment 55
cut 2871
deal with increment 54
cut -2118
deal with increment 15
cut 1529
deal with increment 57
cut -4745
deal with increment 23
cut -5959
deal with increment 58
deal into new stack
deal with increment 48
deal into new stack
cut 2501
deal into new stack
deal with increment 42
deal into new stack
cut 831
deal with increment 74
cut -3119
deal with increment 33
cut 967
deal with increment 69
cut 9191
deal with increment 9
cut 5489
deal with increment 62
cut -9107
deal with increment 14
cut -7717
deal with increment 56
cut 7900
deal with increment 49
cut 631
deal with increment 14
deal into new stack
deal with increment 58
cut -9978
deal with increment 48
deal into new stack
deal with increment 66
cut -1554
deal into new stack
cut 897
deal with increment 36"""

def do_part_one():
    deck = Deck(10007)
    deck.shuffle(puzzle_input)
    
    assert(deck.card_at(7860) == 2019)

if __name__ == "__main__":
    tests()


# With a bigger deck - don't want to calculate the whole thing. Cut down to calculating only the card a position X.
# 'deal into new stack' just means reverse deck. X -> size-X -- and direction = reverse
# 'cut' is a rotation.  X -> X + c is forwards, or X -> X - c if reverse
# example
# cut 3, deal into stack, cut -4
# 0123456789
# 3456789012 cut 3
# 2109876543 deal into stack
# 6543210987 cut -4
# 5432109876 cut 1

# toggling +/- at each deal, ends up with: index from start, +1510 (+336 mod 587)
inn = """deal into new stack
cut -75
cut 194
cut -489
cut 59
cut 74
deal into new stack
cut 313
deal into new stack
cut 355
cut -58
cut -88
deal into new stack
cut 71
deal into new stack
cut -90
cut 13
cut -306
deal into new stack
cut -81
cut 424
deal into new stack
cut -405
cut 62
cut -98
deal into new stack
cut -69"""

deck = Deck(587)
deck.shuffle(inn)
out = deck.order()

# index from start, +336 (mod 587)
print(out[:20])   # 336, 337, ..., 355
print(out[-20:])  # 316, 317, ..., 334, 335
print(out[400])   # 149
assert(out[400] == (400+336)%587)

# So: for only cut & deal onto stack:
# 1. Sum all cuts; +ve if forward (even number of stack deals have happened), -ve if reverse (after odd number of stack deals)
# 2. Answer is (i +sum) % size if forwards, or (size -1 -i) % size if backwards.
#
# Now to handle deal with increment.
# 0123456789 (10)
# (no 2, 4, 6, 8 or 5)
# 0741852963 dwi 3 == 7*i mod 10 (10,3)->7
# 0369258147 dwi 7 == 3*i mod 10 (10,7)->3
#
# 0123456 (7)
# 0415263 dwi 2  7,2 -> 4
# 0531642 dwi 3  7,3 -> 5
# 0246135 dwi 4  7,4 -> 2
# 0362514 dwi 5  7,5 -> 3
# 
# 0 1 2 3 4 5 6 7 8 9 101112 (13)
# 0 7 1 8 2 9 3 104 115 126  13,2 - 7
# 0 9 5 1 106 2 117 3 128 4  13,3 - 9
# 0 107 4 1 118 5 2 129 6 3  13,4 - 10
# 0 8 3 116 1 9 4 127 2 105  13,5 - 8
# 0 119 7 5 3 1 12108 6 4 2  13,6 - 11
# 0 2           1            13,7 - 2
# 0 5   2     4   1     3    13,8 - 5
# 0 3       2       1        13,9 - 3
# 0 4     3     2     1      13,10- 4
# 0 6   5   4   3   2   1    13,11- 6
# 0                       1  13,12- 12
#
# 012345678 (9)
# 051627384 dwi 2  9,2 -> 5
# (dwi 3 - doesn't work)
# 075318642 dwi 4  9,4 -> 7
# 024681357 dwi 5  9,5 -> 2
# (dwi 6 - doesn't work)
# 048372615 dwi 7  9,7 -> 4
# 087654321 dwi 8  9,8 -> 8
#
# 01234 (5)
# 01234 dwi 1  X,1 -> 1
# 03142 dwi 2 (3*i) 5,2 ->3
# 02413 dwi 3  5,3 -> 2
# 04321 dwi 4  5,4 -> 4
#
# x*i %N = 1
