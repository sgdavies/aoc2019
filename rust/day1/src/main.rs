fn main() {
    println!("Part one:");
    let test_masses = [(12u32,2u32,2u32), (14,2,2), (1969,654,966), (100756,33583,50346)];
    let masses = [137503u32,60363,103031,141000,101650,76081,139069,63717,135021,66034,53912,83417,125978,73206,77497,108822,133339,113618,91973,88741,109942,96523,95973,56595,118638,63936,101635,149154,85522,140962,108196,105804,148464,68429,146808,82541,85581,117253,117900,83457,103354,123875,88412,108573,140651,103774,95291,91290,98690,87761,122907,91499,141746,127300,114866,75472,65369,50978,119756,144115,92483,146317,100770,124156,109933,138037,101126,58517,83653,135656,111483,82784,107459,106641,138030,53599,123886,74425,96919,65410,63823,148278,133753,106661,51147,120571,77900,131827,107882,149359,127565,67109,131547,114874,130493,94905,138654,58504,79591,133856];

    for (mass,answer,_) in test_masses.iter() {
        let fuel = fuel_for_module(&mass);
        println!("Fuel needed for module of mass {} is: {}", mass, fuel);
        assert!(fuel == *answer);
    }

    let mut sum = 0;

    for mass in masses.iter() {
        sum += fuel_for_module(&mass);
    }

    println!("Total fuel needed: {}", sum); // 3457281

    println!("Part two:");
    for (mass,_,answer) in test_masses.iter() {
        let fuel = fuel_for_module_plus_fuel(&mass);
        println!("Fuel needed for module of mass {} is: {}", mass, fuel);
        assert!(fuel == *answer);
    }

    let mut sum = 0;

    for mass in masses.iter() {
        sum += fuel_for_module_plus_fuel(&mass);
    }

    println!("Total fuel needed: {}", sum); // 5183030
}

fn fuel_for_module(mass: &u32) -> u32 {
    fuel_for_mass(mass)
}

fn fuel_for_module_plus_fuel(mass: &u32) -> u32 {
    let mut total = 0;
    let mut ffm = fuel_for_mass(mass);

    while ffm > 0 {
        total += ffm;
        ffm = fuel_for_mass(&ffm);
    }

    total
}

fn fuel_for_mass(mass: &u32) -> u32 {
    let third = mass / 3;
    if third >= 2 {
        third - 2
    }
    else {
        0
    }
}
