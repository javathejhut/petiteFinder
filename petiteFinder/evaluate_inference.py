import os
from tools import utils

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd() + os.sep, os.pardir))

path_to_gt = os.path.normpath(PROJECT_ROOT + os.sep + 'COCO_dataset/annotations/test.json')
path_to_pred = os.path.normpath(os.getcwd() + os.sep + "runs/test_exp/result.json")

# necessary dictionaries to do gt ID to SAHI ID mapping
gt_category_dict = utils.get_gt_category_dict(path_to_gt)
gt_img_dict = utils.get_gt_image_dict(path_to_gt)

gt_bbox_dict = utils.get_gt_bboxes(path_to_gt)
pred_bbox_dict = utils.get_pred_bboxes_SAHI(path_to_pred, gt_category_dict, gt_img_dict)

# coco_metrics = evaluate_inference.return_COCO_eval_metrics(gt_bbox_dict, pred_bbox_dict, gt_category_dict)
# print(coco_metrics)

precision_recall_categories = utils.get_precision_recall_grande_petite(0.5, gt_bbox_dict, pred_bbox_dict,
                                                                       gt_category_dict)
pred_petite_freqs = utils.get_petite_frequency_per_img(pred_bbox_dict,gt_category_dict)
gt_petite_freqs = utils.get_petite_frequency_per_img(gt_bbox_dict, gt_category_dict)

COCO_mAP = utils.get_COCO_mAP(gt_bbox_dict, pred_bbox_dict, gt_category_dict)

print("\nimage_id: ground truth petite frequency, predicted petite frequency\n")
for key in pred_petite_freqs:
    print(key, gt_petite_freqs[key], pred_petite_freqs[key])

print("\nimage_id: grande precision, grande recall, petite precision, petite recall: \n")
for key in precision_recall_categories.keys():
    print(key, *precision_recall_categories[key])

print("\nCOCO mAP, mAP@0.5, mAP@0.75")
print(*COCO_mAP)
