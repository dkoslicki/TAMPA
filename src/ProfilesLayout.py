import load_data
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES
import numpy as np

schema_names = COLOR_SCHEMES.keys()


class ProfilesLayout:
    def __init__(self, profile_file, ground_truth_file, sample_of_interest=None, normalize=False):
        self.profile_dict = load_data.open_profile_from_tsv(profile_file, normalize=normalize)
        self.ground_truth_dict = load_data.open_profile_from_tsv(ground_truth_file, normalize=normalize)
        self.sample_of_interest = sample_of_interest

    def get_tax_ids(self, prfl_dict):
        all_taxids = set()
        if self.sample_of_interest:
            predictions = prfl_dict[self.sample_of_interest]['predictions']
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

    def get_all_tax_ids(self):
        all_taxids = self.get_tax_ids(self.profile_dict)
        all_taxids.update(self.get_tax_ids(self.ground_truth_dict))
        return all_taxids

    def predictions_to_tax_id(self, predictions):
        tax_id_to_percentage = dict()
        for prediction in predictions:
            tax_id = prediction.taxid
            percentage = prediction.percentage
            tax_id_to_percentage[tax_id] = percentage
        return tax_id_to_percentage

    def make_tax_id_to_percentage(self):
        self.profile_tax_id_to_percentage = dict()
        self.ground_truth_tax_id_to_percentage = dict()
        if self.sample_of_interest:
            predictions = self.profile_dict[self.sample_of_interest]['predictions']
            self.profile_tax_id_to_percentage = self.predictions_to_tax_id(predictions)
            predictions = self.ground_truth_dict[self.sample_of_interest]['predictions']
            self.ground_truth_tax_id_to_percentage = self.predictions_to_tax_id(predictions)
        else:  # otherwise, take the average
            pass  # FIXME: do this later, since I will need to keep track of how many are added to get the mean
            #for sample in self.profile_dict.keys():
            #    temp_dict = self.profile_dict[sample]['predictions']
            #    for (key, value) in temp_dict.items()
            #        if key in self.profile_tax_id_to_percentage

    def layout(self, node):
        if not node.is_leaf():
            node_taxid = str(node.taxid)
            size = 0
            if node_taxid in self.profile_tax_id_to_percentage:
                size_profile = self.profile_tax_id_to_percentage[node_taxid]
            else:
                size_profile = 0
            if node_taxid in self.ground_truth_tax_id_to_percentage:
                size_ground_truth = self.ground_truth_tax_id_to_percentage[node_taxid]
            else:
                size_ground_truth = 0
            size = size_profile + size_ground_truth
            chart_sizes = np.array([size_profile, size_ground_truth])
            chart_sizes = chart_sizes/np.sum(chart_sizes)

            F = faces.PieChartFace(chart_sizes,  # TODO: populate these with the prediction probabilities
                                   colors=COLOR_SCHEMES['brbg'],
                                   width=size, height=size)
            F.border.width = None
            F.opacity = 0.6
            faces.add_face_to_node(F, node, 0, position="float")
