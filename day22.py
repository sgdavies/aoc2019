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
        return self.deck

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

    log.critical("All tests passed")

def do_part_one(deck_size):
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
    
    deck = Deck(deck_size)
    deck.shuffle(puzzle_input)
    out = deck.order()
    log.debug(out)

    ix2019 = out.index(2019)
    assert(ix2019 == 7860)

if __name__ == "__main__":
    tests()

    print(10, 10007, timeit.timeit("do_part_one(10007)", setup="from __main__ import do_part_one", number=10))
    print(1, 119315717514047, timeit.timeit("do_part_one(119315717514047)", setup="from __main__ import do_part_one", number=1))
