pub mod computer {
    pub struct Computer {
        ip: usize, // instruction pointer
        memory: Vec<i32>,
        inputs: Vec<i32>,
        outputs: Vec<i32>,
    }
    
    impl Computer {
        pub fn create_computer(program: Vec<i32>) -> Computer {
            Computer {
                ip : 0,
                memory : program,
                inputs: Vec::new(),
                outputs: Vec::new(),
            }
        }
    
        pub fn execute(&mut self) {
            loop {
                // println!("ip {}, instruction {:?}", &self.ip, &self.memory[self.ip..std::cmp::min(self.memory.len(), self.ip+10)]); // Debug only
                let (exit, _output) = Instruction::new(&self.memory[self.ip]).execute(self);
                
                if exit { break; }
            };
        }
    
        pub fn value_at(&self, location: usize) -> i32 {
            self.memory[location]
        }

        pub fn add_input(&mut self, input: i32) {
            self.inputs.push(input);
        }

        pub fn get_next_output(&mut self) -> i32 {
            self.outputs.remove(0)
        }

        pub fn get_last_output(&mut self) -> i32 {
            match self.outputs.pop() {
                Some(val) => val,
                None => panic!("No output to givE")
            }
        }
    }

    #[derive(Debug)]
    enum Mode {
        Immediate,
        Position,
    }

    #[derive(Debug)]
    enum Opcode {
        Add,
        Multiply,
        Input,
        Output,
        JumpIfTrue,
        JumpIfFalse,
        LessThan,
        Equal,
        Exit,
    }

    struct Instruction {
        opcode: Opcode,
        modes: Vec<Mode>,
    }

    impl Instruction {
        fn new(instruction: &i32) -> Instruction {
            let (modes, opcode) = (instruction/100, instruction%100);
            let opcode = match opcode {
                1 => Opcode::Add,
                2 => Opcode::Multiply,
                3 => Opcode::Input,
                4 => Opcode::Output,
                5 => Opcode::JumpIfTrue,
                6 => Opcode::JumpIfFalse,
                7 => Opcode::LessThan,
                8 => Opcode::Equal,
                99 => Opcode::Exit,
                _ => panic!("Unkonwn opcode: {}", opcode),
            };

            let n_modes = match opcode {
                Opcode::Add => 3,
                Opcode::Multiply => 3,
                Opcode::Input => 1,
                Opcode::Output => 1,
                Opcode::JumpIfTrue => 2,
                Opcode::JumpIfFalse => 2,
                Opcode::LessThan => 3,
                Opcode::Equal => 3,
                Opcode::Exit => 0,
            };
            Instruction { modes: Instruction::get_modes(modes, n_modes), opcode: opcode, }
        }

        fn get_modes(modes: i32, n: i32) -> Vec<Mode> {
            let mut v: Vec<Mode> = Vec::new();
            for p in 0..n as u32 {
                let mode: i32 = (modes / 10_i32.pow(p)) % (10_i32.pow(p+1));
                v.push( match mode {
                    0 => Mode::Position,
                    1 => Mode::Immediate,
                    _ => panic!("Unsupported mode! {}", mode)
                } );
            }
            v
        }

        fn execute(&self, computer: &mut Computer) -> (bool, bool) {
            match self.opcode {
                Opcode::Add => {
                    self.combine(computer, |a,b| a+b)
                },

                Opcode::Multiply => {
                    self.combine(computer, |a,b| a*b)
                },

                Opcode::Input => {
                    let addr = self.get_addr_for_param(0, computer);
                    computer.memory[addr] = computer.inputs.remove(0);
                    computer.ip += 2;
                    (false, false)
                },

                Opcode::Output => {
                    let addr = self.get_addr_for_param(0, computer);
                    let val = computer.memory[addr];
                    // println!("Output: {}", &val); // Debug only
                    computer.outputs.push(val);
                    computer.ip += 2;
                    (false, true)
                },

                Opcode::JumpIfTrue => {
                    self.jump_if(computer, |a| a!=0)
                },

                Opcode::JumpIfFalse => {
                    self.jump_if(computer, |a| a==0)
                },

                Opcode::LessThan => {
                    self.compare(computer, |a,b| a<b)
                },

                Opcode::Equal => {
                    self.compare(computer, |a,b| a==b)
                },

                Opcode::Exit => (true, false),
            }
        }

        fn get_addr_for_param(&self, param: usize, computer: &Computer) -> usize {
            match self.modes[param] {
                Mode::Immediate => computer.ip+1+param, // immediate mode
                Mode::Position => computer.memory[computer.ip+1+param] as usize,
            }
        }

        fn combine(&self, computer: &mut Computer, f: impl Fn(i32, i32) -> i32) -> (bool, bool) {
            let a = computer.value_at(self.get_addr_for_param(0, computer));
            let b = computer.value_at(self.get_addr_for_param(1, computer));
            let store_loc = *&computer.memory[computer.ip+3] as usize;
            let val = f(a, b);
            computer.memory[store_loc] = val;
            computer.ip += 4;

            (false, false)
        }

        fn compare(&self, computer: &mut Computer, f: impl Fn(i32, i32) -> bool) -> (bool, bool) {
            let a = computer.value_at(self.get_addr_for_param(0, computer));
            let b = computer.value_at(self.get_addr_for_param(1, computer));
            let store_loc = *&computer.memory[computer.ip+3] as usize;
            
            computer.memory[store_loc] = match f(a, b) { true => 1, false => 0, };
            computer.ip += 4;

            (false, false)
        }

        fn jump_if(&self, computer: &mut Computer, f: impl Fn(i32) -> bool) -> (bool, bool) {
            let test_val = computer.value_at(self.get_addr_for_param(0, computer));
            let jump_loc = computer.value_at(self.get_addr_for_param(1, computer));

            computer.ip = match f(test_val) { true => jump_loc as usize, false => computer.ip+3, };
            (false, false)
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::computer::Computer;

    #[test]
    fn day2_tests() {
        test_final_memory(vec![99,0,1,2,3], vec![99,0,1,2,3]);
    
        test_final_memory(vec![1,0,0,0,99], vec![2,0,0,0,99]);
        test_final_memory(vec![2,3,0,3,99], vec![2,3,0,6,99]);
        test_final_memory(vec![2,4,4,5,99,0], vec![2,4,4,5,99,9801]);
        test_final_memory(vec![1,1,1,4,99,5,6,0,99], vec![30,1,1,4,2,5,6,0,99]);
        test_final_memory(vec![1,9,10,3,2,3,11,0,99,30,40,50], vec![3500,9,10,70,2,3,11,0,99,30,40,50]);
    }

    #[test]
    fn day5_part_one_tests() {
        test_final_memory(vec![1101,100,-1,4,0], vec![1101,100,-1,4,99]);

        // Assorted input/output tests
        test_output_for_input(vec![3, 5, 4, 5, 99, -99], 0, 0); // output the input
        test_output_for_input(vec![3, 5, 4, 5, 99, -99], -11, -11); // output the input
        test_output_for_input(vec![3, 9, 101, 7, 9, 9, 4, 9, 99, -99], 0, 7); // output the input+7
    }
    #[test]
    fn day5_part_two_tests() {
        test_output_for_input(vec![3,9,8,9,10,9,4,9,99,-1,8], 7, 0); // equal to 8->1 (position mode)
        test_output_for_input(vec![3,9,8,9,10,9,4,9,99,-1,8], 8, 1); // equal to 8->1 (position mode)

        test_output_for_input(vec![3,3,1108,-1,8,3,4,3,99], -8, 0); // equal to 8 (immediate mode)
        test_output_for_input(vec![3,3,1108,-1,8,3,4,3,99], 8, 1); // equal to 8 (immediate mode)

        test_output_for_input(vec![3,9,7,9,10,9,4,9,99,-1,8], -1, 1); // less than 8->1 (position mode)
        test_output_for_input(vec![3,9,7,9,10,9,4,9,99,-1,8], 0, 1); // less than 8->1 (position mode)
        test_output_for_input(vec![3,9,7,9,10,9,4,9,99,-1,8], 7, 1); // less than 8->1 (position mode)
        test_output_for_input(vec![3,9,7,9,10,9,4,9,99,-1,8], 8, 0); // less than 8->1 (position mode)
        test_output_for_input(vec![3,9,7,9,10,9,4,9,99,-1,8], 9, 0); // less than 8->1 (position mode)

        test_output_for_input(vec![3,3,1107,-1,8,3,4,3,99], -8, 1); // less than 8 (immediate mode)
        test_output_for_input(vec![3,3,1107,-1,8,3,4,3,99], 8, 0); // less than 8 (immediate mode)
        test_output_for_input(vec![3,3,1107,-1,8,3,4,3,99], 9, 0); // less than 8 (immediate mode)

        test_output_for_input(vec![3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9], 0, 0); // Jump - output 0 if input is 0 (position mode)
        test_output_for_input(vec![3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9], -999, 1); // Jump - output 0 if input is 0 (position mode)
        
        test_output_for_input(vec![3,3,1105,-1,9,1101,0,0,12,4,12,99,1], 0, 0); // Jump - output 0 if input is 0 (immediate mode)
        test_output_for_input(vec![3,3,1105,-1,9,1101,0,0,12,4,12,99,1], 999, 1); // Jump - output 0 if input is 0 (immediate mode)

        test_output_for_input(vec![3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99],
            7, 999); // 999 for <8, 1000 for 8, 1001 for > 8
        test_output_for_input(vec![3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99],
            8, 1000); // 999 for <8, 1000 for 8, 1001 for > 8
        test_output_for_input(vec![3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99],
            9, 1001); // 999 for <8, 1000 for 8, 1001 for > 8
    }
    
    fn test_final_memory(input: Vec<i32>, answer: Vec<i32>) {
        let mut computer = Computer::create_computer(input);
        computer.execute();
        // assert!(output == answer, "Test failed: expected {:?} but got {:?} (input {:?})", answer, output, &input);
        let mut memory: Vec<i32> = Vec::new();
        for x in &answer {
            memory.push(*x);
        }
        assert!(memory == answer, "Test failed: expected {:?} but got {:?}", answer, memory);
    }

    fn test_output_for_input(program: Vec<i32>, input: i32, output: i32) {
        let mut computer = Computer::create_computer(program);
        computer.add_input(input);
        computer.execute();
        let result = computer.get_last_output();
        assert!(result == output, "Expected {}, got {}", output, result);
    }
}
