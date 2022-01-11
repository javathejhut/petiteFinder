import json
import os
from pathlib import Path
from tools import utils

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

        with open(output_folder + os.sep + "SAHI_sweep_results.txt", 'a') as output:
            output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(model_confidence_threshold,
                                                           post_process_type, post_process_metric,
                                                           post_process_threshold, *COCO_mAP))

