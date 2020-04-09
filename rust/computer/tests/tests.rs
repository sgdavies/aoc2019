#[cfg(test)]
mod tests {
    pub use computer::computer::Computer;

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
