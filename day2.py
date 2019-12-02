
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
        print self.program

    def test(self, answer=None):
        print(self.program)
        self.run()
        print(self.program)
        if answer: assert(self.program == answer)
        print



Program([1,0,0,0,99]).test([2,0,0,0,99])
Program([2,3,0,3,99]).test([2,3,0,6,99])
Program([2,4,4,5,99,0]).test([2,4,4,5,99,9801])
Program([1,1,1,4,99, 5,6,0,99]).test([30,1,1,4,2,5,6,0,99])
print("All tests passed")

program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])

program.set(1,12)
program.set(2,2)

program.run()
print program.get(0)


