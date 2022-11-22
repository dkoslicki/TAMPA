# TAMPA: **TA**xono**M**ic **P**rofiling **A**nalysis

> This repository contains the official python implementation of the following paper:
> Sarwal, Varuni, Jaqueline Brito, Serghei Mangul, and David J. Koslicki. **"TAMPA: interpretable analysis and visualization of metagenomics-based taxon abundance profiles."** bioRxiv (2022). <br>
> (https://www.biorxiv.org/content/10.1101/2022.04.28.489926v1.abstract) <br>


## Setup Environment and Install Dependencies

### Clone the repository

```bash
git clone git@github.com:dkoslicki/TAMPA.git
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

###
