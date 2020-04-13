use std::collections::HashMap;
use std::fs;

fn main() {
    let example_input = fs::read_to_string("example.txt").expect("Failed to read example file");
    let example = count_orbits(&example_input);
    let expected = 42;
    assert_eq!(example, expected, "Example: {} vs {}", example, expected);

    let puzzle_input = fs::read_to_string("puzzle.txt").expect("Failed to read puzzle input");
    println!("Part one answer: {}", count_orbits(&puzzle_input)); // 119831
}

fn count_orbits(input: &str) -> u32 {
    let mut orbits = HashMap::new();
    for orbit in input.lines() {
        let parts: Vec<&str> = orbit.split(')').collect();
        let (parent, satellite) = (parts[0], parts[1]);
        let satellite_list = orbits.entry(parent).or_insert(Vec::new());
        satellite_list.push(satellite);
    }

    count_from(&orbits, "COM", 0)
}

fn count_from(orbits: &HashMap<&str, Vec<&str>>, parent: &str, depth: u32) -> u32 {
    let mut total = depth;

    match orbits.get(&parent) {
        Some(v) => { 
            for child in v.iter() {
                total += count_from(&orbits, child, depth+1);
            }
        },
        None => (), // This is a leaf planet (no children)
    }
    
    total
}
