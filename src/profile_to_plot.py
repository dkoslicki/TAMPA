from ete3 import NCBITaxa
from ProfilesLayout import ProfilesLayout
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES

ncbi = NCBITaxa()

#def main():
input_file = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/MS16.profile"
ground_truth = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/gs_marine_short.profile"
sample_of_interest = 'marmgCAMI2_short_read_sample_0'
PF = ProfilesLayout(input_file, ground_truth, sample_of_interest=sample_of_interest, normalize=False)

tree = ncbi.get_topology(PF.get_all_tax_ids())
ts = TreeStyle()
PF.make_tax_id_to_percentage()
ts.layout_fn = PF.layout
ts.mode = "c"
ts.show_leaf_name = True
ts.min_leaf_separation = 15
tree.show(tree_style=ts)



#if __name__ == "__main__": main()