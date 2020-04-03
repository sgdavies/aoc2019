pub mod computer {
    pub struct Computer {
        ip: usize, // instruction pointer
        memory: Vec<i32>,
    }
    
    impl Computer {
        pub fn create_computer(program: Vec<i32>) -> Computer {
            Computer {
                ip : 0,
                memory : program,
            }
        }
    
        pub fn execute(&mut self) {
            loop {
                // execute instruction
                let instruction = Instruction::new(&self.memory[self.ip]);
                match instruction.opcode {
                    1 => { // add
                        let a = self.value_at(*&self.memory[self.ip+1] as usize);
                        let b = self.value_at(*&self.memory[self.ip+2] as usize);
                        let store_loc = *&self.memory[self.ip+3] as usize;
                        let val = a + b;
                        self.memory[store_loc] = val;
                        self.ip += 4;
                    },
    
                    2 => { // multiply
                        let a = self.value_at(*&self.memory[self.ip+1] as usize);
                        let b = self.value_at(*&self.memory[self.ip+2] as usize);
                        let store_loc = *&self.memory[self.ip+3] as usize;
                        let val = a * b;
                        self.memory[store_loc] = val;
                        self.ip += 4;
                    },
    
                    99 => break, // exit
    
                    _ => panic!("Unknown opcode {} at ip {} of program {:?}", instruction.opcode, self.ip, self.memory),
                };
            };
        }
    
        pub fn value_at(&self, location: usize) -> i32 {
            self.memory[location]
        }
    }

    struct Instruction {
        opcode: i32,
        modes: Vec<bool>,
    }

    impl Instruction {
        fn new(instruction: &i32) -> Instruction {
            let (modes, opcode) = (instruction/100, instruction%100);
            let n_modes = match opcode {
                1 => 3,
                2 => 3,
                _ => 0,
            };
            Instruction { modes: Instruction::get_modes(modes, n_modes), opcode: opcode, }
        }

        fn get_modes(modes: i32, n: i32) -> Vec<bool> {
            let mut v: Vec<bool> = Vec::new();
            for p in 0..n as u32 {
                v.push( (modes / 10_i32.pow(p)) % (10_i32.pow(p+1)) == 1 );
            }
            v
        }
    }
}