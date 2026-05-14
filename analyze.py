import csv
import math
from collections import defaultdict

# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def mean(vals):
    return sum(vals) / len(vals)

def stdev(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))

def moe(vals, z=1.96):
    """95% confidence interval margin of error."""
    if len(vals) < 2:
        return 0.0
    return z * stdev(vals) / math.sqrt(len(vals))

def moe_pct(vals, z=1.96):
    """MoE as a percentage of the mean — the rubric targets 5–10%."""
    m = mean(vals)
    if m == 0:
        return 0.0
    return (moe(vals, z) / m) * 100

def welch_t_p(a, b):
    """
    Two-sample Welch's t-test (two-tailed).
    Returns (t_stat, p_value_approx) using the normal approximation for
    large n, which is fine given n=30 per group.
    A p < 0.05 is conventionally considered statistically significant.
    """
    ma, mb = mean(a), mean(b)
    sa, sb = stdev(a), stdev(b)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None, None
    se = math.sqrt(sa**2 / na + sb**2 / nb)
    if se == 0:
        return None, None
    t = (ma - mb) / se
    # Normal approximation: good for n=30
    p = 2 * (1 - normal_cdf(abs(t)))
    return t, p

def normal_cdf(x):
    """Standard normal CDF via math.erf."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

data = defaultdict(list)

try:
    with open("results.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["language"], row["algorithm"], row["input_size"])
            data[key].append(float(row["time_sec"]))
except FileNotFoundError:
    print("results.csv not found — run run_tests.sh first.")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# Per-group summary, grouped by algorithm then size then language
# ---------------------------------------------------------------------------

algorithms = sorted({k[1] for k in data})
sizes_by_algo = {
    algo: sorted({k[2] for k in data if k[1] == algo}, key=lambda x: int(x))
    for algo in algorithms
}
languages = sorted({k[0] for k in data})

col_w = dict(lang=10, algo=15, size=12, n=5, mean=12, sd=10, moe=10, moepct=10)

def header_line():
    return (f"{'Lang':<{col_w['lang']}} {'Algorithm':<{col_w['algo']}} "
            f"{'Size':<{col_w['size']}} {'N':<{col_w['n']}} "
            f"{'Mean(s)':<{col_w['mean']}} {'StdDev':<{col_w['sd']}} "
            f"{'MoE 95%':<{col_w['moe']}} {'MoE%':<{col_w['moepct']}}")

sep = "-" * 84

for algo in algorithms:
    print(f"\n{'='*84}")
    print(f"  ALGORITHM: {algo}")
    print('='*84)
    print(header_line())
    print(sep)

    moe_pct_flags = []   # collect for rubric check at end

    for size in sizes_by_algo[algo]:
        for lang in languages:
            key = (lang, algo, size)
            vals = data.get(key, [])
            if not vals:
                continue
            m  = mean(vals)
            s  = stdev(vals)
            e  = moe(vals)
            ep = moe_pct(vals)
            flag = " ⚠ " if ep > 10 else ""
            moe_pct_flags.append((lang, algo, size, ep))

            print(f"{lang:<{col_w['lang']}} {algo:<{col_w['algo']}} "
                  f"{size:<{col_w['size']}} {len(vals):<{col_w['n']}} "
                  f"{m:<{col_w['mean']}.6f} {s:<{col_w['sd']}.6f} "
                  f"{e:<{col_w['moe']}.6f} {ep:<{col_w['moepct']}.2f}%{flag}")
        print(sep)  # blank separator between size groups

    # -------------------------------------------------------------------
    # Pairwise significance tests for each (size, lang pair)
    # -------------------------------------------------------------------
    print(f"\n  Pairwise Welch's t-test (p < 0.05 = statistically significant)")
    print(f"  {'Comparison':<30} {'Size':<12} {'t-stat':>8} {'p-value':>10} {'Sig?':>6}")
    print(f"  {'-'*68}")

    lang_pairs = [(languages[i], languages[j])
                  for i in range(len(languages))
                  for j in range(i+1, len(languages))]

    for size in sizes_by_algo[algo]:
        for la, lb in lang_pairs:
            a_vals = data.get((la, algo, size), [])
            b_vals = data.get((lb, algo, size), [])
            if not a_vals or not b_vals:
                continue
            t, p = welch_t_p(a_vals, b_vals)
            if t is None:
                continue
            sig = "YES" if p < 0.05 else "no"
            label = f"{la} vs {lb}"
            print(f"  {label:<30} {size:<12} {t:>8.3f} {p:>10.4f} {sig:>6}")

# ---------------------------------------------------------------------------
# Rubric MoE summary
# The rubric asks you to aim for a MoE "around 5–10%". This is a ceiling,
# not a floor — a low MoE simply means your data is consistent and your
# sample size is sufficient. Only flag groups ABOVE 10%, which would suggest
# too much variance or too few runs.
# ---------------------------------------------------------------------------
print(f"\n{'='*84}")
print("  MoE% RUBRIC CHECK  (must be <= ~10%; lower is better)")
print('='*84)
any_flag = False
for lang, algo, size, ep in sorted(moe_pct_flags):
    if ep > 10:
        print(f"  ⚠  {lang:<10} {algo:<15} size={size:<10} MoE%={ep:.2f}%  — TOO HIGH: consider more runs or check for outliers")
        any_flag = True
if not any_flag:
    print("  All groups at or below 10% MoE. ✓ (your data is well within the acceptable range)")
