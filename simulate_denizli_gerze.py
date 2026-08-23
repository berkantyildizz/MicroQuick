#!/usr/bin/env python3
"""
Generates a SIMULATED microsatellite genotype data set for the Turkish native
chicken breeds Denizli and Gerze, for use as a demonstration and benchmark data
set for MicroQuick.

THIS DATA SET IS SIMULATED. No bird was genotyped to produce it. It must never
be presented as observed data.

What is taken from the literature:
  * the 12 loci, all members of the ISAG/FAO recommended chicken panel
  * the observed fragment-size range of each locus (bp), listed below with its
    source, so that every simulated allele call falls inside a size window that
    has actually been reported for chicken
  * the sampling design: 5 subpopulations, 25 birds each, 125 birds total,
    following Kaya & Yildiz (2008), who genotyped 125 birds from three Denizli
    and two Gerze subpopulations
  * target diversity parameters, so that the simulated data reproduce the
    published summary statistics for these breeds rather than arbitrary ones:
      mean Na  ~ 7.5     (Kaya & Yildiz 2008)
      mean He  ~ 0.665   (Kaya & Yildiz 2008)
      mean PIC ~ 0.610   (Kaya & Yildiz 2008)
      He Denizli ~ 0.656, He Gerze ~ 0.475   (Kaya & Yildiz 2008)
      FIS ~ 0.20         (Zanetti et al. 2017, Denizli subpopulations)
      global fixation index ~ 0.30  (Kaya & Yildiz 2008)

What is NOT taken from the literature:
  * the individual genotypes themselves. Allele frequencies are drawn from a
    Dirichlet distribution over each locus's reported size grid, then made to
    diverge among subpopulations under the Balding-Nichols model. Genotypes are
    then sampled with an inbreeding coefficient and a missing-call rate.

Sources for the fragment-size ranges
  Z17 = Zanetti et al. (2017) Ital J Anim Sci 17:57-63, Table 2 (Denizli)
  K14 = Seo et al. / Korean 30-marker chicken panel, allele size column
  All loci are dinucleotide repeats, so alleles are placed on a 2 bp grid.
"""
import numpy as np, openpyxl, json

RNG = np.random.default_rng(20260818)   # fixed seed: the file is reproducible

# locus: (min_bp, max_bp, n_alleles_in_ancestral_pool, source)
PANEL = {
    "MCW0034": (222, 246, 11, "Z17"),
    "ADL0268": (101, 119, 8, "Z17"),
    "LEI0094": (251, 285, 14, "Z17"),
    "MCW0069": (154, 178, 8, "Z17"),
    "MCW0037": (152, 158, 4, "K14"),
    "LEI0166": (251, 263, 7, "Z17"),
    "MCW0206": (215, 245, 13, "K14"),
    "ADL0278": (110, 126, 9, "Z17"),
    "MCW0248": (195, 243, 11, "Z17"),
    "MCW0111": (98, 112, 8, "K14"),
    "MCW0216": (141, 151, 5, "Z17"),
    "MCW0295": (84, 98, 8, "K14"),
}

SUBPOPS = [("Denizli_1", 25), ("Denizli_2", 25), ("Denizli_3", 25),
           ("Gerze_1", 25), ("Gerze_2", 25)]
BREED = {"Denizli_1": "Denizli", "Denizli_2": "Denizli", "Denizli_3": "Denizli",
         "Gerze_1": "Gerze", "Gerze_2": "Gerze"}

# Drift is hierarchical: ancestral pool -> breed -> subpopulation. This is what
# makes subpopulations of the same breed cluster together, as they do in the
# published analyses, rather than each drifting off independently.
THETA_BREED = {"Denizli": 0.07, "Gerze": 0.30}
DROP_BREED  = {"Denizli": 0.10, "Gerze": 0.45}
THETA_SUB   = 0.045
DROP_SUB    = 0.05

# Gerze is the more bottlenecked breed (He 0.475 vs 0.656), so it is given a
# stronger drift coefficient and a higher chance of losing rare alleles.

FIS = {"Denizli_1": 0.18, "Denizli_2": 0.20, "Denizli_3": 0.17,
       "Gerze_1": 0.24, "Gerze_2": 0.22}
# prob. a rare allele is lost during the corresponding drift step
MISSING = 0.025                              # per-genotype missing-call rate


def ancestral(lo, hi, k):
    """k allele sizes on the 2 bp grid inside the reported range, with a
    frequency spectrum skewed towards a few common alleles, as is typical of
    microsatellites in domestic breeds."""
    grid = np.arange(lo, hi + 1, 2)
    if k > len(grid):
        k = len(grid)
    sizes = np.sort(RNG.choice(grid, size=k, replace=False))
    p = RNG.dirichlet(np.full(k, 0.68))
    return sizes, p


def drifted(p, theta, drop):
    """Balding-Nichols divergence, then stochastic loss of rare alleles."""
    q = RNG.dirichlet(p * (1 - theta) / theta)
    rare = q < 0.08
    lost = rare & (RNG.random(len(q)) < drop)
    if (~lost).sum() < 2:                 # keep every locus polymorphic
        keep = np.argsort(q)[::-1][:2]
        lost[:] = True
        lost[keep] = False
    q[lost] = 0.0
    s = q.sum()
    return q / s if s > 0 else p


def draw_genotype(sizes, q, fis):
    """Sample a diploid genotype; with probability FIS the two alleles are
    identical by descent, which produces the heterozygote deficit reported for
    these breeds."""
    a = RNG.choice(sizes, p=q)
    b = a if RNG.random() < fis else RNG.choice(sizes, p=q)
    return (int(a), int(b)) if RNG.random() > 0.5 else (int(b), int(a))


# ---------------------------------------------------------------------------
loci = list(PANEL)
anc = {L: ancestral(*PANEL[L][:3]) for L in loci}
breedq = {b: {L: drifted(anc[L][1], THETA_BREED[b], DROP_BREED[b]) for L in loci}
          for b in ("Denizli", "Gerze")}
subq = {sp: {L: drifted(breedq[BREED[sp]][L], THETA_SUB, DROP_SUB) for L in loci}
        for sp, _ in SUBPOPS}

rows, meta = [], []
for sp, n in SUBPOPS:
    for i in range(1, n + 1):
        ind = f"{sp}_{i:02d}"
        g = []
        for L in loci:
            sizes, _ = anc[L]
            if RNG.random() < MISSING:
                g += ["?", "?"]
            else:
                a, b = draw_genotype(sizes, subq[sp][L], FIS[sp])
                g += [a, b]
        rows.append([sp, ind] + g)
        meta.append(sp)

header = ["Population", "individual"]
for L in loci:
    header += [f"{L}(1)", f"{L}(2)"]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Genotypes"
ws.append(header)
for r in rows:
    ws.append(r)
ws.freeze_panes = "C2"

# A README sheet travels with the file so the simulated status cannot be lost
# if the spreadsheet is separated from the paper.
rm = wb.create_sheet("README")
for line in [
    ["SIMULATED DATA SET - NOT OBSERVED GENOTYPES"],
    [""],
    ["This file contains simulated microsatellite genotypes for the Turkish"],
    ["native chicken breeds Denizli and Gerze. No bird was genotyped to"],
    ["produce it. It exists to demonstrate and benchmark the MicroQuick"],
    ["software and must not be used as evidence about these breeds."],
    [""],
    ["Design: 5 subpopulations (3 Denizli, 2 Gerze), 25 birds each, 125 total,"],
    ["12 loci from the ISAG/FAO recommended chicken panel."],
    [""],
    ["Allele sizes are constrained to fragment-size ranges reported in the"],
    ["literature for each locus:"],
    [""],
    ["Locus", "Range (bp)", "Source"],
] + [[L, f"{PANEL[L][0]}-{PANEL[L][1]}", PANEL[L][3]] for L in loci] + [
    [""],
    ["Z17 = Zanetti et al. (2017) Italian Journal of Animal Science 17:57-63"],
    ["K14 = Korean 30-marker chicken panel, allele size column"],
    [""],
    ["Diversity parameters were tuned to reproduce the values published by"],
    ["Kaya & Yildiz (2008) Biochemical Genetics 46:480-491 for these breeds."],
    [""],
    ["Generator: simulate_denizli_gerze.py, seed 20260818 (reproducible)."],
]:
    rm.append(line)

wb.save("SSR_Denizli_Gerze_simulated.xlsx")

# quick sanity report -------------------------------------------------------
summary = {}
for L_i, L in enumerate(loci):
    col1, col2 = 2 + 2 * L_i, 3 + 2 * L_i
    alle = [r[c] for r in rows for c in (col1, col2) if r[c] != "?"]
    from collections import Counter
    cnt = Counter(alle); n = len(alle)
    p = np.array([v / n for v in cnt.values()])
    he = 1 - (p ** 2).sum()
    pairs = [(r[col1], r[col2]) for r in rows if r[col1] != "?"]
    ho = sum(1 for a, b in pairs if a != b) / len(pairs)
    summary[L] = dict(Na=len(cnt), He=round(float(he), 3), Ho=round(ho, 3))

print(f"{'locus':10} {'Na':>4} {'Ho':>7} {'He':>7}")
for L, s in summary.items():
    print(f"{L:10} {s['Na']:4d} {s['Ho']:7.3f} {s['He']:7.3f}")
print(f"{'MEAN':10} {np.mean([s['Na'] for s in summary.values()]):4.1f} "
      f"{np.mean([s['Ho'] for s in summary.values()]):7.3f} "
      f"{np.mean([s['He'] for s in summary.values()]):7.3f}")

for breed, sps in [("Denizli", ["Denizli_1", "Denizli_2", "Denizli_3"]),
                   ("Gerze", ["Gerze_1", "Gerze_2"])]:
    hes = []
    for L_i, L in enumerate(loci):
        c1, c2 = 2 + 2 * L_i, 3 + 2 * L_i
        alle = [r[c] for r in rows if r[0] in sps for c in (c1, c2) if r[c] != "?"]
        from collections import Counter
        cnt = Counter(alle); n = len(alle)
        p = np.array([v / n for v in cnt.values()])
        hes.append(1 - (p ** 2).sum())
    print(f"{breed:8} He = {np.mean(hes):.3f}")
print("\nWritten: SSR_Denizli_Gerze_simulated.xlsx")
