struct ProgramState {
    ip: usize, // instruction pointer
    memory: Vec<i32>,
}

fn main() {
    run_tests();

    // let mut program = vec![1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,5,19,23,1,23,5,27,1,27,13,31,1,31,5,35,1,9,35,39,2,13,39,43,1,43,10,47,1,47,13,51,2,10,51,55,1,55,5,59,1,59,5,63,1,63,13,67,1,13,67,71,1,71,10,75,1,6,75,79,1,6,79,83,2,10,83,87,1,87,5,91,1,5,91,95,2,95,10,99,1,9,99,103,1,103,13,107,2,10,107,111,2,13,111,115,1,6,115,119,1,119,10,123,2,9,123,127,2,127,9,131,1,131,10,135,1,135,2,139,1,10,139,0,99,2,0,14,0];
}

fn run_program(program: Vec<i32>) -> ProgramState {
    let mut state = ProgramState {
        ip : 0,
        memory : program,
    };

    loop {
        // execute instruction
        let opcode = *&state.memory[state.ip];
        match opcode {
            1 => { // add
                let a = value_at(&state.memory, *&state.memory[state.ip+1] as usize);
                let b = value_at(&state.memory, *&state.memory[state.ip+2] as usize);
                let store_loc = *&state.memory[state.ip+3] as usize;
                let val = a + b;
                state.memory[store_loc] = val;
                state.ip += 4;
            },

            2 => { // multiply
                let a = value_at(&state.memory, *&state.memory[state.ip+1] as usize);
                let b = value_at(&state.memory, *&state.memory[state.ip+2] as usize);
                let store_loc = *&state.memory[state.ip+3] as usize;
                let val = a * b;
                state.memory[store_loc] = val;
                state.ip += 4;
            },

            99 => break, // exit

            _ => panic!("Unknown opcode {} at ip {} of program {:?}", opcode, state.ip, state.memory),
        };
    };

    state
}

fn value_at(memory: &Vec<i32>, location: usize) -> i32 {
    memory[location]
}

fn run_tests() {
    run_test(vec![99,0,1,2,3], vec![99,0,1,2,3]);
    // run_test(vec![1,2,3,0,99], vec![1,2,3,0,99]);

    run_test(vec![1,0,0,0,99], vec![2,0,0,0,99]);
    run_test(vec![2,3,0,3,99], vec![2,3,0,6,99]);
    run_test(vec![2,4,4,5,99,0], vec![2,4,4,5,99,9801]);
    run_test(vec![1,1,1,4,99,5,6,0,99], vec![30,1,1,4,2,5,6,0,99]);
    run_test(vec![1,9,10,3,2,3,11,0,99,30,40,50], vec![3500,9,10,70,2,3,11,0,99,30,40,50]);
}

fn run_test(input: Vec<i32>, answer: Vec<i32>) {
    let final_state = run_program(input);
    // assert!(output == answer, "Test failed: expected {:?} but got {:?} (input {:?})", answer, output, &input);
    assert!(final_state.memory == answer, "Test failed: expected {:?} but got {:?}", answer, final_state.memory);
}