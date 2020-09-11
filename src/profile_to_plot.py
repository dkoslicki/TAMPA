from ete3 import NCBITaxa, is_taxadb_up_to_date
from ProfilesLayout import ProfilesLayout
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, CircleFace, TextFace
import argparse
import os
#os.environ['QT_QPA_PLATFORM']='offscreen'
import seaborn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

import faulthandler

ncbi = NCBITaxa()




def build_tree(PF, rank_limit):


    return True

def generateFigure(PF, sample, rank, input_file, output_base_name, file_type, plot_l1, scaling, output_dpi):

    # Make the ETE3 tree
    try:
        tree = ncbi.get_topology(PF.get_all_tax_ids(sample), rank_limit=rank)

    except:
        logging.getLogger('Tampa').critical("Input format not compatible.")
        exit(1)

    ts = TreeStyle()
    ts.layout_fn = PF.layout
    ts.mode = "c"
    ts.show_leaf_name = False
    ts.show_branch_length = False
    ts.show_branch_support = False
    ts.min_leaf_separation = 10
    ts.arc_span = 360
    #ts.legend.add_face(CircleFace(100, "#1b9e77", label="Predicted"), column=0)
    #ts.legend.add_face(CircleFace(100, '#d95f02', label="True"), column=1)
    # add white space to move the legend closer
    ts.legend.add_face(CircleFace(65, "#FFFFFF"), column=2)
    ts.legend.add_face(CircleFace(65, "#FFFFFF"), column=1)
    ts.legend.add_face(CircleFace(65, "#FFFFFF"), column=0)
    ts.legend.add_face(CircleFace(65, "#FFFFFF"), column=2)
    ts.legend.add_face(CircleFace(65, "#FFFFFF"), column=1)
    ts.legend.add_face(CircleFace(65, "#FFFFFF"), column=0)

    # add the legend
    legend_fs = 50
    C1 = CircleFace(100, "#1b9e77")
    C1.hz_align = True
    ts.legend.add_face(C1, column=0)
    T1 = TextFace("Predicted", fsize=legend_fs)
    T1.hz_align = True
    ts.legend.add_face(T1, column=0)

    if len(PF.ground_truth_dict) > 0:
        C2 = CircleFace(100, "#d95f02")
        C2.hz_align = True
        ts.legend.add_face(C2, column=1)
        T2 = TextFace("True", fsize=legend_fs)
        T2.hz_align = True
        ts.legend.add_face(T2, column=1)

    T3 = TextFace(f"Tool: {os.path.basename(input_file).split('.')[0]}", fsize=legend_fs)
    T3.hz_align = True
    ts.legend.add_face(T3, column=0)
    ts.allow_face_overlap = False  # this lets me mess a bit with font size and face size without the interaction of the two
    ts.min_leaf_separation = 10
    tree_output_file = f"{output_base_name}_tree_{rank}_{sample}.{file_type}"
    tree.render(tree_output_file, h=5.2, w=5, tree_style=ts, units="in", dpi=output_dpi)


    if plot_l1:

        # if you asked for L1 too, then plot that
        true_abundance_at_rank = []
        predicted_abundance_at_rank = []
        for node in tree.get_leaves():
            if node.rank == rank:
                tax_id = str(node.taxid)
                if tax_id in PF.ground_truth_tax_id_to_percentage:
                    true_abundance_at_rank.append(PF.ground_truth_tax_id_to_percentage[str(node.taxid)] / 100.)
                else:
                    true_abundance_at_rank.append(0)
                if tax_id in PF.profile_tax_id_to_percentage:
                    predicted_abundance_at_rank.append(PF.profile_tax_id_to_percentage[str(node.taxid)] / 100.)
                else:
                    predicted_abundance_at_rank.append(0)

        data = np.zeros((len(true_abundance_at_rank), 2))
        data[:, 0] = np.array(true_abundance_at_rank)
        data[:, 1] = np.array(predicted_abundance_at_rank)

        df = pd.DataFrame(data, columns=['True', 'Predicted'])
        # g = seaborn.FacetGrid(df, height=6)
        ax = seaborn.scatterplot(x='True', y='Predicted', data=df, color='b', s=55)
        eps = 1
        ax.set_aspect('equal')
        max_val = np.max(data) + eps
        ax.set_xlim(-.5, max_val)
        ax.set_ylim(-.5, max_val)
        ax.set_xbound(-.5, max_val)
        ax.set_ybound(-.5, max_val)

        #plt.figure(figsize=(6,6))
        plt.plot(np.linspace(0, max_val, 100), np.linspace(0, max_val, 100), color='k')

        for (x, y) in zip(true_abundance_at_rank, predicted_abundance_at_rank):
            if x > y:
                ax.vlines(x, y, x, colors='r')
            if y > x:
                ax.vlines(x, x, y, colors='r')
        plt.title(f"Tool: {os.path.basename(input_file).split('.')[0]}")
        plt.tight_layout()
        l1_out_file = f"{output_base_name}_L1_{rank}.{file_type}"
        plt.savefig(l1_out_file, dpi=output_dpi)


def main():
    argparser = argparse.ArgumentParser(description='Plot abundance of profile against ground truth on taxonomic tree.')
    argparser.add_argument('-i', '--input_profile', type=str, help='Input taxonomic profile')
    argparser.add_argument('-g', '--ground_truth_input_profile', type=str, help='Input ground truth taxonoomic profile')
    argparser.add_argument('-b', '--output_base_name', type=str, help='Base name for output')
    argparser.add_argument('-t', '--file_type', type=str, default='png', help="File type for output images (svg, png, pdf, etc.")
    argparser.add_argument('-s', '--sample_of_interest', type=str, help="If you're only interested in a single sample of interest, specify here.")
    argparser.add_argument('-k', '--scaling', type=str, default='log', help="Plot scaling (log, sqrt, power etc.")
    argparser.add_argument('-a', '--labels', type=str, default='All', help="Specify this otion if you want to add labels to the graph (All, Leaf, None)")
    argparser.add_argument('-y', '--layout', type=str, default='Pie', help="Chose the layout of the graph (Pie, Bar, Circle, Rectangle")
    argparser.add_argument('-l', '--plot_l1', action='store_true', help="If you also want to plot the L1 error")
    argparser.add_argument("-n", "--normalize", help="specify this option if you want to normalize the node weights/relative abundances so that they sum to one", dest="normalize", action="store_true")
    argparser.add_argument("-m", "--merge", help="specify this option if you to average over all the @SampleID's and plot a single tree", dest="merge", action="store_true")
    argparser.add_argument('-d', '--db_file', type=str, default='', help="specify database dump file")
    argparser.add_argument('-r', '--res', type=str, default='800', help="specify the resolution (dpi)")
    argparser.add_argument('taxonomic_rank', type=str, help='Taxonomic rank to do the plotting at')


    # Parse the parameters
    params = argparser.parse_args()
    rank = params.taxonomic_rank
    #input_file = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/MS15.profile"
    input_file = params.input_profile
    #ground_truth = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/gs_marine_short.profile"
    ground_truth = params.ground_truth_input_profile
    #sample_of_interest = 'marmgCAMI2_short_read_sample_0'
    sample_of_interest = params.sample_of_interest
    scaling=params.scaling
    labels=params.labels
    layt=params.layout
    output_base_name = params.output_base_name
    plot_l1 = params.plot_l1
    file_type = params.file_type
    normalize = params.normalize
    merge = params.merge
    db_file=params.db_file
    output_dpi=int(params.res)

    
    # updates the ncbi taxdump database
    if not is_taxadb_up_to_date() or db_file != '':
        try:
            ncbi.update_taxonomy_database(db_file)
        except:
            if not os.path.exists(db_file):
                logging.getLogger('Tampa').critical("Database file does not exist.")
            else:
                logging.getLogger('Tampa').critical("Database file not compatible.")
            exit(1)

    # ingest the profiles information

    PF = ProfilesLayout(input_file, ground_truth, scaling, labels, layt,sample_of_interest=sample_of_interest, normalize=normalize)


    if sample_of_interest:
        sample_keys =  [sample_of_interest]
    elif merge:
        sample_keys = [None] #if merge is selected, then combine all samples into single merged sample
    else:
        sample_keys = PF.profile_dict.keys()

    #create a figure for each key on key_samples

    for sample in sample_keys:
        # print("sample=",sample)
        PF.make_tax_id_to_percentage(sample=sample, merge=merge)
        generateFigure(PF, sample, rank, input_file, output_base_name, file_type, plot_l1, scaling, output_dpi)




if __name__ == "__main__": main()
