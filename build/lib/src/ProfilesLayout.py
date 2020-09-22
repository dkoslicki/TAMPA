import load_data
from ete3 import Tree, faces, TreeStyle, COLOR_SCHEMES, TextFace
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
    def __init__(self, profile_file, ground_truth_file, scaling,labels, layt, sample_of_interest=None, normalize=False):
        self.profile_dict = load_data.open_profile(profile_file, normalize=normalize)
        self.ground_truth_dict = dict()
        if ground_truth_file is not None:
            self.ground_truth_dict = load_data.open_profile(ground_truth_file, normalize=normalize)
        self.sample_of_interest = sample_of_interest
        self.scaling=scaling
        self.labels=labels
        self.layt=layt

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
        #if not node.is_leaf():
        scale=self.scaling
        eps = .000000001
        node_taxid = str(node.taxid)

        if node_taxid in self.profile_tax_id_to_percentage and self.profile_tax_id_to_percentage[node_taxid] > 0.:
            if  (scale=="log"):
                size_profile = np.log(self.profile_tax_id_to_percentage[node_taxid])
            elif(scale=="sqrt"):
                size_profile = np.sqrt(self.profile_tax_id_to_percentage[node_taxid])
            elif(scale=="exponent"):
                size_profile = np.exp(self.profile_tax_id_to_percentage[node_taxid])
            elif(scale=="linear"):
                size_profile = (self.profile_tax_id_to_percentage[node_taxid])
        else:
            size_profile = eps

        if node_taxid in self.ground_truth_tax_id_to_percentage and self.ground_truth_tax_id_to_percentage[node_taxid] > 0.:
            if  (scale=="log"):
                size_ground_truth = np.log(self.ground_truth_tax_id_to_percentage[node_taxid])
            elif(scale=="sqrt"):
                size_ground_truth = np.sqrt(self.ground_truth_tax_id_to_percentage[node_taxid])
            elif(scale=="exponent"):
                size_ground_truth = np.exp(self.ground_truth_tax_id_to_percentage[node_taxid])
            elif(scale=="linear"):
                size_ground_truth = (self.ground_truth_tax_id_to_percentage[node_taxid])
        else:
            size_ground_truth = eps

        size = 25*max([size_ground_truth, size_profile])
        chart_sizes = np.array([size_profile, size_ground_truth])
        # print(np.sum(chart_sizes))
        if not np.sum(chart_sizes) == 0:
            chart_sizes = 100 * (chart_sizes / np.sum(chart_sizes))
            if(self.labels=="All"):
                F2 = TextFace(abbreaviate_name(node.sci_name), tight_text=True, fsize=20)  # use the scientific name
                faces.add_face_to_node(F2, node, column=0, position="branch-right")
            elif(self.labels=="Leaf"):
                if node.is_leaf():
                    F2 = TextFace(abbreaviate_name(node.sci_name), tight_text=True, fsize=20)  # use the scientific name
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
