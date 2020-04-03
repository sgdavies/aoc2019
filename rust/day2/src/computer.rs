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
                let opcode = *&self.memory[self.ip];
                match opcode {
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
    
                    _ => panic!("Unknown opcode {} at ip {} of program {:?}", opcode, self.ip, self.memory),
                };
            };
        }
    
        pub fn value_at(&self, location: usize) -> i32 {
            self.memory[location]
        }
    }   
}