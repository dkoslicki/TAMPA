import load_data
from  load_data import Prediction
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, TextFace, PhyloTree
import numpy as np
schema_names = COLOR_SCHEMES.keys()


def abbreaviate_name(name):

    names = name.split(' ')
    abbr_name = names[0][0]+'.'
    if len(names) > 1:
        for i in range(1,len(names)):
            abbr_name += ' '+names[i]
    else:
        return name
    return abbr_name


class ProfilesLayout:
    def __init__(self, profile_file, ground_truth_file, scaling, labels, layt, normalize=False, fs=500, ls=1., bm=0, lw=1., lsep=10):

        self.profile_dict = dict()
        self.ground_truth_dict = dict()
        self.scaling = scaling
        self.labels = labels
        self.layt = layt
        self.font_size = fs
        self.label_size = ls
        self.branch_margin = bm
        self.label_width = lw
        self.leaf_separation = lsep

        self.profile_dict = load_data.open_profile(profile_file, normalize=normalize)

        if ground_truth_file is not None:
            self.ground_truth_dict = load_data.open_profile(ground_truth_file, normalize=normalize)

        self.rank_position = {'superkingdom':0,'phylum':1, 'class':2, 'order':3,
                              'family':4, 'genus':5, 'species':6, 'strain':7, 'None':8}

    def get_font_size(self):
        return self.font_size

    def get_label_size(self):
        return self.label_size

    def get_branch_margin(self):
        return self.branch_margin

    def get_leaf_separation(self):
        return self.leaf_separation

    def get_sampleIDs(self):
        return self.profile_dict.keys()

    def create_merged_sample(self):
        self.merge_samples(self.profile_dict)
        self.merge_samples(self.ground_truth_dict)


    def merge_samples(self, sample_dict):

        merged_predictions = dict()
        samples = sample_dict.keys()

        for sample_id in samples:
            predictions = sample_dict[sample_id]['predictions']

            for prediction in predictions:
                tax_id = prediction.taxid

                if tax_id not in merged_predictions:
                    merged_predictions[tax_id] = dict()
                    merged_predictions[tax_id]["values"] = []

                merged_predictions[tax_id]["values"].append(prediction.percentage)
                merged_predictions[tax_id]['rank'] = prediction.rank
                merged_predictions[tax_id]['taxpath'] = prediction.taxpath
                merged_predictions[tax_id]['taxpathsn'] = prediction.taxpathsn

        sample_dict["merged"] = dict()
        sample_dict["merged"]['predictions'] = []
        sample_dict["merged"]['metadata'] = "merged sample"

        for taxid in merged_predictions.keys():

            values = merged_predictions[taxid]['values']

            prediction = Prediction()
            prediction.taxid = taxid
            prediction.rank = merged_predictions[taxid]['rank']
            prediction.percentage = np.mean(values)
            prediction.taxpath = merged_predictions[taxid]['taxpath']
            prediction.taxpathsn = merged_predictions[taxid]['taxpathsn']

            sample_dict["merged"]["predictions"].append(prediction)

    def get_tax_ids(self, prfl_dict, sample=None):

        all_taxids = set()

        if sample in prfl_dict.keys():
            predictions = prfl_dict[sample]['predictions']
            for prediction in predictions:
                tax_id = prediction.taxid
                try:  # some of these aren't actually taxID's, like 181234.123, so make sure to not include those
                    tax_id_int = int(tax_id)
                    all_taxids.add(prediction.taxid)
                except ValueError:
                    continue
        else:
            for sample in prfl_dict.keys():
                predictions = prfl_dict[sample]['predictions']
                for prediction in predictions:
                    tax_id = prediction.taxid
                    try:  # some of these aren't actually taxID's, like 181234.123, so make sure to not include those
                        tax_id_int = int(tax_id)
                        all_taxids.add(prediction.taxid)
                    except ValueError:
                        continue
        return all_taxids

    def get_all_tax_ids(self, sample=None):
        all_taxids = self.get_tax_ids(self.profile_dict, sample)
        all_taxids.update(self.get_tax_ids(self.ground_truth_dict, sample))
        return all_taxids


    def predictions_to_tax_id(self, type, sample=None):

        tax_id_to_percentage = dict()

        if type == 'profile':
            sample_dict = self.profile_dict
        else:
            sample_dict = self.ground_truth_dict

        merged_predictions = dict()

        predictions = sample_dict[sample]['predictions']

        for prediction in predictions:
            tax_id = prediction.taxid
            tax_id_to_percentage[tax_id] = dict()
            tax_id_to_percentage[tax_id]['percentage'] = prediction.percentage # TODO: so they are fractions, not probabilities
            tax_id_to_percentage[tax_id]['rank'] = prediction.rank
            tax_id_to_percentage[tax_id]['taxpath'] = prediction.taxpath
            tax_id_to_percentage[tax_id]['taxpathsn'] = prediction.taxpathsn

        return tax_id_to_percentage


    def make_tax_id_to_percentage(self, sample=None):

        self.profile_tax_id_to_percentage = dict()
        self.ground_truth_tax_id_to_percentage = dict()
        self.profile_tax_id_to_percentage = self.predictions_to_tax_id('profile', sample)
        self.ground_truth_tax_id_to_percentage = self.predictions_to_tax_id('ground_truth', sample)


    def get_taxpath(self, tax_id):

        if tax_id in self.profile_tax_id_to_percentage.keys():
            return list(self.profile_tax_id_to_percentage[tax_id]['taxpath'].split('|'))

        if tax_id in self.ground_truth_tax_id_to_percentage.keys():
            return list(self.ground_truth_tax_id_to_percentage[tax_id]['taxpath'].split('|'))

        return []

    def get_rank(self, tax_id):

        if tax_id in self.profile_tax_id_to_percentage.keys():
            return self.profile_tax_id_to_percentage[tax_id]['rank']

        if tax_id in self.ground_truth_tax_id_to_percentage.keys():
            return self.ground_truth_tax_id_to_percentage[tax_id]['rank']

        return "no rank"

    def get_name(self, tax_id):

        if tax_id in self.profile_tax_id_to_percentage.keys():
            return self.profile_tax_id_to_percentage[tax_id]['taxpathsn'].split('|')[-1]

        if tax_id in self.ground_truth_tax_id_to_percentage.keys():
            return self.ground_truth_tax_id_to_percentage[tax_id]['taxpathsn'].split('|')[-1]

        return "no sci_name"


    def build_tree(self, sample, rank_limit='None'):

        # Gets taxids of sample.  Gets all taxids if sample is None.
        taxids = set(self.get_all_tax_ids(sample))

        taxid2nodes = {}
        all_nodes = {}
        root_children = []

        for taxid in taxids:
            taxid2nodes[taxid] = []

            taxpath = self.get_taxpath(taxid)
            rank = self.get_rank(taxid)

            if self.rank_position[rank] <= self.rank_position[rank_limit]:

                for node_id in taxpath:

                    if node_id != '':

                        if node_id not in all_nodes:
                            node = all_nodes.setdefault(node_id, PhyloTree())
                            node.name = str(node_id)
                            node.taxid = node_id
                            rank = self.get_rank(node_id)
                            node.add_feature("rank", rank)
                            node.add_feature("sci_name", self.get_name(node_id))

                            if rank == 'superkingdom':
                                root_children.append(node)

                        else:
                            node = all_nodes[node_id] # node already exists

                        taxid2nodes[taxid].append(node)

        # generate parent child relationships
        for taxid in taxid2nodes.keys():
            parent = None
            for node in taxid2nodes[taxid]:
                if parent and node not in parent.children:
                    parent.add_child(node)
                parent = node

        root = PhyloTree()
        root.name = 'root'
        root.taxid = '0'
        root.add_feature("rank", "root")
        root.add_feature("sci_name", "root")

        for child in root_children:
            root.add_child(child)

        tree = root
        if len(root.children) == 1:
            tree = root.children[0].detach()

        return tree




    def layout(self, node):

        scale=self.scaling
        eps = .000000001
        node_taxid = str(node.taxid)

        if node_taxid in self.profile_tax_id_to_percentage and self.profile_tax_id_to_percentage[node_taxid]['percentage'] > 0.:
            if  (scale=="log"):
                size_profile = (np.log(self.profile_tax_id_to_percentage[node_taxid]['percentage'])+9.)/11.*self.label_size
            elif(scale=="sqrt"):
                size_profile = (np.sqrt(self.profile_tax_id_to_percentage[node_taxid]['percentage'])-0.0000316227766)/10*self.label_size
            elif(scale=="exponent"):
                size_profile = (np.exp(self.profile_tax_id_to_percentage[node_taxid]['percentage'])-1.000000001)/np.exp(100)*self.label_size
            elif(scale=="linear"):
                size_profile = (self.profile_tax_id_to_percentage[node_taxid]['percentage'])/100*self.label_size
        else:
            size_profile = eps

        if node_taxid in self.ground_truth_tax_id_to_percentage and self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'] > 0.:
            if  (scale=="log"):
                size_ground_truth = (np.log(self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])+9.)/11.*self.label_size
            elif(scale=="sqrt"):
                size_ground_truth = (np.sqrt(self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])-0.0000316227766)/10*self.label_size
            elif(scale=="exponent"):
                size_ground_truth = (np.exp(self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])-1.000000001)/np.exp(100)*self.label_size
            elif(scale=="linear"):
                size_ground_truth = (self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])/100*self.label_size
        else:
            size_ground_truth = eps




        chart_sizes = np.array([size_profile, size_ground_truth])

        if not np.sum(chart_sizes) == 0:
            chart_sizes = 100 * (chart_sizes / np.sum(chart_sizes))

            if(self.labels=="All"):
                F2 = TextFace(abbreaviate_name(node.sci_name), tight_text=True, fsize=self.font_size)  # use the scientific name
                faces.add_face_to_node(F2, node, column=0, position="branch-right")

            elif(self.labels=="Leaf"):
                if node.is_leaf():
                    F2 = TextFace(abbreaviate_name(node.sci_name), tight_text=True, fsize=self.font_size)  # use the scientific name
                    faces.add_face_to_node(F2, node, column=0, position="branch-right")

            if(self.layt=="Pie"):  # PIE CHART

                size = max([size_profile, size_ground_truth])
                F = faces.PieChartFace(chart_sizes,colors=['#1b9e77', '#d95f02'],width=size, height=size)

            elif(self.layt=="Circle"): #TWO CIRCLES SIDE BY SIDE
                F=faces.CircleFace(radius=size_profile, color="#1b9e77", style='circle', label=None)
                F1=faces.CircleFace(radius=size_ground_truth, color="#d95f02", style='circle', label=None)
                F1.border.width = None
                F1.opacity = 0.6
                faces.add_face_to_node(F1, node, 0, position="float-behind")

            elif(self.layt=="Rectangle"): #TWO CIRCLES SIDE BY SIDE

                F=faces.RectFace(width=size_profile, height=self.label_width, fgcolor="#1b9e77",bgcolor="#1b9e77", label=None)
                F1=faces.RectFace(width=size_ground_truth, height=self.label_width, fgcolor="#d95f02",bgcolor="#d95f02", label=None)
                F1.border.width = None
                F1.opacity = 0.6
                faces.add_face_to_node(F1, node, 0, position="float-behind")


            faces.add_face_to_node(F, node, 0, position="float-behind")
            F.border.width = None
            F.opacity = 0.6
