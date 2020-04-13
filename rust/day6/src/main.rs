use std::collections::HashMap;
use std::fs;

fn main() {
    // Part one
    let example_input = fs::read_to_string("example.txt").expect("Failed to read example file");
    let example = count_orbits(&example_input);
    let expected = 42;
    assert_eq!(example, expected, "Example: {} vs {}", example, expected);

    let puzzle_input = fs::read_to_string("puzzle.txt").expect("Failed to read puzzle input");
    println!("Part one answer: {}", count_orbits(&puzzle_input)); // 119831

    // Part two
    let example = count_transfers(&fs::read_to_string("example2.txt").expect("Failed to read second example file"));
    let expected = 4;
    assert_eq!(example, expected, "Example: {} vs {}", example, expected);

    println!("Part two answer: {}", count_transfers(&puzzle_input)); // 322
}

fn parse_orbits(input: &str) -> Vec<(&str, &str)> {
    // Read input and return list of (parent, child) relationships
    let mut orbits = Vec::new();
    for orbit in input.lines() {
        let parts: Vec<&str> = orbit.split(')').collect();
        orbits.push( (parts[0], parts[1]) );
    }
    orbits
}

fn count_orbits(input: &str) -> u32 {
    let mut orbits = HashMap::new();
    let relations = parse_orbits(input);
    for (parent, satellite) in relations {
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

fn count_transfers(input: &str) -> u32 {
    let relations = parse_orbits(input);

    // Build a list of parents from each of YOU and SAN to COM, then find out where they intersect
    // Start with a map of all child->parent relations
    let mut parents = HashMap::new();
    for (parent, child) in relations {
        parents.insert(child, parent);
    }

    let mut san_ancestors = HashMap::new();
    for (ix, anc) in ancestors("SAN", &parents).iter().enumerate() {
        san_ancestors.insert(anc.clone(), ix);
    }

    for (ix, anc) in ancestors("YOU", &parents).iter().enumerate() {
        if san_ancestors.contains_key(anc) {
            return (ix + san_ancestors.get(anc).expect("'get' failed after 'contains'!")) as u32;
        }
    }

    panic!("Couldn't find common ancestor!");
}

fn ancestors<'a>(body: &str, parents: &'a HashMap<&'a str, &str>) -> Vec<&'a str> {
    let mut collector = Vec::new();
    ancestors_rec(body, parents, &mut collector);
    collector
}

fn ancestors_rec<'b>(body: &str, parents: &HashMap<&str, &'b str>, mut collector: &mut Vec<&'b str>) {
    match parents.get(body) {
        Some(parent) => {
            collector.push(&parent);
            ancestors_rec(&parent, parents, &mut collector);
        },
        None => (),
    }
}