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

        if DEBUG: print("{} ({} | {})".format(instruction, opcode, modes),)

        return { 1 : AddInstr,
                 2 : MultInstr,
                 3 : InputInstr,
                 4 : OutputInstr,
                 5 : JitInstr,
                 6 : JifInstr,
                 7 : LtInstr,
                 8 : EqInstr,
                 9 : RelBaseInstr,
                99 : TerminateInstr }[opcode](modes)

    def __init__ (self, modes):
        self.modes = modes

        self._params = None

        if DEBUG: print(self.__class__.__name__)

    def get_params (self, computer):
        if self._params is None:
            self._decode_modes()
            self._params = self._get_params(computer)

        return self._params

    def _get_params (self, computer):
        # override in child class
        assert(False)

    def _get_single_param (self, computer, ip):
        p = computer.get(ip)
        return self._maybe_deref(p, computer)

    def _maybe_deref (self, param, computer):
        # Only works if params are called in order!
        m = self.modes.pop(0) if self.modes else 0

        if m == 0:
            # position mode
            return computer.get(param)
        elif m == 1:
            # immediate mode
            return param
        elif m == 2:
            # relative base mode
            return computer.get(computer.relative_base + param)
        else:
            print ("Unknown mode:", m)
            assert(False)

    def execute (self, computer):
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

    def execute (self, computer):
        # Execute this instruction, modifying the passed-in memory
        p1,p2,p3 = self.get_params(computer)

        computer.store(self.combine(p1,p2), p3)
        return computer.ip+4, True

    def combine (self, p1, p2):
        # override in child class
        assert(False)

    def _get_params (self, computer):
        # Add or multiply - process 2 params and store at 3rd
        # Three parameters, starting from the next position after the ip
        p1 = self._get_single_param(computer, computer.ip+1)
        p2 = self._get_single_param(computer, computer.ip+2)

        p3 = computer.get(computer.ip+3)
        m = self.modes.pop(0) if self.modes else 0
        if m == 2: p3 = p3 + computer.relative_base

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

    def execute (self, computer):
        #assert(len(self.modes) == 1)
        mode = self.modes

        val = computer.get_input()

        if DEBUG: print("mode:", mode, " val:", val)

        if mode == 0 or mode == 1:
            # Store the val at the address stored in the param
            loc = computer.get(computer.ip +1)
        elif mode == 2:
            loc = computer.get(computer.ip +1) + computer.relative_base
        else:
            print("unknown input mode:", mode)
            assert(False)

        computer.store(val,loc)

        return computer.ip+2, True

class OutputInstr(Instruction):
    # Dummy showing which methods definitely need overriding
    def execute (self, computer):
        val = self.get_params(computer)[0]
        computer.append_to_output(val)
        return computer.ip+2, True

    def _get_params(self, computer):
        p = self._get_single_param(computer, computer.ip+1)
        return (p, )

class TerminateInstr(Instruction):
    # Dummy showing which methods definitely need overriding
    def execute (self, computer):
        return computer.ip+1, False

    def _get_params (self, computer):
        return (None,)

class JumpIfInstr(Instruction):
    def execute (self, computer):
        test_val, ip_val = self.get_params(computer)

        if self.do_test(test_val):
            next_ip = ip_val
        else:
            next_ip = computer.ip +3  # Opcode, test val, next ip val

        if DEBUG: print(self.__class__.__name__, test_val, ip_val, "->", next_ip)
        return next_ip, True

    def _get_params (self, computer):
        ip = computer.ip

        return (self._get_single_param(computer, ip+1), self._get_single_param(computer, ip+2))

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
    def execute (self, computer):
        t1, t2, loc = self.get_params(computer)

        if self._compare(t1,t2):
            val = 1
        else:
            val = 0

        computer.store(val, loc)
        return computer.ip+4, True  # instruction, 2 params to compare, 1 store

    def _get_params (self, computer):
        p1 = self._get_single_param(computer, computer.ip+1)
        p2 = self._get_single_param(computer, computer.ip+2)

        p3 = computer.get(computer.ip+3)
        m = self.modes.pop(0) if self.modes else 0
        if m == 2: p3 = p3 + computer.relative_base

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

class RelBaseInstr(Instruction):
    def execute (self, computer):
        computer.relative_base += self.get_params(computer)[0]
        if DEBUG: print("Relbase is now", computer.relative_base)
        return computer.ip+2, True

    def _get_params (self, computer):
        p1 = self._get_single_param(computer, computer.ip+1)
        return (p1, )

class TemplateInstr(Instruction):
    # Dummy showing which methods definitely need overriding
    def execute (self, computer):
        # TODO
        return next_ip, True

    def _get_params (self, computer):
        # TODO figure out what params you need
        return (p1, p2, )


class Computer:
    def __init__ (self, initial_memory_state, inputs=[], input_fun=None, pause_on_output=False):
        if inputs and input_fun:
            print("Invalid - define either inputs array or inputs function, not both")
            print(inputs)
            print(input_fun)
            assert(False)
        self.memory = list(initial_memory_state)
        self.ip = 0
        self.inputs = inputs
        self.input_fun = input_fun
        self.output_buffer = []
        self.new_output = False
        self.pause_on_output = pause_on_output
        self.relative_base = 0

    def append_to_output (self, val):
        # Output
        self.output_buffer.append(val)
        if DEBUG: print("Output updated:\t", " ".join([str(o) for o in self.output_buffer]))
        self.new_output = True

    def store (self, val, loc):
        self._check_or_extend_memory(loc)

        self.memory[loc] = val
        if DEBUG: print("Update ({}->{}):\t".format(loc,val), self.memory)

    def get (self, ix):
        self._check_or_extend_memory(ix)
        return self.memory[ix]

    def _check_or_extend_memory(self, loc):
        while loc >= len(self.memory):
            self.memory.append(0)

    def get_input(self):
        if self.input_fun:
            return self.input_fun()
        else:
            return self.inputs.pop(0)

    def run(self):
        # If computer is in "pause_on_output" mode, run until there is an instruction or program
        # halts, and return (output_val, halted) tuple
        # Otherwise run until halting, and return the full output (as an array of numbers)
        if DEBUG: print("Starting prog:\t", self.memory,"\n  with inputs:\t", self.inputs)
        carry_on = True
        try:
            while carry_on:
                if DEBUG: print("ip:",self.ip,"\t",)
                this_instr = self.get(self.ip)
                instr = Instruction.get_instruction(this_instr)
                self.ip, carry_on = instr.execute(self)

                if carry_on and self.pause_on_output and self.new_output:
                    # Send the output and then pause
                    output = self.output_buffer[0]
                    self.output_buffer = []
                    self.new_output = False
                    if DEBUG: print("Interim output:", output)
                    return output, False
        except:
            raise
        finally:
            if self.output_buffer:
                if DEBUG: print("Output:", self.output_buffer)

        if self.pause_on_output:
            if self.new_output:
                output = self.output_buffer[0]
            else:
                output = None
            return output, True
        else:
            return self.output_buffer

    def display(self, debug=False):
        print(self.memory)
        if debug:
            print(self.ip)
            print()

def test (program, inputs=None, input_fun=None, output=None, expected_mem=None, expected_mem_len=None):
    p = Computer(program, inputs=inputs, input_fun=input_fun)
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
    #Computer([1,0,0,0,99]).test([2,0,0,0,99])
    test([1,0,0,0,99], expected_mem = [2,0,0,0,99])

    #Computer([2,3,0,3,99]).test([2,3,0,6,99])
    test([2,3,0,3,99], expected_mem = [2,3,0,6,99])

    #Computer([2,4,4,5,99,0]).test([2,4,4,5,99,9801])
    test([2,4,4,5,99,0], expected_mem = [2,4,4,5,99,9801])

    #Computer([1,1,1,4,99, 5,6,0,99]).test([30,1,1,4,2,5,6,0,99])
    test([1,1,1,4,99, 5,6,0,99], expected_mem = [30,1,1,4,2,5,6,0,99])

    #computer = Computer([1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0])
    #computer.set(1,12)
    #computer.set(2,2)
    #computer.run()
    #print computer.get(0)
    #assert(computer.get(0) == 3562624)
    test([1, 12,2, 3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0],
         expected_mem = [3562624], expected_mem_len=1)

    #Computer([1002,4,3,4,33]).test([1002,4,3,4,99])
    test([1002,4,3,4,33], expected_mem = [1002,4,3,4,99])

    #Computer([1101,100,-1,4,0]).test([1101,100,-1,4,99])
    test([1101,100,-1,4,0], expected_mem = [1101,100,-1,4,99])


def test_day5_1_examples ():
    #p = Computer([3,1,4,1,99], inputs=[77])
    #p.test([3,77,4,1,99])
    #assert(p.output_buffer == "77")
    test([3,1,4,1,99], inputs=[77], output="77")

    # With input function
    def input77(): return 77
    test([3,1,4,1,99], input_fun=input77, output="77")

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
        if DEBUG: print("\n", aa,)
        bs = list(aas)
        bs.pop(bs.index(aa))
        for bb in bs:
            if DEBUG: print(".",) ;sys.stdout.flush()
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
    ampA = Computer(program, inputs=[aa, 0])
    outA = ampA.run()[0]

    ampB = Computer(program, inputs=[bb, outA])
    outB = ampB.run()[0]

    ampC = Computer(program, inputs=[cc, outB])
    outC = ampC.run()[0]

    ampD = Computer(program, inputs=[dd, outC])
    outD = ampD.run()[0]

    ampE = Computer(program, inputs=[ee, outD])
    outE = ampE.run()[0]

    return outE

def day7part2fun(program, aa,bb,cc,dd,ee):
    # Assumes loop runs through more than once
    ampA = Computer(program, inputs=[aa, 0], pause_on_output=True)
    outA, stopped = ampA.run()
    assert (not stopped)
    ampB = Computer(program, inputs=[bb, outA], pause_on_output=True)
    outB, stopped = ampB.run()
    assert (not stopped)
    ampC = Computer(program, inputs=[cc, outB], pause_on_output=True)
    outC, stopped = ampC.run()
    assert (not stopped)
    ampD = Computer(program, inputs=[dd, outC], pause_on_output=True)
    outD, stopped = ampD.run()
    assert (not stopped)
    ampE = Computer(program, inputs=[ee, outD], pause_on_output=True)
    outE, stopped = ampE.run()
    assert (not stopped)

    finalE = outE

    halting = False
    while not halting:
        ampA.inputs.append(outE)
        outA, a_stopped = ampA.run()
        if a_stopped:
            halting = True

        if outA: ampB.inputs.append(outA)
        outB, b_stopped = ampB.run()
        if halting:
            assert(b_stopped)

        if outB: ampC.inputs.append(outB)
        outC, c_stopped = ampC.run()
        if halting:
            assert(c_stopped)

        if outC: ampD.inputs.append(outC)
        outD, d_stopped = ampD.run()
        if halting:
            assert(d_stopped)

        if outD: ampE.inputs.append(outD)
        outE, e_stopped = ampE.run()
        if halting:
            assert(e_stopped)
            return finalE
        else:
            finalE=outE


def test_day7():
    DAY_7_PROGRAM = [3,8,1001,8,10,8,105,1,0,0,21,34,55,68,93,106,187,268,349,430,99999,3,9,102,5,9,9,1001,9,2,9,4,9,99,3,9,1001,9,5,9,102,2,9,9,101,2,9,9,102,2,9,9,4,9,99,3,9,101,2,9,9,102,4,9,9,4,9,99,3,9,101,4,9,9,102,3,9,9,1001,9,2,9,102,4,9,9,1001,9,2,9,4,9,99,3,9,101,2,9,9,1002,9,5,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,99,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,99]

    # Part 1
    assert(43210 == find_largest_output((0,5), [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0], day7part1fun)[0])
    assert(54321 == find_largest_output((0,5), [3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0], day7part1fun)[0])
    assert(65210 == find_largest_output((0,5), [3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0], day7part1fun)[0])

    assert(34852 == find_largest_output((0,5), DAY_7_PROGRAM, day7part1fun)[0])

    # Part 2
    assert(139629729 == find_largest_output((5,10), [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5], day7part2fun)[0])
    assert(18216 == find_largest_output((5,10), [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10], day7part2fun)[0])
    assert(44282086 == find_largest_output((5,10), DAY_7_PROGRAM, day7part2fun)[0])

def test_day_9():
    DAY_9_PROGRAM=[1102,34463338,34463338,63,1007,63,34463338,63,1005,63,53,1101,3,0,1000,109,988,209,12,9,1000,209,6,209,3,203,0,1008,1000,1,63,1005,63,65,1008,1000,2,63,1005,63,904,1008,1000,0,63,1005,63,58,4,25,104,0,99,4,0,104,0,99,4,17,104,0,99,0,0,1102,0,1,1020,1102,29,1,1001,1101,0,28,1016,1102,1,31,1011,1102,1,396,1029,1101,26,0,1007,1101,0,641,1026,1101,466,0,1023,1101,30,0,1008,1102,1,22,1003,1101,0,35,1019,1101,0,36,1018,1102,1,37,1012,1102,1,405,1028,1102,638,1,1027,1102,33,1,1000,1102,1,27,1002,1101,21,0,1017,1101,0,20,1015,1101,0,34,1005,1101,0,23,1010,1102,25,1,1013,1101,39,0,1004,1101,32,0,1009,1101,0,38,1006,1101,0,473,1022,1102,1,1,1021,1101,0,607,1024,1102,1,602,1025,1101,24,0,1014,109,22,21108,40,40,-9,1005,1013,199,4,187,1105,1,203,1001,64,1,64,1002,64,2,64,109,-17,2102,1,4,63,1008,63,32,63,1005,63,229,4,209,1001,64,1,64,1105,1,229,1002,64,2,64,109,9,21108,41,44,1,1005,1015,245,1105,1,251,4,235,1001,64,1,64,1002,64,2,64,109,4,1206,3,263,1105,1,269,4,257,1001,64,1,64,1002,64,2,64,109,-8,21102,42,1,5,1008,1015,42,63,1005,63,291,4,275,1105,1,295,1001,64,1,64,1002,64,2,64,109,-13,1208,6,22,63,1005,63,313,4,301,1105,1,317,1001,64,1,64,1002,64,2,64,109,24,21107,43,44,-4,1005,1017,339,4,323,1001,64,1,64,1105,1,339,1002,64,2,64,109,-5,2107,29,-8,63,1005,63,361,4,345,1001,64,1,64,1105,1,361,1002,64,2,64,109,-4,2101,0,-3,63,1008,63,32,63,1005,63,387,4,367,1001,64,1,64,1106,0,387,1002,64,2,64,109,13,2106,0,3,4,393,1001,64,1,64,1105,1,405,1002,64,2,64,109,-27,2102,1,2,63,1008,63,35,63,1005,63,425,1105,1,431,4,411,1001,64,1,64,1002,64,2,64,109,5,1202,2,1,63,1008,63,31,63,1005,63,455,1001,64,1,64,1106,0,457,4,437,1002,64,2,64,109,19,2105,1,1,1001,64,1,64,1105,1,475,4,463,1002,64,2,64,109,-6,21102,44,1,1,1008,1017,45,63,1005,63,499,1001,64,1,64,1105,1,501,4,481,1002,64,2,64,109,6,1205,-2,513,1106,0,519,4,507,1001,64,1,64,1002,64,2,64,109,-17,1207,-1,40,63,1005,63,537,4,525,1106,0,541,1001,64,1,64,1002,64,2,64,109,-8,1201,9,0,63,1008,63,38,63,1005,63,567,4,547,1001,64,1,64,1106,0,567,1002,64,2,64,109,-3,2101,0,6,63,1008,63,32,63,1005,63,591,1001,64,1,64,1105,1,593,4,573,1002,64,2,64,109,22,2105,1,8,4,599,1106,0,611,1001,64,1,64,1002,64,2,64,109,8,1206,-4,625,4,617,1105,1,629,1001,64,1,64,1002,64,2,64,109,3,2106,0,0,1106,0,647,4,635,1001,64,1,64,1002,64,2,64,109,-29,2107,27,9,63,1005,63,667,1001,64,1,64,1106,0,669,4,653,1002,64,2,64,109,7,1207,-4,28,63,1005,63,689,1001,64,1,64,1105,1,691,4,675,1002,64,2,64,109,-7,2108,30,3,63,1005,63,711,1001,64,1,64,1105,1,713,4,697,1002,64,2,64,109,17,21101,45,0,-5,1008,1010,45,63,1005,63,735,4,719,1106,0,739,1001,64,1,64,1002,64,2,64,109,-9,1202,-2,1,63,1008,63,39,63,1005,63,765,4,745,1001,64,1,64,1106,0,765,1002,64,2,64,109,10,21101,46,0,-5,1008,1011,48,63,1005,63,785,1106,0,791,4,771,1001,64,1,64,1002,64,2,64,109,-10,1208,0,36,63,1005,63,811,1001,64,1,64,1105,1,813,4,797,1002,64,2,64,109,7,1205,8,827,4,819,1105,1,831,1001,64,1,64,1002,64,2,64,109,-15,2108,27,4,63,1005,63,853,4,837,1001,64,1,64,1106,0,853,1002,64,2,64,109,14,1201,-3,0,63,1008,63,30,63,1005,63,877,1001,64,1,64,1106,0,879,4,859,1002,64,2,64,109,11,21107,47,46,-5,1005,1018,899,1001,64,1,64,1105,1,901,4,885,4,64,99,21101,0,27,1,21101,0,915,0,1105,1,922,21201,1,31783,1,204,1,99,109,3,1207,-2,3,63,1005,63,964,21201,-2,-1,1,21101,0,942,0,1106,0,922,21201,1,0,-1,21201,-2,-3,1,21101,0,957,0,1105,1,922,22201,1,-1,-2,1106,0,968,22102,1,-2,-2,109,-3,2105,1,0]
    # Quine
    program = [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
    assert(program == Computer(program).run())

    # 16-digit number
    out = Computer([1102,34915192,34915192,7,4,7,99,0]).run()
    assert(len(out) == 1)
    out = out[0]
    assert(out // 10**(16-1) > 0)
    assert(out // 10**(17-1) == 0)

    # Middle number - 1125899906842624
    assert(Computer([104,1125899906842624,99]).run()[0] == 1125899906842624)

    # Day 9 part 1
    assert(Computer(DAY_9_PROGRAM, inputs=[1]).run()[0] == 2350741403)

    # Day 9 part 2 - slow! (5 seconds or so)
    assert(Computer(DAY_9_PROGRAM, inputs=[2]).run()[0] == 53088)

def test11_robot():
    drawing_program = [3,8,1005,8,299,1106,0,11,0,0,0,104,1,104,0,3,8,102,-1,8,10,101,1,10,10,4,10,108,1,8,10,4,10,102,1,8,28,1006,0,85,1,106,14,10,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,0,10,4,10,101,0,8,58,1,1109,15,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,0,10,4,10,1002,8,1,84,3,8,102,-1,8,10,1001,10,1,10,4,10,108,1,8,10,4,10,1002,8,1,105,1006,0,48,3,8,1002,8,-1,10,1001,10,1,10,4,10,108,0,8,10,4,10,102,1,8,130,1006,0,46,1,1001,17,10,3,8,1002,8,-1,10,101,1,10,10,4,10,1008,8,0,10,4,10,1002,8,1,160,2,109,20,10,3,8,102,-1,8,10,1001,10,1,10,4,10,108,0,8,10,4,10,1002,8,1,185,3,8,102,-1,8,10,1001,10,1,10,4,10,108,1,8,10,4,10,1001,8,0,207,1006,0,89,2,1002,6,10,1,1007,0,10,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,1,10,4,10,101,0,8,241,2,4,14,10,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,1,10,4,10,101,0,8,267,1,1107,8,10,1,109,16,10,2,1107,4,10,101,1,9,9,1007,9,1003,10,1005,10,15,99,109,621,104,0,104,1,21101,0,387239486208,1,21102,316,1,0,1106,0,420,21101,0,936994976664,1,21102,327,1,0,1105,1,420,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,21102,1,29192457307,1,21102,1,374,0,1106,0,420,21101,0,3450965211,1,21101,0,385,0,1106,0,420,3,10,104,0,104,0,3,10,104,0,104,0,21102,1,837901103972,1,21101,408,0,0,1106,0,420,21102,867965752164,1,1,21101,0,419,0,1105,1,420,99,109,2,22102,1,-1,1,21102,40,1,2,21102,451,1,3,21102,1,441,0,1106,0,484,109,-2,2106,0,0,0,1,0,0,1,109,2,3,10,204,-1,1001,446,447,462,4,0,1001,446,1,446,108,4,446,10,1006,10,478,1102,0,1,446,109,-2,2105,1,0,0,109,4,1201,-1,0,483,1207,-3,0,10,1006,10,501,21101,0,0,-3,22101,0,-3,1,22102,1,-2,2,21101,1,0,3,21101,520,0,0,1106,0,525,109,-4,2106,0,0,109,5,1207,-3,1,10,1006,10,548,2207,-4,-2,10,1006,10,548,21201,-4,0,-4,1105,1,616,22101,0,-4,1,21201,-3,-1,2,21202,-2,2,3,21101,0,567,0,1106,0,525,22101,0,1,-4,21101,1,0,-1,2207,-4,-2,10,1006,10,586,21102,1,0,-1,22202,-2,-1,-2,2107,0,-3,10,1006,10,608,21202,-1,1,1,21102,608,1,0,106,0,483,21202,-2,-1,-2,22201,-4,-2,-4,109,-5,2105,1,0]
    brain = Computer(drawing_program, pause_on_output=True)
    grid = {}
    robot_location = (0,0)
    robot_facing = 'u'

    TURN_LEFT={'u':'l','l':'d','d':'r','r':'u'}
    TURN_RIGHT={'u':'r','r':'d','d':'l','l':'u'}
    TURN = {0:TURN_LEFT, 1:TURN_RIGHT}

    def read_camera(location, grid, brain):
        color = grid.get(location, 0) # 0=black
        brain.inputs.append(color)

    def advance(location, facing):
        if DEBUG:print(location, facing)
        if facing == 'u':
            location = (location[0], location[1]-1)
        elif facing == 'd':
            location = (location[0], location[1]+1)
        elif facing == 'l':
            location = (location[0]-1, location[1])
        elif facing == 'r':
            location = (location[0]+1, location[1])
        else:
            print("Bad direction:", facing)
            assert(False)

        return location

    # Start here
    grid[robot_location] = 1  # Start on white
    read_camera(robot_location, grid, brain)
    stop = False

    while not stop:
        color, stop = brain.run()  # Stops on output
        if stop:
            assert (color is None)
            break

        grid[robot_location] = color

        turn_direction, stop = brain.run()

        robot_facing = TURN[turn_direction][robot_facing]
        robot_location = advance(robot_location, robot_facing)

        read_camera(robot_location, grid, brain)

    #print(len(grid))

    def pretty_print_grid (grid):
        minx = min([a[0] for a in grid.keys()])
        maxx = max([a[0] for a in grid.keys()])
        miny = min([a[1] for a in grid.keys()])
        maxy = max([a[1] for a in grid.keys()])

        width = maxx-minx +1  # Extra 1 for the origin
        height = maxy-miny +1

        out=[]
        for y in range(height):
            out.append(['.']*width)

        for location in grid.keys():
            #print item
            if grid[location]:  # 1=white
                out[ location[1] -miny ][ location[0] -minx ] = '#'

        return ("\n".join(["".join([str(s) for s in row]) for row in out]))

    assert(pretty_print_grid(grid) == """..##...##...##..#....###...##....##.####...
.#..#.#..#.#..#.#....#..#.#..#....#.#......
.#..#.#....#..#.#....#..#.#.......#.###....
.####.#.##.####.#....###..#.##....#.#......
.#..#.#..#.#..#.#....#.#..#..#.#..#.#......
.#..#..###.#..#.####.#..#..###..##..####...""")

def tests ():
    global DEBUG
    test_day2()
    test_day5_1_examples()
    test_day5_1_puzzle()
    test_day5_2_tests()
    test_day5_2_puzzle()
    test_day7()

    # Slow test (6 seconds)
    #test_day_9()

    test11_robot()

    print("All tests passed")

if __name__ == "__main__":
    tests()