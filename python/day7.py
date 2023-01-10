DEBUG=False

def massert (cond, *args):
    # My assert - print args and exit if condition is false
    if not cond:
        print("\nAssertion!")
        print("\n".join([str(arg) for arg in args]))
        assert(False)

class Instruction:
    @staticmethod
    def get_instruction (instruction):
        # Factory
        opcode = instruction %100
        modes = instruction // 100

        if DEBUG: print(instruction, opcode, modes)

        return { 1 : AddInstr,
                 2 : MultInstr,
                 3 : InputInstr,
                 4 : OutputInstr,
                 5 : JitInstr,
                 6 : JifInstr,
                 7 : LtInstr,
                 8 : EqInstr,
                99 : TerminateInstr }[opcode](modes)

    def __init__ (self, modes):
        self.modes = modes

        self._params = None

        if DEBUG: print(self.__class__.__name__)

    def get_params (self, program):
        if self._params is None:
            self._decode_modes()
            self._params = self._get_params(program)

        return self._params

    def _get_params (self, program):
        # override in child class
        assert(False)

    def _get_single_param (self, program, ip):
        p = program.get(ip)
        return self._maybe_deref(p, program)

    def _maybe_deref (self, param, program):
        # Only works if params are called in order!
        m = self.modes.pop(0) if self.modes else 0

        if m == 0:
            return program.get(param)
        else:
            return param

    def execute (self, program):
        # Must override in child class
        # returns (new ip, continue)
        assert(False)

    def _decode_modes (self):
        modesarr = []
        while self.modes > 0:
            modesarr.append(self.modes % 10)
            self.modes //= 10

        self.modes = modesarr

class CombineTwoInstr(Instruction):
    # Use default init method

    def execute (self, program):
        # Execute this instruction, modifying the passed-in memory
        p1,p2,p3 = self.get_params(program)

        program.store(self.combine(p1,p2), p3)
        return program.ip+4, True

    def combine (self, p1, p2):
        # override in child class
        assert(False)

    def _get_params (self, program):
        # Add or multiply - process 2 params and store at 3rd
        # Three parameters, starting from the next position after the ip
        p1 = self._get_single_param(program, program.ip+1)
        p2 = self._get_single_param(program, program.ip+2)
        p3 = program.get(program.ip+3)

        return (p1, p2, p3)

class AddInstr(CombineTwoInstr):
    def combine (self, a, b):
        try:
            return a+b
        except TypeError:
            print(a)
            print(b)
            print(self)
            raise

class MultInstr(CombineTwoInstr):
    def combine (self, a, b):
        return a*b

class InputInstr(Instruction):
    def execute (self, program):
        val = program.inputs.pop(0)
        loc = self.get_params(program)[0]
        program.store(val, loc)

        return program.ip+2, True

    def _get_params (self, program):
        return (program.get(program.ip+1), )

class OutputInstr(Instruction):
    # Dummy showing which methods definitely need overriding
    def execute (self, program):
        val = self.get_params(program)[0]
        program.append_to_output(val)
        return program.ip+2, True

    def _get_params(self, program):
        p = self._get_single_param(program, program.ip+1)
        return (p, )

class TerminateInstr(Instruction):
    # Dummy showing which methods definitely need overriding
    def execute (self, program):
        return program.ip+1, False

    def _get_params (self, program):
        return (None,)

class JumpIfInstr(Instruction):
    def execute (self, program):
        test_val, ip_val = self.get_params(program)

        if self.do_test(test_val):
            next_ip = ip_val
        else:
            next_ip = program.ip +3  # Opcode, test val, next ip val

        if DEBUG: print(self.__class__.__name__, test_val, ip_val, "->", next_ip)
        return next_ip, True

    def _get_params (self, program):
        ip = program.ip

        return (self._get_single_param(program, ip+1), self._get_single_param(program, ip+2))

class JitInstr(JumpIfInstr):
    # Jump if true.  If first param is non-zero, set ip to value from second param
    def do_test (self, val):
        return val

class JifInstr(JumpIfInstr):
    # Jump if false.  If first param is zero, set ip to value from second param
    def do_test (self, val):
        return not val

class CompareInstr(Instruction):
    # Compare two values, and store the results in the third location
    def execute (self, program):
        t1, t2, loc = self.get_params(program)

        if self._compare(t1,t2):
            val = 1
        else:
            val = 0

        program.store(val, loc)
        return program.ip+4, True  # instruction, 2 params to compare, 1 store

    def _get_params (self, program):
        p1 = self._get_single_param(program, program.ip+1)
        p2 = self._get_single_param(program, program.ip+2)
        p3 = program.get(program.ip+3)
        return (p1, p2, p3)

    def _compare (self, a, b):
        # Override in child class
        assert(False)

class LtInstr(CompareInstr):
    def _compare (self, a, b):
        return a < b

class EqInstr(CompareInstr):
    def _compare (self, a, b):
        return a == b

class TemplateInstr(Instruction):
    # Dummy showing which methods definitely need overriding
    def execute (self, program):
        # TODO
        return next_ip, True

    def _get_params (self, program):
        # TODO figure out what params you need
        return (p1, p2, )


class Program:
    def __init__ (self, initial_memory_state, inputs=[], pause_on_output=False):
        self.memory = list(initial_memory_state)
        self.ip = 0
        self.inputs = inputs
        self.output_buffer = []
        self.new_output = False
        self.pause_on_output = pause_on_output

    def append_to_output (self, val):
        # Output
        self.output_buffer.append(val)
        if DEBUG: print("Output updated:\t", " ".join([str(o) for o in self.output_buffer]))
        self.new_output = True

    def store (self, val, loc):
        if loc >= len(self.memory):
            print("Store outside memory buffer: {} with memory of length {}".format(loc, len(self.memory)))
            exit(1)

        self.memory[loc] = val
        if DEBUG: print("Update ({}->{}):\t".format(loc,val), self.memory)

    def get (self, ix):
        return self.memory[ix]

    def run(self):
        if DEBUG: print("Starting prog:\t", self.memory,"\n  with inputs:\t", self.inputs)
        carry_on = True
        try:
            while carry_on:
                if DEBUG: print("ip:",self.ip,"\t")
                this_instr = self.get(self.ip)
                instr = Instruction.get_instruction(this_instr)
                self.ip, carry_on = instr.execute(self)

                if carry_on and self.pause_on_output and self.new_output:
                    # Send the output and then pause
                    output = self.output_buffer[0]
                    self.output_buffer = []
                    self.new_output = False
                    if DEBUG: print("Interim output:", output)
                    return output
        except:
            raise
        finally:
            if self.output_buffer:
                if DEBUG: print("Output:", self.output_buffer)

        return self.output_buffer

    def display(self, debug=False):
        print(self.memory)
        if debug:
            print(self.ip)
            print()

def test (program, inputs=None, output=None, expected_mem=None, expected_mem_len=None):
    p = Program(program, inputs=inputs)
    p_out = p.run()

    if output:
        assert(" ".join([str(o) for o in p_out]) == output)

    if expected_mem:
        if not expected_mem_len:
            expected_mem_len = len(expected_mem)

        if not (p.memory[:expected_mem_len] == expected_mem):
            print("Vals not equal:\n\t", p.memory[:expected_mem_len],"\n\t", expected_mem)
            assert(False)

def test_day2 ():
    # Test day2 simple programs
    #Program([1,0,0,0,99]).test([2,0,0,0,99])
    test([1,0,0,0,99], expected_mem = [2,0,0,0,99])

    #Program([2,3,0,3,99]).test([2,3,0,6,99])
    test([2,3,0,3,99], expected_mem = [2,3,0,6,99])

    #Program([2,4,4,5,99,0]).test([2,4,4,5,99,9801])
    test([2,4,4,5,99,0], expected_mem = [2,4,4,5,99,9801])

    #Program([1,1,1,4,99, 5,6,0,99]).test([30,1,1,4,2,5,6,0,99])
    test([1,1,1,4,99, 5,6,0,99], expected_mem = [30,1,1,4,2,5,6,0,99])

    #program = Program([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])
    #program.set(1,12)
    #program.set(2,2)
    #program.run()
    #print program.get(0)
    #assert(program.get(0) == 3562624)
    test([1, 12,2, 3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0],
         expected_mem = [3562624], expected_mem_len=1)

    #Program([1002,4,3,4,33]).test([1002,4,3,4,99])
    test([1002,4,3,4,33], expected_mem = [1002,4,3,4,99])

    #Program([1101,100,-1,4,0]).test([1101,100,-1,4,99])
    test([1101,100,-1,4,0], expected_mem = [1101,100,-1,4,99])


def test_day5_1_examples ():
    #p = Program([3,1,4,1,99], inputs=[77])
    #p.test([3,77,4,1,99])
    #assert(p.output_buffer == "77")
    test([3,1,4,1,99], inputs=[77], output="77")

def test_day5_1_puzzle():
    # Day 5.1 puzzle
    program = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,82,10,225,101,94,44,224,101,-165,224,224,4,224,1002,223,8,223,101,3,224,224,1,224,223,223,1102,35,77,225,1102,28,71,225,1102,16,36,225,102,51,196,224,101,-3468,224,224,4,224,102,8,223,223,1001,224,7,224,1,223,224,223,1001,48,21,224,101,-57,224,224,4,224,1002,223,8,223,101,6,224,224,1,223,224,223,2,188,40,224,1001,224,-5390,224,4,224,1002,223,8,223,101,2,224,224,1,224,223,223,1101,9,32,224,101,-41,224,224,4,224,1002,223,8,223,1001,224,2,224,1,223,224,223,1102,66,70,225,1002,191,28,224,101,-868,224,224,4,224,102,8,223,223,101,5,224,224,1,224,223,223,1,14,140,224,101,-80,224,224,4,224,1002,223,8,223,101,2,224,224,1,224,223,223,1102,79,70,225,1101,31,65,225,1101,11,68,225,1102,20,32,224,101,-640,224,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,8,226,226,224,1002,223,2,223,1006,224,329,101,1,223,223,1008,677,677,224,102,2,223,223,1006,224,344,101,1,223,223,1107,226,677,224,102,2,223,223,1005,224,359,101,1,223,223,1008,226,226,224,1002,223,2,223,1006,224,374,1001,223,1,223,1108,677,226,224,1002,223,2,223,1006,224,389,1001,223,1,223,7,677,226,224,1002,223,2,223,1006,224,404,101,1,223,223,7,226,226,224,1002,223,2,223,1005,224,419,101,1,223,223,8,226,677,224,1002,223,2,223,1006,224,434,1001,223,1,223,7,226,677,224,1002,223,2,223,1006,224,449,1001,223,1,223,107,226,677,224,1002,223,2,223,1005,224,464,1001,223,1,223,1007,677,677,224,102,2,223,223,1005,224,479,101,1,223,223,1007,226,226,224,102,2,223,223,1005,224,494,1001,223,1,223,1108,226,677,224,102,2,223,223,1005,224,509,101,1,223,223,1008,677,226,224,102,2,223,223,1005,224,524,1001,223,1,223,1007,677,226,224,102,2,223,223,1005,224,539,101,1,223,223,1108,226,226,224,1002,223,2,223,1005,224,554,101,1,223,223,108,226,226,224,102,2,223,223,1005,224,569,101,1,223,223,108,677,677,224,102,2,223,223,1005,224,584,101,1,223,223,1107,226,226,224,1002,223,2,223,1006,224,599,101,1,223,223,8,677,226,224,1002,223,2,223,1006,224,614,1001,223,1,223,108,677,226,224,102,2,223,223,1006,224,629,1001,223,1,223,1107,677,226,224,1002,223,2,223,1006,224,644,1001,223,1,223,107,677,677,224,102,2,223,223,1005,224,659,101,1,223,223,107,226,226,224,102,2,223,223,1006,224,674,1001,223,1,223,4,223,99,226]
    test(program, inputs=[1], output="0 0 0 0 0 0 0 0 0 8332629")

def test_day5_2_tests ():
  if True:
    # Day 5.2 tests
    # Test 1 - eq, position mode
    program = [3,9,8,9,10,9,4,9,99,-1,8]
    test(program, inputs=[7], output="0")  # Input ne 8
    test(program, inputs=[8], output="1")  # Input eq 8

    # Test 2 - lt, position mode
    program = [3,9,7,9,10,9,4,9,99,-1,8]
    test(program, inputs=[7], output="1")  # input lt 8
    test(program, inputs=[8], output="0")  # input not lt 8
    test(program, inputs=[9], output="0")  # input not lt 8
    test(program, inputs=[-1], output="1") # input lt 8

    # Test 3 - eq, immediate mode
    program = [3,3,1108,-1,8,3,4,3,99]
    test(program, inputs=[7], output="0")  # Input ne 8
    test(program, inputs=[8], output="1")  # Input eq 8

    # Test 4 - lt, immediate mode
    program = [3,3,1107,-1,8,3,4,3,99]
    test(program, inputs=[7], output="1")  # input lt 8
    test(program, inputs=[8], output="0")  # input not lt 8
    test(program, inputs=[9], output="0")  # input not lt 8
    test(program, inputs=[-1], output="1") # input lt 8

  if True:
    # Test larger example
    program = [3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99]
    test(program, inputs=[7],output="999")
    test(program, inputs=[-1],output="999")
    test(program, inputs=[8],output="1000")
    test(program, inputs=[9],output="1001")

def test_day5_2_puzzle ():
    program = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,82,10,225,101,94,44,224,101,-165,224,224,4,224,1002,223,8,223,101,3,224,224,1,224,223,223,1102,35,77,225,1102,28,71,225,1102,16,36,225,102,51,196,224,101,-3468,224,224,4,224,102,8,223,223,1001,224,7,224,1,223,224,223,1001,48,21,224,101,-57,224,224,4,224,1002,223,8,223,101,6,224,224,1,223,224,223,2,188,40,224,1001,224,-5390,224,4,224,1002,223,8,223,101,2,224,224,1,224,223,223,1101,9,32,224,101,-41,224,224,4,224,1002,223,8,223,1001,224,2,224,1,223,224,223,1102,66,70,225,1002,191,28,224,101,-868,224,224,4,224,102,8,223,223,101,5,224,224,1,224,223,223,1,14,140,224,101,-80,224,224,4,224,1002,223,8,223,101,2,224,224,1,224,223,223,1102,79,70,225,1101,31,65,225,1101,11,68,225,1102,20,32,224,101,-640,224,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,8,226,226,224,1002,223,2,223,1006,224,329,101,1,223,223,1008,677,677,224,102,2,223,223,1006,224,344,101,1,223,223,1107,226,677,224,102,2,223,223,1005,224,359,101,1,223,223,1008,226,226,224,1002,223,2,223,1006,224,374,1001,223,1,223,1108,677,226,224,1002,223,2,223,1006,224,389,1001,223,1,223,7,677,226,224,1002,223,2,223,1006,224,404,101,1,223,223,7,226,226,224,1002,223,2,223,1005,224,419,101,1,223,223,8,226,677,224,1002,223,2,223,1006,224,434,1001,223,1,223,7,226,677,224,1002,223,2,223,1006,224,449,1001,223,1,223,107,226,677,224,1002,223,2,223,1005,224,464,1001,223,1,223,1007,677,677,224,102,2,223,223,1005,224,479,101,1,223,223,1007,226,226,224,102,2,223,223,1005,224,494,1001,223,1,223,1108,226,677,224,102,2,223,223,1005,224,509,101,1,223,223,1008,677,226,224,102,2,223,223,1005,224,524,1001,223,1,223,1007,677,226,224,102,2,223,223,1005,224,539,101,1,223,223,1108,226,226,224,1002,223,2,223,1005,224,554,101,1,223,223,108,226,226,224,102,2,223,223,1005,224,569,101,1,223,223,108,677,677,224,102,2,223,223,1005,224,584,101,1,223,223,1107,226,226,224,1002,223,2,223,1006,224,599,101,1,223,223,8,677,226,224,1002,223,2,223,1006,224,614,1001,223,1,223,108,677,226,224,102,2,223,223,1006,224,629,1001,223,1,223,1107,677,226,224,1002,223,2,223,1006,224,644,1001,223,1,223,107,677,677,224,102,2,223,223,1005,224,659,101,1,223,223,107,226,226,224,102,2,223,223,1006,224,674,1001,223,1,223,4,223,99,226]
    test(program, inputs=[5], output="8805067")

# Day 7
import sys

def find_largest_output (limits, program, fun):
    biggest_output = 0

    aas = range(limits[0], limits[1])

    for aa in aas:
        if DEBUG: print("\n", aa)
        bs = list(aas)
        bs.pop(bs.index(aa))
        for bb in bs:
            if DEBUG: print(".") ;sys.stdout.flush()
            cs = list(bs)
            cs.pop(cs.index(bb))
            for cc in cs:
                ds = list(cs)
                ds.pop(ds.index(cc))
                for dd in ds:
                    es = list(ds)
                    es.pop(es.index(dd))
                    assert(len(es) == 1)
                    for ee in es:
                        output = fun(program, aa,bb,cc,dd,ee)

                        if output > biggest_output:
                            biggest_output = output
                            best_order = [aa,bb,cc,dd,ee]

    if DEBUG: print()
    return biggest_output, best_order

def day7part1fun(program, aa,bb,cc,dd,ee):
    ampA = Program(program, inputs=[aa, 0])
    outA = ampA.run()[0]

    ampB = Program(program, inputs=[bb, outA])
    outB = ampB.run()[0]

    ampC = Program(program, inputs=[cc, outB])
    outC = ampC.run()[0]

    ampD = Program(program, inputs=[dd, outC])
    outD = ampD.run()[0]

    ampE = Program(program, inputs=[ee, outD])
    outE = ampE.run()[0]

    return outE

def day7part2fun(program, aa,bb,cc,dd,ee):
    # Assumes loop runs through more than once
    ampA = Program(program, inputs=[aa, 0], pause_on_output=True)
    outA = ampA.run()
    ampB = Program(program, inputs=[bb, outA], pause_on_output=True)
    outB = ampB.run()
    ampC = Program(program, inputs=[cc, outB], pause_on_output=True)
    outC = ampC.run()
    ampD = Program(program, inputs=[dd, outC], pause_on_output=True)
    outD = ampD.run()
    ampE = Program(program, inputs=[ee, outD], pause_on_output=True)
    outE = ampE.run()

    finalE = outE

    halting = False
    while not halting:
        ampA.inputs.append(outE)
        outA = ampA.run()
        if type(outA) == list:
            halting = True
            if outA: outA = outA[0]

        if outA: ampB.inputs.append(outA)
        outB = ampB.run()
        if halting:
            assert(type(outB) == list)
            if outB: outB = outB[0]

        if outB: ampC.inputs.append(outB)
        outC = ampC.run()
        if halting:
            assert(type(outC) == list)
            if outC: outC = outC[0]

        if outC: ampD.inputs.append(outC)
        outD = ampD.run()
        if halting:
            assert(type(outD) == list)
            if outD: outD = outD[0]

        if outD: ampE.inputs.append(outD)
        outE = ampE.run()
        if halting:
            assert(type(outE) == list)
            return finalE
        else:
            finalE=outE


#DAY_7_PROGRAM = [3,8,1001,8,10,8,105,1,0,0,21,34,55,68,93,106,187,268,349,430,99999,3,9,102,5,9,9,1001,9,2,9,4,9,99,3,9,1001,9,5,9,102,2,9,9,101,2,9,9,102,2,9,9,4,9,99,3,9,101,2,9,9,102,4,9,9,4,9,99,3,9,101,4,9,9,102,3,9,9,1001,9,2,9,102,4,9,9,1001,9,2,9,4,9,99,3,9,101,2,9,9,1002,9,5,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,99,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,99]
DAY_7_PROGRAM = [3,8,1001,8,10,8,105,1,0,0,21,38,55,72,93,118,199,280,361,442,99999,3,9,1001,9,2,9,1002,9,5,9,101,4,9,9,4,9,99,3,9,1002,9,3,9,1001,9,5,9,1002,9,4,9,4,9,99,3,9,101,4,9,9,1002,9,3,9,1001,9,4,9,4,9,99,3,9,1002,9,4,9,1001,9,4,9,102,5,9,9,1001,9,4,9,4,9,99,3,9,101,3,9,9,1002,9,3,9,1001,9,3,9,102,5,9,9,101,4,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,99]
def test_day7():
    assert(43210 == find_largest_output((0,5), [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0], day7part1fun)[0])
    assert(54321 == find_largest_output((0,5), [3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0], day7part1fun)[0])
    assert(65210 == find_largest_output((0,5), [3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0], day7part1fun)[0])

    #assert(34852 == find_largest_output((0,5), DAY_7_PROGRAM, day7part1fun)[0])

def tests ():
    test_day2()
    test_day5_1_examples()
    test_day5_1_puzzle()
    test_day5_2_tests()
    test_day5_2_puzzle()
    test_day7()

    print("All tests passed")

tests()

DEBUG=False
print(find_largest_output((5,10), [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5], day7part2fun))
sys.stdout.flush()
print(find_largest_output((5,10), [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10], day7part2fun))
sys.stdout.flush()
print(find_largest_output((0,5), DAY_7_PROGRAM, day7part1fun))
print(find_largest_output((5,10), DAY_7_PROGRAM, day7part2fun))
sys.stdout.flush()

