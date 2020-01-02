import logging, pdb, timeit

logging.basicConfig()
log = logging.getLogger()

class Deck():
    def __init__(self, size, debug=False):
        self.size = size
        self.debug = debug

        if self.debug:
            self.deck = list(range(size))

        self.x_for_i = {}
        self.funs = []
        def identity(x): return x
        self.funs.append(identity)

    def shuffle(self, instructions):
        for instruction in instructions.split('\n'):
            self.do_instruction(instruction)

    def do_instruction(self, instruction):
        if instruction == "deal into new stack":
            if self.debug:
                self.deck = self.deck[::-1]

            last_f = self.funs[-1]
            def f(x): return last_f(self.size-1-x)
            self.funs.append(f)

        elif instruction.startswith("cut "):
            cut_len = int(instruction[4:])

            if self.debug:
                self._cut(cut_len)

            last_f = self.funs[-1]
            def f(x): return last_f(x+cut_len)
            self.funs.append(f)

        elif instruction.startswith("deal with increment "):
            increment = int(instruction[len("deal with increment "):])

            if self.debug:
                self._deal_with_increment(increment)

            last_f = self.funs[-1]
            def f(x): return last_f(x*self.get_x_for_i(increment))
            self.funs.append(f)

        else:
            log.critical("Didn't understand instruction: '{}'".format(instruction))
            assert(False)

    def get_x_for_i(self, increment):
        if increment not in self.x_for_i:
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

            #x = 1
            #while x < self.size:
            #    if (x*increment)%self.size == 1:
            #        self.x_for_i[x] = increment
            #        self.x_for_i[increment] = x
            #        log.debug("x-for-i: {},{}".format(increment, x))
            #        break
            #    x += 1

        return self.x_for_i[increment]

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
        assert(self.debug), "Can't show whole deck for large deck"
        return [self.card_at(i) for i in range(self.size)]

    def card_at(self, index):
        if self.debug:
            assert(self.card_at_fun(index) == self.deck[index])
        return self.card_at_fun(index)

    def card_at_fun(self, index):
        answer = self.funs[-1](index)
        answer = answer % self.size
        return answer

def test(deck_size, instructions, answer, debug=False):
    deck = Deck(10, debug=debug)
    deck.shuffle(instructions)

    log.debug(deck.order())
    assert(" ".join([str(i) for i in deck.order()]) == answer)

def tests():
    #log.setLevel(logging.DEBUG)
    test(10, "deal into new stack", "9 8 7 6 5 4 3 2 1 0", debug=True)
    test(10, "cut 3", "3 4 5 6 7 8 9 0 1 2", debug=True)
    test(10, "cut -4", "6 7 8 9 0 1 2 3 4 5", debug=True)
    test(10, "deal with increment 3", "0 7 4 1 8 5 2 9 6 3", debug=True)

    example_one = """deal with increment 7
deal into new stack
deal into new stack"""

    test(10, example_one, "0 3 6 9 2 5 8 1 4 7", debug=True)

    example_two = """cut 6
deal with increment 7
deal into new stack"""
    test(10, example_two, "3 0 7 4 1 8 5 2 9 6", debug=True)

    example_three = """deal with increment 7
deal with increment 9
cut -2"""
    test(10, example_three, "6 3 0 7 4 1 8 5 2 9", debug=True)

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
    test(10, example_four, "9 2 5 8 1 4 7 0 3 6", debug=True)

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
    deck = Deck(10007, debug=True)
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

deck = Deck(587, debug=True)
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
inn = """deal with increment 5
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
deck = Deck(13, debug=True)
print(" ".join([str(x) for x in deck.order()]))
for ins in inn.split('\n'):
    deck.shuffle(ins)
    print("{:25} {}".format(ins, " ".join([str(x) for x in deck.order()])))

print("Done")



import sys, time

deck = Deck(119315717514047)
# Seed the factors
#for x in [9, 14, 15, 19, 23, 24, 27, 31, 32, 33, 34, 36, 39, 42, 48, 49, 53, 54, 55, 56, 57, 58, 61, 62, 65, 66, 69, 74, 75]:
#    log.debug("Seeding", x); sys.stdout.flush()
#    log.debug(deck.get_x_for_i(x))

print("Starting shuffle on big deck"); sys.stdout.flush()

for i in range(10):
    start = time.time()
    deck.shuffle(puzzle_input)
    print("{} (took {:.1f}s)".format(deck.card_at(2020), time.time())); sys.stdout.flush()

print("Done")







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

# Unique instructions in puzzle input:
# deal into new stack
# cut -1554
# cut -2118
# cut -3065
# cut -3119
# cut -405
# cut -4271
# cut -4745
# cut -4891
# cut -5824
# cut -5959
# cut -6927
# cut -7558
# cut -7717
# cut -8156
# cut -8799
# cut -889
# cut -9003
# cut -9107
# cut -9826
# cut -9906
# cut -9978
# cut 13
# cut 1529
# cut 194
# cut 2277
# cut 2501
# cut 2871
# cut 3138
# cut 3553
# cut 4242
# cut 5489
# cut 5938
# cut 6273
# cut 631
# cut 7128
# cut 7454
# cut 7900
# cut 831
# cut 897
# cut 9191
# cut 967
# deal with increment 9
# deal with increment 14
# deal with increment 15
# deal with increment 19
# deal with increment 23
# deal with increment 24
# deal with increment 27
# deal with increment 31
# deal with increment 32
# deal with increment 33
# deal with increment 34
# deal with increment 36
# deal with increment 39
# deal with increment 42
# deal with increment 48
# deal with increment 49
# deal with increment 53
# deal with increment 54
# deal with increment 55
# deal with increment 56
# deal with increment 57
# deal with increment 58
# deal with increment 61
# deal with increment 62
# deal with increment 65
# deal with increment 66
# deal with increment 69
# deal with increment 74
# deal with increment 75



