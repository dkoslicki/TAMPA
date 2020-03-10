from ete3 import NCBITaxa
from ProfilesLayout import ProfilesLayout
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, CircleFace, TextFace
import argparse
import os, sys

ncbi = NCBITaxa()

def main():
    argparser = argparse.ArgumentParser(description='Plot abundance of profile against ground truth on taxonomic tree.')
    argparser.add_argument('-i', '--input_profile', type=str, help='Input taxonoomic profile')
    argparser.add_argument('-g', '--ground_truth_input_profile', type=str, help='Input ground truth taxonoomic profile')
    argparser.add_argument('-o', '--output_file', type=str, help='File for output (.svg, png, pdf, etc.')
    argparser.add_argument('-s', '--sample_of_interest', type=str, help="If you're only interested in a single sample of interest, specify here.")
    argparser.add_argument('taxonomic_rank', type=str, help='Taxonomic rank to do the plotting at')
    params = argparser.parse_args()
    rank = params.taxonomic_rank
    #input_file = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/MS15.profile"
    input_file = params.input_profile
    #ground_truth = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/gs_marine_short.profile"
    ground_truth = params.ground_truth_input_profile
    #sample_of_interest = 'marmgCAMI2_short_read_sample_0'
    sample_of_interest = params.sample_of_interest
    output_file = params.output_file

    PF = ProfilesLayout(input_file, ground_truth, sample_of_interest=sample_of_interest, normalize=True)

    tree = ncbi.get_topology(PF.get_all_tax_ids(), rank_limit=rank)
    ts = TreeStyle()
    PF.make_tax_id_to_percentage()
    ts.layout_fn = PF.layout
    ts.mode = "c"
    ts.show_leaf_name = False
    ts.min_leaf_separation = 10
    #ts.legend.add_face(CircleFace(100, "#1b9e77", label="Predicted"), column=0)
    #ts.legend.add_face(CircleFace(100, '#d95f02', label="True"), column=1)
    ts.legend.add_face(CircleFace(500, "#1b9e77"), column=0)
    ts.legend.add_face(TextFace("Predicted", fsize=124), column=0)
    ts.legend.add_face(CircleFace(500, "#d95f02"), column=1)
    ts.legend.add_face(TextFace("True", fsize=124), column=1)
    T = TextFace(f"{os.path.basename(input_file).split('.')[0]}", fsize=124)
    T.hz_align = True
    ts.legend.add_face(T, column=0)
    ts.optimal_scale_level = 'full'
    #tree.show(tree_style=ts)
    tree.render(output_file, h=5, w=5, tree_style=ts, units="in")
    #tree.render('out.svg', tree_style=ts)




if __name__ == "__main__": main()