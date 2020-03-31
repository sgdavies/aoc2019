#[derive(Debug)]
enum Direction {
    U, D, L, R,
}

struct SegmentDefinition(Direction, i32);
struct Extents {
    minx: i32, maxx: i32, miny: i32, maxy: i32,
}

struct Wire {
    segments: Vec<SegmentDefinition>,
    extents: Extents,
}

impl Wire {
    fn from_string(description: &str) -> Wire {
        let mut vec = Vec::new();
        for segment in description.split(',') {
            let (dir, dist) = (&segment[0..1], segment[1..].parse::<i32>().unwrap());
            let dir = match dir {
                "U" => Direction::U,
                "D" => Direction::D,
                "L" => Direction::L,
                "R" => Direction::R,
                _ => panic!("Unsupported direction: {}", dir),
            };
            vec.push(SegmentDefinition(dir, dist));
        }

        let extents = Wire::find_extents(&vec);
        Wire{ segments: vec, extents: extents, }
    }

    fn find_extents(segments: &Vec<SegmentDefinition>) -> Extents {
        // TODO implement
        Extents{minx: 0, maxx: 0, miny: 0, maxy: 0}
    }
}

fn main() {
    run_tests();
}

fn get_distance(wire_one: &str, wire_two: &str) -> i32 {
    let wire_one = Wire::from_string(wire_one);
    let wire_two = Wire::from_string(wire_two);
    6
}

fn wire_from_string(wire: &str) -> Vec<SegmentDefinition> {
    let mut vec = Vec::new();
    for segment in wire.split(',') {
        let (dir, dist) = (&segment[0..1], segment[1..].parse::<i32>().unwrap());
        let dir = match dir {
            "U" => Direction::U,
            "D" => Direction::D,
            "L" => Direction::L,
            "R" => Direction::R,
            _ => panic!("Unsupported direction: {}", dir),
        };
        vec.push(SegmentDefinition(dir, dist));
    }
    vec
}

fn run_tests() {
    run_test("R8,U5,L5,D3", "U7,R6,D4,L4", 6);
    run_test("R75,D30,R83,U83,L12,D49,R71,U7,L72", "U62,R66,U55,R34,D71,R55,D58,R83", 159);
    run_test("R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51", "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7", 135);

    println!("All tests pass!");
}

fn run_test(wire_one: &str, wire_two: &str, answer: i32) {
    let distance = get_distance(wire_one, wire_two);
    assert_eq!(distance, answer, "Failed: {} != {} for wires {} and {}", distance, answer, wire_one, wire_two);
}