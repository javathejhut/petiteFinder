import json
import os
from pathlib import Path
from tools import utils
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd() + os.sep, os.pardir))
target_folder = 'runs/GS_total'
output_folder = 'runs/'
p = Path(os.getcwd() + os.sep + target_folder + os.sep)

# get dictionaries of ground truth annotations (validate)
path_to_gt = os.path.normpath(PROJECT_ROOT + os.sep + 'COCO_dataset/annotations/validate.json')
gt_category_dict = utils.get_gt_category_dict(path_to_gt)
gt_img_dict = utils.get_gt_image_dict(path_to_gt)
gt_bbox_dict = utils.get_gt_bboxes(path_to_gt)

if os.path.isfile(output_folder + os.sep + "SAHI_sweep_results.txt"):
    os.remove(output_folder + os.sep + "SAHI_sweep_results.txt")

for folder in p.glob("*/"):
    folder_name = folder.name

    model_confidence_threshold = float(folder_name.split('_')[0])
    post_process_type = str(folder_name.split('_')[1])
    post_process_metric = str(folder_name.split('_')[2])
    post_process_threshold = float(folder_name.split('_')[3])

    for json_file in folder.rglob('*.json'):
        print("writing param combination + results to SAHI_sweep_results.txt")
        pred_bbox_dict = utils.get_pred_bboxes_SAHI(json_file, gt_category_dict, gt_img_dict)
        COCO_mAP = utils.get_COCO_mAP(gt_bbox_dict, pred_bbox_dict, gt_category_dict)
        # precision_recall_categories = utils.get_precision_recall_grande_petite(0.5, gt_bbox_dict, pred_bbox_dict,
        #                                                                        gt_category_dict)
        # print(precision_recall_categories)
        # grande_avg_precision = np.mean([precision_recall_categories[key][0]]
        #                                for key in precision_recall_categories.keys())
        # grande_avg_recall = np.mean([precision_recall_categories[key][1]]
        #                             for key in precision_recall_categories.keys())
        # petite_avg_precision = np.mean([precision_recall_categories[key][2]]
        #                                for key in precision_recall_categories.keys())
        # petite_avg_recall = np.mean([precision_recall_categories[key][3]]
        #                             for key in precision_recall_categories.keys())
        #
        # precision_recall_means = [grande_avg_precision, grande_avg_recall,
        #                           petite_avg_precision, petite_avg_recall]

        pred_petite_freqs = utils.get_petite_frequency_per_img(pred_bbox_dict, gt_category_dict)
        gt_petite_freqs = utils.get_petite_frequency_per_img(gt_bbox_dict, gt_category_dict)

        percent_difference = [abs(pred_petite_freqs[key] - gt_petite_freqs[key])
                              for key in gt_petite_freqs.keys()]

        avg_percent_error = np.mean(percent_difference)

        with open(output_folder + os.sep + "SAHI_sweep_results.txt", 'a') as output:
            output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(model_confidence_threshold,
                                                                   post_process_type,
                                                                   post_process_metric,
                                                                   post_process_threshold,
                                                                   *COCO_mAP,
                                                                   avg_percent_error))
