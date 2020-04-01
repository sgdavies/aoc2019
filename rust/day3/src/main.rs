use std::collections::HashMap;

#[derive(Debug)]
enum Direction {
    U, D, L, R,
}

struct SegmentDefinition {
    direction: Direction, 
    distance: i32,
}

#[derive(PartialEq, Eq, Hash, Clone, Debug)]
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn manhatten_distance(&self, other: &Point) -> i32 {
        (self.x - other.x).abs() + (self.y - other.y).abs()
    }
}

struct Wire {
    segments: Vec<SegmentDefinition>,
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
            vec.push(SegmentDefinition { direction: dir, distance: dist, });
        }

        Wire{ segments: vec, }
    }

    fn trace_path(&self, circuit_board: &mut HashMap<Point,u32>) {
        // Don't insert the origin
        let mut location = Point { x: 0, y: 0, };

        for segment in &self.segments {
            self.trace_segment(&segment, &mut location, circuit_board);
        }
    }

    fn trace_segment(&self, segment: &SegmentDefinition, location: &mut Point, circuit_board: &mut HashMap<Point,u32>) {
        for _ in 0..segment.distance {
            match segment.direction {
                Direction::U => location.y += 1,
                Direction::D => location.y -= 1,
                Direction::L => location.x += 1,
                Direction::R => location.x -= 1,
            }

            let visited = circuit_board.entry(location.clone()).or_insert(0);
            *visited += 1;
        }
    }
}

fn main() {
    run_tests();
}

fn get_distance(wire_one: &str, wire_two: &str) -> i32 {
    let wire_one = Wire::from_string(wire_one);
    let wire_two = Wire::from_string(wire_two);

    let mut circuit_board: HashMap<Point,u32> = HashMap::new();

    wire_one.trace_path(&mut circuit_board);
    wire_two.trace_path(&mut circuit_board);

    for (k, v) in circuit_board.iter()
        .filter(|&(k, v)| *v > 1) {
            // Map to manhatten distances, then sort, then print closest distance
            println!("{:?} = {}", k, v);
        }
    6 // replace with actual value
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