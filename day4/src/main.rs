fn main() {
    // START = 165432, END = 707912
    let mut part_one_count = 0;
    let mut part_two_count = 0;

    // This is quite hacky - which we get away with because of being lucky in the number range.
    // Start: The minimum acceptable candidate after 165432 is 166666, so we only need to be clever when choosing d2 the first time.
    // End: The maximum acceptable candidate before 707912 is 699999, so we can stop as soon as d1 hits 7.
    for d1 in 1..7 {
        let d2_start = if d1==1 { 6 } else { d1 };
        for d2 in d2_start..10 {
            for d3 in d2..10 {
                for d4 in d3..10 {
                    for d5 in d4..10 {
                        for d6 in d5..10 {
                            if d1==d2 || d2==d3 || d3==d4 || d4==d5 || d5==d6 {
                                part_one_count += 1;
                            }
                            
                            if (d1==d2 && d2!=d3) || (d2==d3 && d1!=d2 && d3!=d4) || (d3==d4 && d2!=d3 && d4!=d5) || (d4==d5 && d3!=d4 && d5!=d6) || (d5==d6 && d4!=d5) {
                                part_two_count += 1;
                            }
                        }
                    }
                }
            }
        }
    }

    println!("{} {}", part_one_count, part_two_count);
}
