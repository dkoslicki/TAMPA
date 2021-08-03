from ete3 import NCBITaxa, is_taxadb_up_to_date
from ProfilesLayout import ProfilesLayout
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, CircleFace, TextFace, PhyloTree, NodeStyle
import argparse
import os
#os.environ['QT_QPA_PLATFORM']='offscreen'
import seaborn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging


ncbi = NCBITaxa()

def myComparator(n):

    return n.percentage

def add_percentage(tree, PF):

    root = tree
    for node in root.get_descendants():

        if str(node.taxid) in PF.profile_tax_id_to_percentage and PF.profile_tax_id_to_percentage[str(node.taxid)]['percentage'] > 0.:
            node.add_feature("percentage", PF.profile_tax_id_to_percentage[str(node.taxid)]['percentage'])
        else:
            node.add_feature("percentage", .000000001)
        #print(node.name, node.percentage)

    return root

def get_top_nodes(tree, N=0):

    nodes_to_remove = set()

    root = tree

    if len(root.children) > N:
        children = []
        for child in root.children:
            children.append(child)

        children.sort(reverse=True, key=myComparator)

        for i in range(N, len(children)):
            nodes_to_remove.add(children[i].taxid)
            for child in children[i].get_descendants():
                nodes_to_remove.add(child.taxid)


    for n in root.get_descendants():

        if n.taxid not in nodes_to_remove and len(n.children) > N:

            children = []
            for child in n.children:
                children.append(child)

            children.sort(reverse=True, key=myFunc)

            for i in range(N, len(children)):
                nodes_to_remove.add(children[i].taxid)
                for child in children[i].get_descendants():
                    nodes_to_remove.add(child.taxid)


    for n in root.get_descendants():

        if n.taxid in nodes_to_remove:
            n.delete(prevent_nondicotomic=False)

    return root



def get_nodes_by_threshold(tree, thr=0.):

    nodes_to_remove = set()
    root = tree

    for n in root.get_descendants():

        if n.taxid not in nodes_to_remove:
            if n.percentage is not None and n.percentage < thr:
                nodes_to_remove.add(n.taxid)
                for child in n.get_descendants():
                    nodes_to_remove.add(child.taxid)



    for n in root.get_descendants():

        if n.taxid in nodes_to_remove:
            n.delete(prevent_nondicotomic=False)

    return root



def generateFigure(PF, sample, rank, input_file, output_base_name, file_type, plot_l1, scaling, output_dpi, use_profile, fw, fh, limit=None, limit_value=None):


    PF.make_tax_id_to_percentage(sample=sample)

    try:
        if use_profile:
            # Make the custom ETE3 tree
            tree = PF.build_tree(sample, rank_limit=rank)
        else:
            # Make the ETE3 tree
            tree = ncbi.get_topology(PF.get_all_tax_ids(sample), rank_limit=rank)

        tree = add_percentage(tree, PF)
    except:
        logging.getLogger('Tampa').critical("Input format not compatible.")
        exit(1)

    if limit == "top":
        tree = get_top_nodes(tree, N=limit_value)
    elif limit == "threshold":
        tree = get_nodes_by_threshold(tree, thr=limit_value)

    # removes the default node labels
    nstyle = NodeStyle()
    nstyle["fgcolor"] = "#FFFFFF"
    nstyle["size"] = 0

    for n in tree.traverse():
        n.set_style(nstyle)


    ts = TreeStyle()
    ts.layout_fn = PF.layout
    ts.mode = "c"
    ts.show_leaf_name = False
    ts.show_branch_length = False
    ts.show_branch_support = False
    ts.min_leaf_separation = PF.get_leaf_separation()
    ts.arc_span = 360
    ts.allow_face_overlap = False
    ts.branch_vertical_margin = PF.get_branch_margin()
    ts.show_scale = False

    # add the legend
    legend_fs = PF.get_font_size()
    label_size = PF.get_label_size()

    # add white space to move the legend closer
    ts.legend.add_face(CircleFace(label_size, "#FFFFFF"), column=2)
    ts.legend.add_face(CircleFace(label_size, "#FFFFFF"), column=1)
    ts.legend.add_face(CircleFace(label_size, "#FFFFFF"), column=0)
    ts.legend.add_face(CircleFace(label_size, "#FFFFFF"), column=2)
    ts.legend.add_face(CircleFace(label_size, "#FFFFFF"), column=1)
    ts.legend.add_face(CircleFace(label_size, "#FFFFFF"), column=0)

    C1 = CircleFace(label_size, "#1b9e77")
    C1.hz_align = True
    ts.legend.add_face(C1, column=0)
    T1 = TextFace("Predicted", fsize=legend_fs)
    T1.hz_align = True
    ts.legend.add_face(T1, column=0)

    if len(PF.ground_truth_dict) > 0:
        C2 = CircleFace(label_size, "#d95f02")
        C2.hz_align = True
        ts.legend.add_face(C2, column=1)
        T2 = TextFace("True", fsize=legend_fs)
        T2.hz_align = True
        ts.legend.add_face(T2, column=1)

    T3 = TextFace(f"Tool: {os.path.basename(input_file).split('.')[0]}", fsize=legend_fs)
    T3.hz_align = True
    ts.legend.add_face(T3, column=0)

    tree_output_file = f"{output_base_name}_tree_{rank}_{sample}.{file_type}"
    tree.render(tree_output_file, h=fh, w=fw, tree_style=ts, units="in", dpi=output_dpi)


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
    argparser.add_argument('-p', '--profile', action='store_true', help="specify this option to use only the input profile(s) taxID's to construct the tree")
    argparser.add_argument('-top', '--top', type=str, help="specify this option to display only the top nodes with highest abundance")
    argparser.add_argument('-thr', '--thr', type=str, help="specify this option to display only the nodes with abundance higher than threshold")
    argparser.add_argument('-fs', '--fontsize', type=str, default='12', help="specify this option to change the font size of the labels")
    argparser.add_argument('-ls', '--labelsize', type=str, default='20', help="specify this option to display only the nodes with abundance higher than threshold")
    argparser.add_argument('-lw', '--labelwidth', type=str, default='8', help="specify this option to display only the nodes with abundance higher than threshold")
    argparser.add_argument('-bm', '--branchmargin', type=str, default='0', help="specify this option to change the branch vertical margin")
    argparser.add_argument('-lsep', '--leaf_sep', type=str, default='10', help="specify this option to change the leaf separation")
    argparser.add_argument('-fh', '--figheight', type=str, default='5.2', help="specify this option to change the figure height (in)")
    argparser.add_argument('-fw', '--figwidth', type=str, default='5', help="specify this option to change the figure width (in)")
    argparser.add_argument('-nm', '--no_monitor', action='store_true', help='If you are running on a server or other monitor-less environment, use this flag to save directly to a file')
    argparser.add_argument('taxonomic_rank', type=str, help='Taxonomic rank to do the plotting at')


    # Parse the parameters
    params = argparser.parse_args()
    if params.no_monitor:
        os.environ['QT_QPA_PLATFORM']='offscreen'
    rank = params.taxonomic_rank
    input_file = params.input_profile
    ground_truth = params.ground_truth_input_profile
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
    use_profile = params.profile
    limit = None
    limit_value = None
    if params.top is not None:
        limit="top"
        limit_value=int(params.top)
    elif params.thr is not None:
        limit="threshold"
        limit_value=float(params.thr)
    fs = float(params.fontsize)
    ls = float(params.labelsize)
    bm = int(params.branchmargin)
    lw = float(params.labelwidth)
    fw = float(params.figwidth)
    fh = float(params.figheight)
    lsep = float(params.leaf_sep)


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
    PF = ProfilesLayout(input_file, ground_truth, scaling, labels, layt, normalize=normalize, fs=fs, ls=ls, bm=bm, lw=lw, lsep=lsep)

    if sample_of_interest:
        sample_keys =  [sample_of_interest]
    elif merge:
        PF.create_merged_sample() #if merge is selected, then combine all samples into single merged sample
        sample_keys = ["merged"]
        sample_of_interest = "merged"
    else:
        sample_keys = PF.get_sampleIDs()

    #create a figure for each key on key_samples
    for sample in sample_keys:
        generateFigure(PF, sample, rank, input_file, output_base_name, file_type, plot_l1, scaling, output_dpi, use_profile, fw, fh, limit, limit_value)


if __name__ == "__main__": main()
