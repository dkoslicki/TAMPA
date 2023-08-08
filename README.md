# TAMPA: **TA**xono**M**ic **P**rofiling **A**nalysis

> This repository contains the official python implementation of the following paper:
> Sarwal, Varuni, Jaqueline Brito, Serghei Mangul, and David J. Koslicki. **"TAMPA: interpretable analysis and visualization of metagenomics-based taxon abundance profiles."** bioRxiv (2022). <br>
> (https://www.biorxiv.org/content/10.1101/2022.04.28.489926v1.abstract) <br>


## Setup Environment and Install Dependencies

### Clone the repository

```bash
git clone https://github.com/dkoslicki/TAMPA.git
cd TAMPA
```


### Installation with Conda

Please follow the instructions at the following link to set up anaconda: [Anaconda Setup](https://docs.anaconda.com/anaconda/install/index.html)

The following commands create a conda environment inside the repository with the dependencies.

```bash
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda create -c etetoolkit -y -n CAMIViz python=3.7 numpy  ete3  seaborn pandas matplotlib biom-format
conda activate CAMIViz
```

### Installation with Bioconda
Waiting for pull request to get merged


### Example usage
```bash
python src/tampa.py -i data/mad_yalow_0.profile.txt -g data/gs_marine_short.profile.txt class -s marmgCAMI2_short_read_sample_0 -b marine_test -k linear -r 1600 -c False -o .
```
This should result in a plot that looks like:

<h1 align="center"><img src="./figures/metaphyler_CAMIhigh_tree_phylum_CAMI_HIGH_S001.png" width="75%"></h1>

TAMPA provides a "CONTRAST MODE" to better visualize the differences between the tool and gold standard. The contrast mode can be activated by setting the parameter c to True as follows

```bash
python src/tampa.py -i data/mad_yalow_0.profile.txt -g data/gs_marine_short.profile.txt class -s marmgCAMI2_short_read_sample_0 -b marine_test -k linear -r 1600 -c True -o .
```
This should result in a plot that looks like: 

<h1 align="center"><img src="./figures/metaphyler_CAMIhigh_normal_tree_phylum_CAMI_HIGH_S001.png" width="75%"></h1>

A comprehensive list of visualization options can be obtained using 
```bash
python src/tampa.py 
```
The options are as follows:

```bash

usage: tampa.py [-h] [-i INPUT_PROFILE] [-i1 INPUT_PROFILE1]
                [-g GROUND_TRUTH_INPUT_PROFILE] [-b OUTPUT_BASE_NAME]
                [-t FILE_TYPE] [-s SAMPLE_OF_INTEREST] [-k SCALING]
                [-a LABELS] [-y LAYOUT] [-l] [-n] [-m] [-d DB_FILE] [-r RES]
                [-p] [-top TOP] [-thr THR] [-fs FONTSIZE] [-ls LABELSIZE]
                [-lw LABELWIDTH] [-bm BRANCHMARGIN] [-lsep LEAF_SEP]
                [-fh FIGHEIGHT] [-fw FIGWIDTH] [-nm] [-o OUTPUT_PATH]
                [-dt HIGHLIGHT_DIFFERENCES_THRESHOLD] [-c CONTRAST]
                [-fir INPUT1] [-sec INPUT2]
                taxonomic_rank

Plot abundance of profile against ground truth on taxonomic tree.

positional arguments:
  taxonomic_rank        Taxonomic rank to do the plotting at

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PROFILE, --input_profile INPUT_PROFILE
                        Input taxonomic profile
  -i1 INPUT_PROFILE1, --input_profile1 INPUT_PROFILE1
                        Second (optional) input taxonomic profile1
  -g GROUND_TRUTH_INPUT_PROFILE, --ground_truth_input_profile GROUND_TRUTH_INPUT_PROFILE
                        Input ground truth taxonoomic profile
  -b OUTPUT_BASE_NAME, --output_base_name OUTPUT_BASE_NAME
                        Base name for output
  -t FILE_TYPE, --file_type FILE_TYPE
                        File type for output images (svg, png, pdf, etc.
  -s SAMPLE_OF_INTEREST, --sample_of_interest SAMPLE_OF_INTEREST
                        If you're only interested in a single sample of
                        interest, specify here.
  -k SCALING, --scaling SCALING
                        Plot scaling (log, sqrt, power etc.
  -a LABELS, --labels LABELS
                        Specify this otion if you want to add labels to the
                        graph (All, Leaf, None)
  -y LAYOUT, --layout LAYOUT
                        Chose the layout of the graph (Pie, Bar, Circle,
                        Rectangle
  -l, --plot_l1         If you also want to plot the L1 error
  -n, --normalize       specify this option if you want to normalize the node
                        weights/relative abundances so that they sum to one
  -m, --merge           specify this option if you to average over all the
                        @SampleID's and plot a single tree
  -d DB_FILE, --db_file DB_FILE
                        specify database dump file
  -r RES, --res RES     specify the resolution (dpi)
  -p, --profile         specify this option to use only the input profile(s)
                        taxID's to construct the tree
  -top TOP, --top TOP   specify this option to display only the top nodes with
                        highest abundance
  -thr THR, --thr THR   specify this option to display only the nodes with
                        abundance higher than threshold
  -fs FONTSIZE, --fontsize FONTSIZE
                        specify this option to change the font size of the
                        labels
  -ls LABELSIZE, --labelsize LABELSIZE
                        specify this option to display only the nodes with
                        abundance higher than threshold
  -lw LABELWIDTH, --labelwidth LABELWIDTH
                        specify this option to display only the nodes with
                        abundance higher than threshold
  -bm BRANCHMARGIN, --branchmargin BRANCHMARGIN
                        specify this option to change the branch vertical
                        margin
  -lsep LEAF_SEP, --leaf_sep LEAF_SEP
                        specify this option to change the leaf separation
  -fh FIGHEIGHT, --figheight FIGHEIGHT
                        specify this option to change the figure height (in)
  -fw FIGWIDTH, --figwidth FIGWIDTH
                        specify this option to change the figure width (in)
  -nm, --no_monitor     If you are running on a server or other monitor-less
                        environment, use this flag to save directly to a file
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Output path
  -dt HIGHLIGHT_DIFFERENCES_THRESHOLD, --highlight_differences_threshold HIGHLIGHT_DIFFERENCES_THRESHOLD
                        If at any rank the two input samples have a difference
                        in abundance greater than or equal to N percent, this
                        taxa will be highlighted
  -c CONTRAST, --contrast CONTRAST
                        contrast mode for comparison with gold standard
  -fir INPUT1, --input1 INPUT1
                        Name of the first input
  -sec INPUT2, --input2 INPUT2
                        Name of the second input
```
### Options to condense visualization in case of large datasets

1. -thr: This option can be used to display only the nodes with abundance higher than a particular threshold
2. -c: Contrast mode can be used to identify problematic subregions of large trees. In the contrast mode, the false positive taxas are represented as red circles, the false negative taxas as blue circles, true positives as white, and the remaining taxas in a gradient of white to green, with the color intensity proportional to the relative error.
3. -top: This option can be used to display only the top nodes with highest abundance
