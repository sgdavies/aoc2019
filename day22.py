import logging, pdb, timeit
import sys, time

logging.basicConfig()
log = logging.getLogger()

class Deck():
    def __init__(self, size, instructions):
        self.size = size
        self._prepare_shuffle(instructions)

    def _prepare_shuffle(self, instructions):
        self.x_for_i = {}
        self.a = 1
        self.b = 0

        self.shuffles = 0
        self.calculated_at = 0

        backwards_instructions = instructions.split('\n')
        backwards_instructions.reverse()
        for instruction in backwards_instructions:
            self.do_instruction(instruction)

    def shuffle(self):
        self.shuffles += 1

    def do_instruction(self, instruction):
        if instruction == "deal into new stack":
            # x' = (size-1) - x
            # => a'i+b' = -(ai+b) + (size-1)
            # => a' = -a, b' = -b + size-1
            self.a = -self.a
            self.b = (self.size - 1) - self.b

        elif instruction.startswith("cut "):
            cut_len = int(instruction[4:])
            # x' = x + c
            # a'i + b' = a.i + b+c
            self.b += cut_len

        elif instruction.startswith("deal with increment "):
            increment = int(instruction[len("deal with increment "):])
            complement = self.get_x_for_i(increment)
            # x' = c.x
            # a'i + b' = ca.i + cb
            self.a *= complement
            self.b *= complement

        else:
            log.critical("Didn't understand instruction: '{}'".format(instruction))
            assert(False)

    def get_x_for_i(self, increment):
        if increment not in self.x_for_i:
            # Find x for Ax = 1 mod N
            def inverse(a, n):
                # https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
                t=0; newt=1; r=n; newr=a

                while newr != 0:
                    quot = r // newr
                    t, newt = newt, t - (quot*newt)
                    r, newr = newr, r - (quot*newr)

                if r > 1:
                    assert(False), "{} is not invertible in {}".format(a, n)

                if t < 0:
                    t = t + n

                return t

            x = inverse(increment, self.size)
            self.x_for_i[x] = increment
            self.x_for_i[increment] = x

        return self.x_for_i[increment]

    def card_at(self, index):
        if self.calculated_at != self.shuffles:
            self._calculate()
            self.calculated_at = self.shuffles
        ans = (index*self.a + self.b) % self.size

        if log.level <= logging.DEBUG:
            import math
            a_len = int(math.log(self.a, 10)) if self.a>0 else 1
            if a_len < 100:
                log.debug("a: {}  b: {}  index: {}  value: {}".format(self.a, self.b, index, ans))
            else:
                b_len = int(math.log(self.b, 10)) if self.b>0 else 1
                log.debug("a: {} digits, b: {} digits.  index: {}  value: {}".format(a_len, b_len, index, ans))
        return ans

    def _calculate(self):
        if self.shuffles==1:
            # Easy case. Should fall out of the below as well, actually.
            self.calculated_at = 1
            return

        # Define a load of helper functions to see where the time is going (profiling)
        def reduce_a(aa):
            while aa % (self.size+1) == 0:
                aa //= (self.size+1)
            return aa

        def reduce_b(bb):
            return (bb) % self.size

        def next_cur_a(aa):
            return reduce_a(aa*aa)

        def next_cur_b(aa, bb):
            return reduce_b(bb*(aa+1))

        def next_final_a(fa, ca):
            return reduce_a(fa*ca)

        def next_final_b(fa, fb, cb):
            return reduce_b(fa*cb + fb)

        s1=0
        s2=0
        cur_a = self.a
        cur_b = self.b
        final_a = 1
        final_b = 0
        pos = 1
        while pos <= self.shuffles:
            # 
            s1+=1
            if pos & self.shuffles:
                s2+=1
                # m = prev value (final_), n = next (cur_)
                # a{n+m} = a{n} + a{m}
                # b{n+m} = a{m}.b{n} + b{m}
                final_b = next_final_b(final_a, final_b, cur_b) # reduce_b(final_a*cur_b + final_b)
                final_a = next_final_a(final_a, cur_a)          # reduce_a(final_a*cur_a)

            # calc the next a and b
            cur_b = next_cur_b(cur_a, cur_b)    # reduce_b(cur_b*(cur_a + 1))
            cur_a = next_cur_a(cur_a)           # reduce_a(cur_a*cur_a)

            pos *= 2

        self.a = final_a
        self.b = final_b
        print("{} shuffles: {} steps and {} calcs".format(self.shuffles, s1, s2))


class SimpleDeck(Deck):
    def _prepare_shuffle(self, instructions):
        self.instructions = instructions
        self.deck = list(range(self.size))

    def shuffle(self):
        for instruction in self.instructions.split('\n'):
            self.do_instruction(instruction)

    def do_instruction(self, instruction):
        if instruction == "deal into new stack":
            self.deck = self.deck[::-1]

        elif instruction.startswith("cut "):
            cut_len = int(instruction[4:])
            self._cut(cut_len)

        elif instruction.startswith("deal with increment "):
            increment = int(instruction[len("deal with increment "):])
            self._deal_with_increment(increment)

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
    deck = SimpleDeck(10, instructions)
    deck.shuffle()

    log.debug(deck.order())
    assert(" ".join([str(i) for i in deck.order()]) == answer)

    deck = Deck(10, instructions)
    deck.shuffle()
    assert(" ".join([str(deck.card_at(i)) for i in range(10)]) == answer)


inn13 = """deal with increment 5
deal with increment 2
cut -4
deal with increment 4
cut 12
deal with increment 7
deal with increment 8
cut -7
cut -12
deal with increment 2
deal into new stack
deal with increment 5
deal with increment 4
deal into new stack
deal with increment 7
deal into new stack
cut 5
deal with increment 8
deal with increment 7"""

def tests():
    # log.setLevel(logging.DEBUG)
    test(10, "deal into new stack", "9 8 7 6 5 4 3 2 1 0")
    test(10, "cut 3", "3 4 5 6 7 8 9 0 1 2")
    test(10, "cut -4", "6 7 8 9 0 1 2 3 4 5")
    test(10, "deal with increment 3", "0 7 4 1 8 5 2 9 6 3")

    test(10, "deal into new stack\ndeal into new stack", "0 1 2 3 4 5 6 7 8 9")

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

    # Repeated shuffling
    # How do a/b change after repeated invocations?
    # log.setLevel(logging.DEBUG)
    N=107
    log.debug("Doing {} shuffles".format(N))
    deck = Deck(13, inn13)
    simple_deck = SimpleDeck(13, inn13)
    for rep in range(N):
        deck.shuffle()
        simple_deck.shuffle()

    simple_deck_answer = " ".join([str(simple_deck.card_at(x)) for x in range(13)])
    log.debug(simple_deck_answer)
    deck_answer = " ".join([str(deck.card_at(x)) for x in range(13)])
    log.debug(deck_answer)
    log.debug("{}, {}".format(deck.a, deck.b))
    assert(deck_answer == simple_deck_answer), "Decks not equal after shuffling"

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
    deck = SimpleDeck(10007, puzzle_input)
    deck.shuffle()

    assert(deck.card_at(7860) == 2019)

    deck = Deck(10007, puzzle_input)
    deck.shuffle()

    assert(deck.card_at(7860) == 2019)

if __name__ == "__main__":
    tests()


# With a bigger deck - don't want to calculate the whole thing. Cut down to
# calculating only the card a position X.
#
# So: for only cut & deal onto stack:
# 1. Sum all cuts; +ve if forward (even number of stack deals have happened), -ve if reverse (after odd number of stack deals)
# 2. Answer is (i +sum) % size if forwards, or (size -1 -i) % size if backwards.
#
# Now to handle deal with increment A.
# See details below - net is:
# Card at index i is Xi mod N, for some value of X [while facing forward]
#
# Examples (deck 7)
# 0123456
# 0415263 dwi 2 (X=4) 0>0, 1>4, 2>8=1, 3>12=5, 4>16=2, 5>20=6, 6>24=3
# 0654321 dwi 3 (X=5) 0>0, 1>5, 2>10=3, 3>15=1, 4>20=6, 5>25=4, 6>30=2
#
# To solve:
# 1- what's the effect of dwi A + dwi B?
# 2- what's the effect of dwi X after cut?
# 3- what's the effect of dwi X after reverse?
# 4- what's the combined effect of all the above?
#
# 0123456
# 0415263 dwi 2 (x=4)
# 0246135 dwi 2 again
#
# 1. dwi A, dwi B?
#    dwi A,B = i(X*Y)%N
#
# 2. cut A then dwi B?
# 0123456
# 2345601 cut 2 x=i+c =i+2
# 2630415 dwi 2 (X=4)  x=(Xi+c)%N =(4i+2)%7
# 4152630 cut 4 (or 6304152 cut 1, 3041526 cut 2, 0415263 cut 3 etc)
#           X(i+c2)+c1 = X(i+4) +2
# 4321065 dwi 3 (X=5)  x1(x2*i+c2)+c1

# Deck of 13
#                       0:  0 1 2 3 4 5 6 7 8 9 10 11 12
# deal with increment 5 1:  0 8 3 11 6 1 9 4 12 7 2 10 5  x1=8    a=x1.i = 8i
# deal with increment 2 2:  0 4 8 12 3 7 11 2 6 10 1 5 9  x2=7    a=x1.x2.i = 56i
# cut -4                3:  10 1 5 9 0 4 8 12 3 7 11 2 6  c3=-4   a=x1.x2.(i+c3) = 56(i-4)
# deal with increment 4 4:  10 11 12 0 1 2 3 4 5 6 7 8 9  x4=10   a=x1.x2.(x4.i+c3)
# cut 12                5:  9 10 11 12 0 1 2 3 4 5 6 7 8  c5=12
# deal with increment 7 6:  9 11 0 2 4 6 8 10 12 1 3 5 7  x6=2
# deal with increment 8 7:  9 6 3 0 10 7 4 1 11 8 5 2 12  x7=5
# cut -7                8:  4 1 11 8 5 2 12 9 6 3 0 10 7  c8=-7
# cut -12               9:  1 11 8 5 2 12 9 6 3 0 10 7 4  c9=-12
# deal with increment 2 10: 1 6 11 3 8 0 5 10 2 7 12 4 9  x10=7  a=x1.x2.(x4.(x6.x7.(x10.i+c9+c8)+c5)+c3)
# deal into new stack   11: 9 4 12 7 2 10 5 0 8 3 11 6 1  ****   a=f11(x)=f10(12-x)
# deal with increment 5 12: 9 8 7 6 5 4 3 2 1 0 12 11 10  x12=8
# deal with increment 4 13: 9 12 2 5 8 11 1 4 7 10 0 3 6  x13=10 a=f13(x)=f12(10*x)
# deal into new stack   14: 6 3 0 10 7 4 1 11 8 5 2 12 9  ****  f14=f13(12-x)
# deal with increment 7 15: 6 0 7 1 8 2 9 3 10 4 11 5 12  x15=2
# deal into new stack   16: 12 5 11 4 10 3 9 2 8 1 7 0 6  ****
# cut 5                 17: 3 9 2 8 1 7 0 6 12 5 11 4 10  c17=5
# deal with increment 8 18: 3 7 11 2 6 10 1 5 9 0 4 8 12  x18=5
# deal with increment 7 19: 3 11 6 1 9 4 12 7 2 10 5 0 8  x19=2

deck = SimpleDeck(13, None)
log.debug(" ".join([str(x) for x in deck.order()]))
for ins in inn13.split('\n'):
    deck.do_instruction(ins)
    log.debug("{:25} {}".format(ins, " ".join([str(x) for x in deck.order()])))


# Part Two
#
# Trial: shorter deck.
# Repeats after 10006 shuffles.  This suggests that if we could shuffle
# 'backwards' we could get there faster? (Assumes this is always a perfect
# shuffle on any deck)
# size=10007
# deck = Deck(size, puzzle_input)
# for i in range(size):
#     deck.shuffle()

# print(deck.card_at(7860))

#    101741582076661 times in a row
REPS=10
deck = Deck(119315717514047, puzzle_input)

print("Starting shuffle on big deck"); sys.stdout.flush()
start = time.time()
for i in range(REPS):
    deck.shuffle()

final_card = deck.card_at(2020)
end = time.time()
print("Done {} in {:.1f}s - {}".format(REPS, end-start, final_card))

print("Done")

def solve_puzzle(number_of_shuffles):
    #    101741582076661 times in a row
    deck = Deck(119315717514047, puzzle_input)
    REPS = number_of_shuffles
    deck.shuffles = REPS
    start = time.time()
    final_card = deck.card_at(2020)
    print("Done {} in {:.1f}s - {}".format(REPS, time.time()-start, final_card))

import cProfile
REPS=4000
if True:
    cProfile.run("solve_puzzle(REPS)", sort="cumulative")
else:
    solve_puzzle(REPS)


# Need to map from inc->X
# A,B pairs such that A*B = 1 mod N
#
#
# (i=0 always stays in the same place; N=length of deck)
# How to figure out X??
#
# Each X pairs with A - i.e. X = f(N,A) => A = f(N,X)
#
# 0123456789 (10)
# (no 2, 4, 6, 8 or 5)
# 0741852963 dwi 3 == 7*i mod 10 (10,3)->7
# 0369258147 dwi 7 == 3*i mod 10 (10,7)->3
# 0987654321 dwi 9 == 9*i mod 10 (10,9)->9
# So 10->3,7
#
# 0123456 (7)
# 0415263 dwi 2  7,2 -> 4
# 0531642 dwi 3  7,3 -> 5
# 0246135 dwi 4  7,4 -> 2
# 0362514 dwi 5  7,5 -> 3
# 7->2,4, 3,5
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
# 13 -> 2,7, 3,9, 4,10, 5-8, 6,11
# AX = 1modN
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
