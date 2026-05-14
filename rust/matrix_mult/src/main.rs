use std::env;
use std::sync::Arc;
use std::thread;
use std::time::Instant;

const NUM_THREADS: usize = 4;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <matrix_size>", args[0]);
        std::process::exit(1);
    }

    let size: usize = args[1].parse().expect("invalid size");

    let mut a = vec![0.0f64; size * size];
    let mut b = vec![0.0f64; size * size];

    for i in 0..size {
        for j in 0..size {
            a[i * size + j] = (i + j + 1) as f64;
            b[i * size + j] = (i as i64 - j as i64 + 1) as f64;
        }
    }

    let a = Arc::new(a);
    let b = Arc::new(b);

    let rows_per_thread = size / NUM_THREADS;
    let mut handles = vec![];

    let start = Instant::now();

    for t in 0..NUM_THREADS {
        let a = Arc::clone(&a);
        let b = Arc::clone(&b);
        let start_row = t * rows_per_thread;
        let end_row = if t == NUM_THREADS - 1 { size } else { start_row + rows_per_thread };

        handles.push(thread::spawn(move || {
            let mut partial = vec![0.0f64; (end_row - start_row) * size];
            for i in start_row..end_row {
                for j in 0..size {
                    let mut sum = 0.0;
                    for k in 0..size {
                        sum += a[i * size + k] * b[k * size + j];
                    }
                    partial[(i - start_row) * size + j] = sum;
                }
            }
            (start_row, partial)
        }));
    }

    let mut c = vec![0.0f64; size * size];
    for h in handles {
        let (start_row, partial) = h.join().unwrap();
        let rows = partial.len() / size;
        for i in 0..rows {
            for j in 0..size {
                c[(start_row + i) * size + j] = partial[i * size + j];
            }
        }
    }

    println!("{:.6}", start.elapsed().as_secs_f64());
}
