use std::env;
use std::thread;
use std::time::Instant;

const NUM_THREADS: usize = 4;

fn merge_sort(arr: &mut Vec<i32>) {
    let n = arr.len();
    if n <= 1 {
        return;
    }
    let mid = n / 2;
    let mut left = arr[..mid].to_vec();
    let mut right = arr[mid..].to_vec();

    merge_sort(&mut left);
    merge_sort(&mut right);

    let (mut i, mut j, mut k) = (0, 0, 0);
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {
            arr[k] = left[i];
            i += 1;
        } else {
            arr[k] = right[j];
            j += 1;
        }
        k += 1;
    }
    while i < left.len() { arr[k] = left[i]; i += 1; k += 1; }
    while j < right.len() { arr[k] = right[j]; j += 1; k += 1; }
}

fn merge_vecs(left: Vec<i32>, right: Vec<i32>) -> Vec<i32> {
    let mut out = Vec::with_capacity(left.len() + right.len());
    let (mut i, mut j) = (0, 0);
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] { out.push(left[i]); i += 1; }
        else { out.push(right[j]); j += 1; }
    }
    out.extend_from_slice(&left[i..]);
    out.extend_from_slice(&right[j..]);
    out
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <array_size>", args[0]);
        std::process::exit(1);
    }

    let n: usize = args[1].parse().expect("invalid size");
    let arr: Vec<i32> = (0..n as i32).map(|x| (x.wrapping_mul(1103515245).wrapping_add(12345)).abs() % 1000000).collect();

    let chunk = n / NUM_THREADS;
    let chunks: Vec<Vec<i32>> = (0..NUM_THREADS).map(|t| {
        let s = t * chunk;
        let e = if t == NUM_THREADS - 1 { n } else { s + chunk };
        arr[s..e].to_vec()
    }).collect();

    let start = Instant::now();

    let handles: Vec<_> = chunks.into_iter().map(|mut c| {
        thread::spawn(move || { merge_sort(&mut c); c })
    }).collect();

    let mut sorted: Vec<Vec<i32>> = handles.into_iter().map(|h| h.join().unwrap()).collect();

    // merge all sorted chunks into one
    while sorted.len() > 1 {
        let mut next = vec![];
        {
            let mut iter = sorted.drain(..);
            while let Some(l) = iter.next() {
                match iter.next() {
                    Some(r) => next.push(merge_vecs(l, r)),
                    None => next.push(l),
                }
            }
        }
        sorted = next;
    }

    println!("{:.6}", start.elapsed().as_secs_f64());
}
