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
