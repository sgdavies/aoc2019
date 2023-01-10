
class Program:
    def __init__ (self, program):
        self.program = program

    def execute (self, instr, a, b):
        if instr == 1:
            return self.get(a) + self.get(b)
        elif instr == 2:
            return self.get(a) * self.get(b)
        else:
            print("Unknown instruction: {}".format(instr))
            exit(1)

    def store (self, val, loc):
        if loc >= len(self.program):
            print("Store outside program buffer: {} with program of length {}".format(loc, len(self.program)))
            exit(1)

        self.program[loc] = val

    def get (self, ix):
        return self.program[ix]

    def set (self, ix, val):
        self.program[ix] = val

    def run(self):
        for ix in range(0, len(self.program), 4):
            instr = self.get(ix)

            if instr == 99:
                break

            else:
                self.store(self.execute(instr, self.get(ix+1), self.get(ix+2)), self.get(ix+3))

    def display(self):
        print(self.program)

    def test(self, answer=None):
        print(self.program)
        self.run()
        print(self.program)
        if answer: assert(self.program == answer)
        print()



Program([1,0,0,0,99]).test([2,0,0,0,99])
Program([2,3,0,3,99]).test([2,3,0,6,99])
Program([2,4,4,5,99,0]).test([2,4,4,5,99,9801])
Program([1,1,1,4,99, 5,6,0,99]).test([30,1,1,4,2,5,6,0,99])
print("All tests passed")

program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,13,1,19,1,19,10,23,2,10,23,27,1,27,6,31,1,13,31,35,1,13,35,39,1,39,10,43,2,43,13,47,1,47,9,51,2,51,13,55,1,5,55,59,2,59,9,63,1,13,63,67,2,13,67,71,1,71,5,75,2,75,13,79,1,79,6,83,1,83,5,87,2,87,6,91,1,5,91,95,1,95,13,99,2,99,6,103,1,5,103,107,1,107,9,111,2,6,111,115,1,5,115,119,1,119,2,123,1,6,123,0,99,2,14,0,0])

program.set(1,12)
program.set(2,2)

program.run()
print(program.get(0))


