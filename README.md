MicroQuick

A single-file browser application that turns a table of scored microsatellite (SSR) genotypes into the standard quality-control, diversity, differentiation and structure summary — with nothing to install and no data leaving the computer.

Version 1.1.0 · MIT licence · diploid codominant markers

MicroQuick is written for people who hold genotype tables but do not program: conservation practitioners, 
breed-society and hatchery managers, genetic-monitoring programmes, and students. It does not replace R 
(adegenet, hierfstat, pegas), Genepop, Arlequin, GenAlEx or STRUCTURE. It gives the routine first report in a 
reproducible way, and exports the data to Genepop and STRUCTURE formats for everything it does not do.
⸻
1. Installation

There is none.
1. Download MicroQuick.html from the latest release (about 1.2 MB).
2. Double-click it. It opens in your web browser (Chrome, Edge, Firefox or Safari).
3. Work offline if you wish: the file contains everything it needs and never contacts a server.

To check the last point yourself, open the browser's developer tools (F12) → Network tab, run an analysis, and 
confirm that the list stays empty. node tests/e2e.js performs the same check automatically.

2. Five-minute tutorial
1. Open MicroQuick.html and press Load example (simulated) — or drop your own .csv, .tsv or .xlsx file.
Panel 2 shows what was read: individuals, loci, populations, and any warning (half-scored genotypes, 
1. non-numeric cells, very small populations). Press Run analysis.
Open Data quality first. It lists Hardy–Weinberg tests for every locus in every population, linkage 
1. disequilibrium between every pair of loci, null-allele estimates, and missing data.
2. A locus failing HWE in most populations → suspect a technical problem (null allele, scoring).
3. A population failing at most loci → suspect inbreeding or a mixed sample.
4. If a locus or population should be left out, click its chip in panel 2 and press Run analysis again.
Read the other tabs, then press Report .xlsx. The Run_info sheet stores the version, file name, 
selection, settings and random seed — keep it with your monitoring records so that next year's sample can 
1. be analysed in exactly the same way.

A longer walk-through with interpretation notes is in docs/USER_GUIDE.md; the same 
text is available inside the application under Guide.

3. Input format

One row per individual. Either
individualPopulationLocA(1)LocA(2)LocB(1)LocB(2)Ind_01North148150201201Ind_02North150150
or one column per locus with both alleles in a cell (148/150). Population and individual columns are 
optional. Missing genotype: empty cell, 0, NA, ? or -9. A genotype with only one allele scored is treated 
as missing and counted in a warning. Alleles must be numbers (fragment size or repeat count). 
CSV files may use comma, semicolon or tab as separator. Only diploid data are supported.

4. What is computed
OutputEstimatorPrimary sourceValidated againstNa, Ne, Shannon Icount; 1/Σp²; −Σp ln pKimura & Crow 1964adegenetHo, He, uHedirect count; 1−Σp²; 2N/(2N−1)·HeNei 1973, 1978adegenet, pegasPIC1−Σp²−ΣΣ2pᵢ²pⱼ²Botstein et al. 1980formulaAllelic richnessrarefaction to the smallest number of gene copiesEl Mousadik & Petit 1996hierfstatHWE, per locus × populationχ² with k(k−1)/2 df; Monte Carlo exact probability testGuo & Thompson 1992pegas, GenepopLinkage disequilibriumG test on genotype tables, permutation; Fisher's method across populationsRaymond & Rousset 1995GenepopNull-allele frequency(uHe−Ho)/(1+uHe), per populationBrookfield 1996formulaHo, Hs, Ht, FIS, GSTNei & Chesser corrected gene diversitiesNei 1987hierfstatG″ST, Jost's Dstandardised / allelic differentiationMeirmans & Hedrick 2011; Jost 2008hierfstat, mmodf, θ, Fvariance componentsWeir & Cockerham 1984hierfstat, pegas95% confidence intervalspercentile bootstrap over lociWeir & Cockerham 1984hierfstatTests of θ (global, pairwise)permutation of individuals among populationsExcoffier et al. 1992—Multiple testingBonferroni, Benjamini–Hochberg, Benjamini–YekutieliBenjamini & Hochberg 1995; Narum 2006R p.adjustPCAcentred individual allele frequenciesJombart 2008adegenet / ade4k-means + BIC, DAPCclustering and discriminant analysis of principal componentsJombart et al. 2010adegenet
All statistical code was written for MicroQuick in plain JavaScript (src/microquick_core.js, about 500 
lines, no dependencies). No code was taken from the packages in the last column; they were used only as 
references to test against. The two bundled third-party libraries do no statistics: SheetJS 0.18.5 
(Apache-2.0) reads and writes spreadsheets, Chart.js 4.4.0 (MIT) draws the plots.

5. Validation
node tests/unit.js              # 47 hand-checkable cases
node tests/e2e.js               # the built HTML in headless Chrome: no errors, no network, UI == core
bash validation/run_all.sh      # every statistic against adegenet, hierfstat, pegas, mmod and Genepop
node tests/null_calibration.js  # type-I error of the permutation tests under simulated null hypotheses
node tests/benchmark_runtime.js # run times in headless Chrome
node tests/xbrowser.js .        # same checks in Firefox and WebKit (needs `npm i playwright`)

Arlequin. validation/external/ compares MicroQuick with Arlequin 3.5.2.2 (arlecore, the console version from 
cmpg.unibe.ch). make_inputs.py writes the data sets as Arlequin projects, make_ars.py the settings files, 
run_arlequin_lima.sh runs arlecore (on Apple-silicon Macs inside an x86_64 Linux VM created with Lima), and 
compare_arlequin.py compares the results. genalex/ holds the same data sets in GenAlEx 6.5 layout, the add-in, 
step-by-step instructions (GenAlEx needs a few clicks in Excel), compare_genalex.py, and in genalex/results/ 
the GenAlEx 6.51b2 output workbooks for the benchmark and the cat data set used in the paper.

Version 1.1.0 was tested in Chrome 157, Firefox 132 and WebKit 18.2 (Safari's engine): identical results in all three, 
including the seeded Monte Carlo p values.

validation/run_all.sh analyses three data sets (a simulated benchmark, and the empirical nancycats and 
microbov data sets distributed with adegenet) and nine simulated scenarios (unequal sample sizes, 5% and 20% 
missing genotypes, weak and strong differentiation, inbreeding, monomorphic loci). Results are written to 
validation/out/; concordance_all.csv is the table reported in the paper. For every statistic whose 
estimator is identical in the reference package, the largest difference over all twelve data sets is below 
5 × 10⁻⁵ (the rounding of one reference function); see the paper for the stochastic tests.

6. Limits
– Diploid codominant data only; no haploid, polyploid or dominant markers.
– No model-based ancestry (STRUCTURE/ADMIXTURE), AMOVA, effective population size, relatedness or parentage.
– Bootstrap intervals are over loci and are unreliable with fewer than about ten loci.
– Private-allele counts are not rarefied.
– Monte Carlo p values have a floor of 1/(permutations + 1).
– Run time grows with the number of permutation tests; see validation/out/runtime.csv.

7. Repository layout
MicroQuick.html      the release file (built by build.py; do not edit by hand)
src/                 microquick_core.js (statistics) · ui.js (interface) · shell.html (page and styles)
vendor/              SheetJS and Chart.js, unmodified
build.py             inlines src/ and vendor/ into MicroQuick.html
data/                validation data sets in MicroQuick CSV format
benchmark/           simulated Denizli/Gerze benchmark and its generator
tests/               unit, end-to-end, runtime benchmark, figure screenshots
validation/          R scripts comparing MicroQuick with reference software, and their outputs
docs/                user guide

8. Citation

Please cite the MicroQuick paper (see CITATION.cff) and the primary source of each statistic you report.

9. Licence

MIT — see LICENSE.
