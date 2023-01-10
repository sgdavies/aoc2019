
class Program:
    def __init__ (self, initial_memory_state):
        self.memory = initial_memory_state
        self.ip = 0

    def execute(self):
        instr = self.get(self.ip)
        self.ip +=1

        if instr == 1:
            val = self.get(self.get(self.ip)) + self.get(self.get(self.ip+1))
            self.store(val, self.get(self.ip+2))
            self.ip += 3
            ret = True
        elif instr == 2:
            val = self.get(self.get(self.ip)) * self.get(self.get(self.ip+1))
            self.store(val, self.get(self.ip+2))
            self.ip += 3
            ret = True
        elif instr == 99:
            ret = False

        return ret

    def store (self, val, loc):
        if loc >= len(self.memory):
            print("Store outside memory buffer: {} with memory of length {}".format(loc, len(self.memory)))
            exit(1)

        self.memory[loc] = val

    def get (self, ix):
        return self.memory[ix]

    def set (self, ix, val):
        self.memory[ix] = val

    def run(self):
        while self.execute():
            #self.display(debug=True)
            pass

    def display(self, debug=False):
        print(self.memory)
        if debug:
            print(self.ip)
            print()

    def test(self, answer=None):
        self.run()
        if answer and not self.memory == answer:
            print("Values not equal:\n{}\n{}".format(self.memory, answer))
            assert(False)



Program([1,0,0,0,99]).test([2,0,0,0,99])
Program([2,3,0,3,99]).test([2,3,0,6,99])
Program([2,4,4,5,99,0]).test([2,4,4,5,99,9801])
Program([1,1,1,4,99, 5,6,0,99]).test([30,1,1,4,2,5,6,0,99])
print("All tests passed")

#program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])
program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,13,1,19,1,19,10,23,2,10,23,27,1,27,6,31,1,13,31,35,1,13,35,39,1,39,10,43,2,43,13,47,1,47,9,51,2,51,13,55,1,5,55,59,2,59,9,63,1,13,63,67,2,13,67,71,1,71,5,75,2,75,13,79,1,79,6,83,1,83,5,87,2,87,6,91,1,5,91,95,1,95,13,99,2,99,6,103,1,5,103,107,1,107,9,111,2,6,111,115,1,5,115,119,1,119,2,123,1,6,123,0,99,2,14,0,0])

program.set(1,12)
program.set(2,2)

program.run()
print(program.get(0))

for noun in range(100):
    for verb in range(100):
        #program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])
        program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,13,1,19,1,19,10,23,2,10,23,27,1,27,6,31,1,13,31,35,1,13,35,39,1,39,10,43,2,43,13,47,1,47,9,51,2,51,13,55,1,5,55,59,2,59,9,63,1,13,63,67,2,13,67,71,1,71,5,75,2,75,13,79,1,79,6,83,1,83,5,87,2,87,6,91,1,5,91,95,1,95,13,99,2,99,6,103,1,5,103,107,1,107,9,111,2,6,111,115,1,5,115,119,1,119,2,123,1,6,123,0,99,2,14,0,0])
        program.set(1, noun)
        program.set(2, verb)

        program.run()

        if program.get(0) == 19690720:
            print(noun, verb, str(noun)+str(verb))
            exit(0)

