import load_data
from  load_data import Prediction
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, TextFace, PhyloTree
import numpy as np
schema_names = COLOR_SCHEMES.keys()


def abbreaviate_name(name):

    names = name.split(' ')
    abr_name = names[0][0]+'.'
    if len(names) > 1:
        for i in range(1,len(names)):
            abr_name += ' '+names[i]
    else:
        return name
    return abr_name



class ProfilesLayout:
    def __init__(self, scaling, labels, layt, sample_of_interest=None):

        self.profile_dict = dict()
        self.ground_truth_dict = dict()
        self.sample_of_interest = sample_of_interest
        self.scaling=scaling
        self.labels=labels
        self.layt=layt


    def load_data(self, profile_file, ground_truth_file, normalize=False):

        self.profile_dict = load_data.open_profile(profile_file, normalize=normalize)

        if ground_truth_file is not None:
            self.ground_truth_dict = load_data.open_profile(ground_truth_file, normalize=normalize)

        if self.sample_of_interest == "merged":
            self.create_merged_sample(self.profile_dict)
            self.create_merged_sample(self.ground_truth_dict)


    def get_sampleIDs(self):
        return self.profile_dict.keys()

    def create_merged_sample(self, sample_dict):

        merged_predictions = dict()
        samples = sample_dict.keys()

        for sample_id in samples:
            predictions = sample_dict[sample_id]['predictions']

            for prediction in predictions:
                tax_id = prediction.taxid

                if tax_id not in merged_predictions:
                    merged_predictions[tax_id] = dict()
                    merged_predictions[tax_id]["values"] = []

                merged_predictions[tax_id]["values"].append(prediction.percentage) # TODO: so they are fractions, not probabilities
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
            tax_id_to_percentage[tax_id]['percentage'] = prediction.percentage*100 # TODO: so they are fractions, not probabilities
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


    def build_tree(self, sample, rank_limit=None):

        # Gets taxids of sample.  Gets all taxids if sample is None.
        taxids = set(self.get_all_tax_ids(sample))

        taxid2nodes = {}
        all_nodes = {}
        root_children = []

        for taxid in taxids:
            taxid2nodes[taxid] = []

            taxpath = self.get_taxpath(taxid)

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
                if rank_limit and node.rank == rank_limit:
                    break
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
        #if not node.is_leaf():
        scale=self.scaling
        eps = .000000001
        node_taxid = str(node.taxid)

        if node_taxid in self.profile_tax_id_to_percentage and self.profile_tax_id_to_percentage[node_taxid]['percentage'] > 0.:
            if  (scale=="log"):
                size_profile = np.log(self.profile_tax_id_to_percentage[node_taxid]['percentage'])
            elif(scale=="sqrt"):
                size_profile = np.sqrt(self.profile_tax_id_to_percentage[node_taxid]['percentage'])
            elif(scale=="exponent"):
                size_profile = np.exp(self.profile_tax_id_to_percentage[node_taxid]['percentage'])
            elif(scale=="linear"):
                size_profile = (self.profile_tax_id_to_percentage[node_taxid]['percentage'])
        else:
            size_profile = eps

        if node_taxid in self.ground_truth_tax_id_to_percentage and self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'] > 0.:
            if  (scale=="log"):
                size_ground_truth = np.log(self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])
            elif(scale=="sqrt"):
                size_ground_truth = np.sqrt(self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])
            elif(scale=="exponent"):
                size_ground_truth = np.exp(self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])
            elif(scale=="linear"):
                size_ground_truth = (self.ground_truth_tax_id_to_percentage[node_taxid]['percentage'])
        else:
            size_ground_truth = eps

        print(size_profile, size_ground_truth)

        size = 50*max([size_ground_truth, size_profile])
        chart_sizes = np.array([size_profile, size_ground_truth])
        # print(np.sum(chart_sizes))
        if not np.sum(chart_sizes) == 0:
            chart_sizes = 100 * (chart_sizes / np.sum(chart_sizes))
            if(self.labels=="All"):
                F2 = TextFace(abbreaviate_name(node.sci_name), tight_text=True, fsize=500)  # use the scientific name
                faces.add_face_to_node(F2, node, column=0, position="branch-right")
            elif(self.labels=="Leaf"):
                if node.is_leaf():
                    F2 = TextFace(abbreaviate_name(node.sci_name), tight_text=True, fsize=500)  # use the scientific name
                    faces.add_face_to_node(F2, node, column=0, position="branch-right")
            # print(chart_sizes)

            if(self.layt=="Pie"):  # PIE CHART
                F = faces.PieChartFace(chart_sizes,colors=['#1b9e77', '#d95f02'],width=size, height=size)

            elif(self.layt=="Bar"):# BAR CHART
                F = faces.BarChartFace(chart_sizes, deviations=None, labels=None, colors=['#1b9e77', '#d95f02'],width=50, height=50, label_fsize=0, scale_fsize=0)

                #print(chart_sizes, node.sci_name)

            elif(self.layt=="Circle"): #TWO CIRCLES SIDE BY SIDE
                F=faces.CircleFace(radius=size_profile*10, color="#1b9e77", style='circle', label=None)
                F1=faces.CircleFace(radius=size_ground_truth*10, color="#d95f02", style='circle', label=None)
                F1.border.width = None
                F1.opacity = 0.6
                faces.add_face_to_node(F1, node, 0, position="float-behind")

            elif(self.layt=="Rectangle"): #TWO CIRCLES SIDE BY SIDE
                F=faces.RectFace(width=size_profile*40, height=40, fgcolor="#1b9e77",bgcolor="#1b9e77", label=None)
                F1=faces.RectFace(width=size_ground_truth*40, height=40, fgcolor="#d95f02",bgcolor="#d95f02", label=None)
                F1.border.width = None
                F1.opacity = 0.6
                faces.add_face_to_node(F1, node, 0, position="float-behind")


            faces.add_face_to_node(F, node, 0, position="float-behind")
            F.border.width = None
            F.opacity = 0.6
