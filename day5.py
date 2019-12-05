
class Program:
    def __init__ (self, initial_memory_state, inputs=[]):
        self.memory = initial_memory_state
        self.ip = 0
        self.inputs = inputs
        self.output_buffer = ""

    def execute(self):
        # Execute the instruction
        # returns True if the program should continue, or False if it should stop
        ret = True

        instr, params = self.decode(self.get(self.ip))
        self.ip += 1 + len(params)  # Ready for next instruction

        if instr == 1:
            val = params[0] + params[1]
            self.store(val, params[2])
        elif instr == 2:
            val = params[0] * params[1]
            self.store(val, params[2])
        elif instr == 3:
            # Input
            self.store(self.inputs.pop(0), params[0])
        elif instr == 4:
            # Output
            if len(self.output_buffer) > 0: self.output_buffer += " "
            self.output_buffer += str(params[0])
        elif instr == 99:
            ret = False

        return ret

    def decode (self, instruction):
        # Instruction is ...edcbA, where
        #  - A is the opcode
        #  - b, c, d, ... are the parameter modes for A's parameters
        #  The exception is special code 99
        if instruction == 99:
            return instruction, []


        opcode, modes = self._decode_detail(instruction)

        if opcode == 1 or opcode == 2:
            # Add or multiply - process 2 params and store at 3rd
            # Three parameters, starting from the next position after the ip
            p1 = self.get(self.ip+1)
            p2 = self.get(self.ip+2)
            p3 = self.get(self.ip+3)

            p1 = self._maybe_deref(p1, modes.pop(0) if modes else 0)
            p2 = self._maybe_deref(p2, modes.pop(0) if modes else 0)
            # p3 is the storage location, which is always returned as an address

            #m1 = modes.pop(0) if modes else 0  # Handles list being empty
            #m2 = modes.pop(0) if modes else 0
            #if m1 == 0: p1 = self.get(p1)  # 0=position mode - derefence
            #if m2 == 0: p2 = self.get(p2)

            params = (p1, p2, p3)

        elif opcode == 3 or opcode == 4:
            # Input or output
            p1 = self.get(self.ip+1)

            if opcode == 4:
                # Output might read immediate or from memory
                assert(len(modes) < 2)  # There should be at most 1 param here
                p1 = self._maybe_deref(p1, modes.pop(0) if modes else 0)

            params = (p1,)
        else:
            print "Invalid instruction:", opcode, instruction, self.memory
            assert(False)

        return opcode, params

    def _maybe_deref (self, param, mode):
        if mode == 0:
            return self.get(param)
        else:
            return param

    def _decode_detail (self, instruction):
        opcode = instruction % 100  # 2-digit opcode
        instruction /= 100

        modes = []
        while instruction > 0:
            modes.append(instruction % 10)
            instruction /= 10

        #print "\t", opcode, modes
        return opcode, modes

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

        if self.output_buffer:
            print "Output:", self.output_buffer

    def display(self, debug=False):
        print self.memory
        if debug:
            print self.ip
            print

    def test(self, answer=None):
        self.run()
        if answer and not self.memory == answer:
            print("Values not equal:\n{}\n{}".format(self.memory, answer))
            assert(False)


def tests ():
    dummy = Program([0])
    val = dummy._decode_detail(30201); #print val
    assert (val == (1, [2,0,3]))  # param mode should never be 2! but this checks the order is correct

    Program([1,0,0,0,99]).test([2,0,0,0,99])
    Program([2,3,0,3,99]).test([2,3,0,6,99])
    Program([2,4,4,5,99,0]).test([2,4,4,5,99,9801])
    Program([1,1,1,4,99, 5,6,0,99]).test([30,1,1,4,2,5,6,0,99])

    program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])
    program.set(1,12)
    program.set(2,2)
    program.run()
    print program.get(0)
    assert(program.get(0) == 3562624)

    Program([1002,4,3,4,33]).test([1002,4,3,4,99])
    Program([1101,100,-1,4,0]).test([1101,100,-1,4,99])

    p = Program([3,1,4,1,99], inputs=[77])
    p.test([3,77,4,1,99])
    assert(p.output_buffer == "77")

    print("All tests passed")

tests()

puzzle_day5_1 = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,82,10,225,101,94,44,224,101,-165,224,224,4,224,1002,223,8,223,101,3,224,224,1,224,223,223,1102,35,77,225,1102,28,71,225,1102,16,36,225,102,51,196,224,101,-3468,224,224,4,224,102,8,223,223,1001,224,7,224,1,223,224,223,1001,48,21,224,101,-57,224,224,4,224,1002,223,8,223,101,6,224,224,1,223,224,223,2,188,40,224,1001,224,-5390,224,4,224,1002,223,8,223,101,2,224,224,1,224,223,223,1101,9,32,224,101,-41,224,224,4,224,1002,223,8,223,1001,224,2,224,1,223,224,223,1102,66,70,225,1002,191,28,224,101,-868,224,224,4,224,102,8,223,223,101,5,224,224,1,224,223,223,1,14,140,224,101,-80,224,224,4,224,1002,223,8,223,101,2,224,224,1,224,223,223,1102,79,70,225,1101,31,65,225,1101,11,68,225,1102,20,32,224,101,-640,224,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,8,226,226,224,1002,223,2,223,1006,224,329,101,1,223,223,1008,677,677,224,102,2,223,223,1006,224,344,101,1,223,223,1107,226,677,224,102,2,223,223,1005,224,359,101,1,223,223,1008,226,226,224,1002,223,2,223,1006,224,374,1001,223,1,223,1108,677,226,224,1002,223,2,223,1006,224,389,1001,223,1,223,7,677,226,224,1002,223,2,223,1006,224,404,101,1,223,223,7,226,226,224,1002,223,2,223,1005,224,419,101,1,223,223,8,226,677,224,1002,223,2,223,1006,224,434,1001,223,1,223,7,226,677,224,1002,223,2,223,1006,224,449,1001,223,1,223,107,226,677,224,1002,223,2,223,1005,224,464,1001,223,1,223,1007,677,677,224,102,2,223,223,1005,224,479,101,1,223,223,1007,226,226,224,102,2,223,223,1005,224,494,1001,223,1,223,1108,226,677,224,102,2,223,223,1005,224,509,101,1,223,223,1008,677,226,224,102,2,223,223,1005,224,524,1001,223,1,223,1007,677,226,224,102,2,223,223,1005,224,539,101,1,223,223,1108,226,226,224,1002,223,2,223,1005,224,554,101,1,223,223,108,226,226,224,102,2,223,223,1005,224,569,101,1,223,223,108,677,677,224,102,2,223,223,1005,224,584,101,1,223,223,1107,226,226,224,1002,223,2,223,1006,224,599,101,1,223,223,8,677,226,224,1002,223,2,223,1006,224,614,1001,223,1,223,108,677,226,224,102,2,223,223,1006,224,629,1001,223,1,223,1107,677,226,224,1002,223,2,223,1006,224,644,1001,223,1,223,107,677,677,224,102,2,223,223,1005,224,659,101,1,223,223,107,226,226,224,102,2,223,223,1006,224,674,1001,223,1,223,4,223,99,226]

Program(puzzle_day5_1, inputs=[1]).run()

#for noun in range(100):
#    for verb in range(100):
#        program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])
#        program.set(1, noun)
#        program.set(2, verb)
#
#        program.run()
#
#        if program.get(0) == 19690720:
#            print noun, verb, str(noun)+str(verb)
#            exit(0)

