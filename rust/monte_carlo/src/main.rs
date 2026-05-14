use std::env;
use std::thread;
use std::time::Instant;

const NUM_THREADS: usize = 4;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <num_points>", args[0]);
        std::process::exit(1);
    }

    let total: u64 = args[1].parse().expect("invalid number");
    let per_thread = total / NUM_THREADS as u64;
    let mut handles = vec![];

    let start = Instant::now();

    for t in 0..NUM_THREADS {
        // each thread gets its own seed so they don't produce identical sequences
        let seed = 987654321u64 ^ (t as u64 * 1234567891);

        handles.push(thread::spawn(move || {
            let mut s = seed;
            let mut inside = 0u64;

            for _ in 0..per_thread {
                // LCG to avoid pulling in external crates
                s = s.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                let x = ((s >> 32) as f64) / (u32::MAX as f64);
                s = s.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                let y = ((s >> 32) as f64) / (u32::MAX as f64);

                if x*x + y*y <= 1.0 {
                    inside += 1;
                }
            }
            inside
        }));
    }

    let total_inside: u64 = handles.into_iter().map(|h| h.join().unwrap()).sum();
    let elapsed = start.elapsed().as_secs_f64();

    eprintln!("pi ~ {:.5}", 4.0 * total_inside as f64 / total as f64);
    println!("{:.6}", elapsed);
}
