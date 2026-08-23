# Benchmark data set

`SSR_Denizli_Gerze_simulated.xlsx` — 125 individuals, 12 loci, 5 subpopulations.

**This data set is simulated. No bird was genotyped to produce it.** It exists so that
MicroQuick can be exercised on a matrix whose generating parameters are known, and so
that the results in the software paper can be reproduced exactly. It must not be cited as
evidence about Denizli or Gerze chickens.

## Why simulated rather than observed

With observed data you can check that a program runs. With simulated data you can check
that it is *right*: the structure was put in deliberately, so either the software recovers
it or it does not. That is a stronger claim, and it is the claim the paper makes.

## What comes from the literature

| Element | Source |
|---|---|
| Sampling design: 125 birds, 3 Denizli + 2 Gerze subpopulations | Kaya & Yıldız (2008) *Biochem Genet* 46:480–491 |
| Fragment-size range of ADL0268, ADL0278, LEI0094, LEI0166, MCW0034, MCW0069, MCW0216, MCW0248 | Zanetti et al. (2017) *Ital J Anim Sci* 17:57–63, Table 2 |
| Fragment-size range of MCW0037, MCW0111, MCW0206, MCW0295 | Korean 30-marker chicken panel |
| Target He: Denizli 0.656, Gerze 0.475; mean Na 7.5; PIC 0.610; fixation index 0.301 | Kaya & Yıldız (2008) |
| Target F<sub>IS</sub> ≈ 0.20, H<sub>O</sub> ≈ 0.47 | Zanetti et al. (2017) |
| Locus panel membership | ISAG/FAO recommended chicken microsatellite panel |

Every simulated allele call falls inside a fragment-size window that has actually been
reported for that locus in chicken, on the 2 bp grid appropriate to a dinucleotide repeat.

## What does not come from the literature

The genotypes. Allele frequencies are drawn from a Dirichlet distribution over each
locus's size grid, then diverged hierarchically — ancestral pool → breed → subpopulation —
under the Balding–Nichols model. Gerze receives the stronger drift coefficient and a
higher rate of rare-allele loss, so that its lower published diversity emerges rather than
being imposed. Genotypes are then sampled with a per-subpopulation inbreeding coefficient
and a 2.5% missing-call rate.

## Reproducing it

```
python3 simulate_denizli_gerze.py
```

Requires `numpy` and `openpyxl`. The seed is fixed (20260818), so the file regenerates
byte-identically. Changing the seed changes the data; changing the panel or the target
parameters changes what the benchmark tests.

## What MicroQuick returns on it

| Statistic | MicroQuick | Published for these breeds |
|---|---|---|
| Mean N<sub>a</sub> | 6.33 | 7.5 |
| Mean H<sub>E</sub> | 0.728 | 0.665 |
| Mean H<sub>O</sub> | 0.506 | 0.473 |
| Mean PIC | 0.683 | 0.610 |
| F<sub>IS</sub> | 0.177 | 0.200 |
| F<sub>IT</sub> | 0.305 | 0.301 |
| F<sub>ST</sub> | 0.157 | — |
| D<sub>EST</sub> | 0.381 | — |

Structure recovered:

- pairwise F<sub>ST</sub> 0.024–0.055 within Denizli, 0.030 within Gerze, 0.118–0.176 between breeds
- PC1 (19.2% of variance) separates the two breeds; subpopulations within a breed overlap
- k-means at K = 2 assigns individuals to their own breed with mean membership 0.77–0.83
- all 12 loci depart from HWE — the expected Wahlund effect from pooling five
  differentiated subpopulations, on top of the simulated inbreeding

The last row is worth dwelling on: a data set built to *contain* substructure produces
wholesale HWE rejection. That is the correct answer, and it is a good illustration of why
the HWE panel is a screening tool rather than a confirmatory test (see the limitations
section of the main README).
