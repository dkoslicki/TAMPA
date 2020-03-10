from ete3 import NCBITaxa
from ProfilesLayout import ProfilesLayout
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, CircleFace, TextFace

ncbi = NCBITaxa()

#def main():
input_file = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/MS16.profile"
ground_truth = "/home/dkoslicki/Data/CAMI2/meta_coder_analysis/profiles/marine_short/gs_marine_short.profile"
sample_of_interest = 'marmgCAMI2_short_read_sample_0'
PF = ProfilesLayout(input_file, ground_truth, sample_of_interest=sample_of_interest, normalize=True)

tree = ncbi.get_topology(PF.get_all_tax_ids())
ts = TreeStyle()
PF.make_tax_id_to_percentage()
ts.layout_fn = PF.layout
ts.mode = "c"
ts.show_leaf_name = False
ts.min_leaf_separation = 15
#ts.legend.add_face(CircleFace(100, "#1b9e77", label="Predicted"), column=0)
#ts.legend.add_face(CircleFace(100, '#d95f02', label="True"), column=1)
ts.legend.add_face(CircleFace(100, "#1b9e77"), column=0)
ts.legend.add_face(TextFace("Predicted", fsize=48), column=0)
ts.legend.add_face(CircleFace(100, "#d95f02"), column=1)
ts.legend.add_face(TextFace("True", fsize=48), column=1)
tree.show(tree_style=ts)




#if __name__ == "__main__": main()