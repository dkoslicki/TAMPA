import load_data
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, TextFace
import numpy as np

schema_names = COLOR_SCHEMES.keys()


class ProfilesLayout:
    def __init__(self, profile_file, ground_truth_file, temp, sample_of_interest=None, normalize=False):
        self.profile_dict = load_data.open_profile(profile_file, normalize=normalize)
        self.ground_truth_dict = dict()
        if ground_truth_file is not None:
            self.ground_truth_dict = load_data.open_profile(ground_truth_file, normalize=normalize)
        self.sample_of_interest = sample_of_interest
        self.scale=temp
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

    def predictions_to_tax_id(self, predictions):
        tax_id_to_percentage = dict()
        for prediction in predictions:
            tax_id = prediction.taxid
            percentage = prediction.percentage
            tax_id_to_percentage[tax_id] = 100*percentage  # TODO: so they are fractions, not probabilities
        return tax_id_to_percentage

    def make_tax_id_to_percentage(self, sample=None, merge=False):

        self.profile_tax_id_to_percentage = dict()
        self.ground_truth_tax_id_to_percentage = dict()
        if sample is not None:
            # populate for the profile
            predictions = self.profile_dict[sample]['predictions']
            self.profile_tax_id_to_percentage = self.predictions_to_tax_id(predictions)

            # populate for the ground truth
            if sample in self.ground_truth_dict.keys():
                predictions = self.ground_truth_dict[sample]['predictions']
                self.ground_truth_tax_id_to_percentage = self.predictions_to_tax_id(predictions)
        else:  # otherwise, take the average

            merged_predictions = dict()

            for sample in self.profile_dict.keys():
                predictions = self.profile_dict[sample]['predictions']
                for prediction in predictions:
                    if prediction.taxid not in merged_predictions:
                        merged_predictions[prediction.taxid]=[]
                    merged_predictions[prediction.taxid].append(prediction.percentage)

            for taxid in merged_predictions.keys():
                values = merged_predictions[taxid]
                merged_predictions[taxid] = np.mean(values)

            self.profile_tax_id_to_percentage = merged_predictions


            merged_predictions = dict()

            for sample in self.ground_truth_dict.keys():
                predictions = self.ground_truth_dict[sample]['predictions']
                for prediction in predictions:
                    if prediction.taxid not in merged_predictions:
                        merged_predictions[prediction.taxid]=[]
                    merged_predictions[prediction.taxid].append(prediction.percentage)

            for taxid in merged_predictions.keys():
                values = merged_predictions[taxid]
                merged_predictions[taxid] = np.mean(values)


            self.ground_truth_tax_id_to_percentage = merged_predictions


    def layout(self, node):
        scale=self.scale
        #if not node.is_leaf():
        eps = .000000001
        node_taxid = str(node.taxid)

        if(self.scale=="log"):
            if node_taxid in self.profile_tax_id_to_percentage and self.profile_tax_id_to_percentage[node_taxid] > 0.:
                size_profile = np.log(self.profile_tax_id_to_percentage[node_taxid])  # TODO: log scale ok?
            else:
                size_profile = eps
            if node_taxid in self.ground_truth_tax_id_to_percentage and self.ground_truth_tax_id_to_percentage[node_taxid] > 0.:
                size_ground_truth = np.log(self.ground_truth_tax_id_to_percentage[node_taxid])  # TODO: log scale ok?
            else:
                size_ground_truth = eps

        elif (self.scale=="sqrt"):
            if node_taxid in self.profile_tax_id_to_percentage and self.profile_tax_id_to_percentage[node_taxid] > 0.:
                size_profile = np.sqrt(self.profile_tax_id_to_percentage[node_taxid]) 
            else:
                size_profile = eps
            if node_taxid in self.ground_truth_tax_id_to_percentage and self.ground_truth_tax_id_to_percentage[node_taxid] > 0.:
                size_ground_truth = np.sqrt(self.ground_truth_tax_id_to_percentage[node_taxid]) 
            else:
                size_ground_truth = eps
        
        elif (self.scale=="exponent"):
            if node_taxid in self.profile_tax_id_to_percentage and self.profile_tax_id_to_percentage[node_taxid] > 0.:
                size_profile = np.exp(self.profile_tax_id_to_percentage[node_taxid]) 
            else:
                size_profile = eps
            if node_taxid in self.ground_truth_tax_id_to_percentage and self.ground_truth_tax_id_to_percentage[node_taxid] > 0.:
                size_ground_truth = np.exp(self.ground_truth_tax_id_to_percentage[node_taxid]) 
            else:
                size_ground_truth = eps        

        size = 500*max([size_ground_truth, size_profile])
        chart_sizes = np.array([size_profile, size_ground_truth])
        print(np.sum(chart_sizes))
        if not np.sum(chart_sizes) == 0:
            chart_sizes = 100 * (chart_sizes / np.sum(chart_sizes))
            F2 = TextFace(node.sci_name, tight_text=True, fsize=68)  # use the scientific name
            faces.add_face_to_node(F2, node, column=0, position="branch-right")
            print(chart_sizes)
            F = faces.PieChartFace(chart_sizes,
                                   colors=['#1b9e77', '#d95f02'],width=size, height=size)

            F.border.width = None
            F.opacity = 0.6
            faces.add_face_to_node(F, node, 0, position="float-behind")
