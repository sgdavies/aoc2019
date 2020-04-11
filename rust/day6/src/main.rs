use std::collections::HashMap;

fn main() {
    let example = "COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L";
    let example = count_orbits(example);
    let expected = 42;
    assert_eq!(example, expected, "Example: {} vs {}", example, expected);
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
        None => (),
    }
    
    total
}
