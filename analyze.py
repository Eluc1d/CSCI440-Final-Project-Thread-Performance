import csv
import math
from collections import defaultdict

def mean(vals):
    return sum(vals) / len(vals)

def stdev(vals):
    m = mean(vals)
    return math.sqrt(sum((v - m)**2 for v in vals) / (len(vals) - 1))

def moe(vals, z=1.96):
    # 95% confidence interval
    return z * stdev(vals) / math.sqrt(len(vals))

data = defaultdict(list)

with open("results.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row["language"], row["algorithm"], row["input_size"])
        data[key].append(float(row["time_sec"]))

print(f"{'Lang':<10} {'Algorithm':<15} {'Size':<12} {'N':<5} {'Mean(s)':<12} {'StdDev':<10} {'MoE 95%':<10}")
print("-" * 76)

for key in sorted(data.keys()):
    lang, algo, size = key
    vals = data[key]
    m = mean(vals)
    s = stdev(vals) if len(vals) > 1 else 0.0
    e = moe(vals) if len(vals) > 1 else 0.0
    print(f"{lang:<10} {algo:<15} {size:<12} {len(vals):<5} {m:<12.6f} {s:<10.6f} {e:<10.6f}")
