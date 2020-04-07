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
                // execute instruction
                let instruction = Instruction::new(&self.memory[self.ip]);
                match instruction.opcode {
                    1 => { // add
                        let a_addr = match instruction.modes[0] {
                            Mode::Immediate => self.ip+1, // immediate mode
                            Mode::Position => self.memory[self.ip+1] as usize,
                        };
                        let b_addr = match instruction.modes[1] {
                            Mode::Immediate => self.ip+2, // immediate mode
                            Mode::Position => self.memory[self.ip+2] as usize,
                        };
                        let a = self.value_at(a_addr);
                        let b = self.value_at(b_addr);
                        let store_loc = *&self.memory[self.ip+3] as usize;
                        let val = a + b;
                        self.memory[store_loc] = val;
                        self.ip += 4;
                    },
    
                    2 => { // multiply
                        let a_addr = match instruction.modes[0] {
                            Mode::Immediate => self.ip+1, // immediate mode
                            Mode::Position => self.memory[self.ip+1] as usize,
                        };
                        let b_addr = match instruction.modes[1] {
                            Mode::Immediate => self.ip+2, // immediate mode
                            Mode::Position => self.memory[self.ip+2] as usize,
                        };
                        let a = self.value_at(a_addr);
                        let b = self.value_at(b_addr);
                        let store_loc = *&self.memory[self.ip+3] as usize;
                        let val = a * b;
                        self.memory[store_loc] = val;
                        self.ip += 4;
                    },

                    3 => { // read input
                        let addr = match instruction.modes[0] {
                            Mode::Immediate => self.ip+1, // immediate mode
                            Mode::Position => self.memory[self.ip+1] as usize,
                        };
                        self.memory[addr] = self.inputs.remove(0);
                        self.ip += 2;
                    },

                    4 => { // append output
                        let addr = match instruction.modes[0] {
                            Mode::Immediate => self.ip+1, // immediate mode
                            Mode::Position => self.memory[self.ip+1] as usize,
                        };
                        let val = self.memory[addr];
                        // println!("Output: {}", &val); // Debug only
                        self.outputs.push(val);
                        self.ip += 2;
                    }
    
                    99 => break, // exit
    
                    _ => panic!("Unknown opcode {} at ip {} of program {:?}", instruction.opcode, self.ip, self.memory),
                };
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

    struct Instruction {
        opcode: i32,
        modes: Vec<Mode>,
    }

    impl Instruction {
        fn new(instruction: &i32) -> Instruction {
            let (modes, opcode) = (instruction/100, instruction%100);
            let n_modes = match opcode {
                1 => 3,
                2 => 3,
                3 => 1,
                4 => 1,
                _ => 0,
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
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
