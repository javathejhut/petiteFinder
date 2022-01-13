import os
from tools import utils
import numpy as np

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
category_counts_g = utils.get_category_count_per_img(gt_bbox_dict, gt_category_dict,'g')
category_counts_p = utils.get_category_count_per_img(gt_bbox_dict, gt_category_dict,'p')

print(np.mean([category_counts_g[key]+ category_counts_p[key] for key in category_counts_g.keys()]))

precision_recall_categories = utils.get_precision_recall_grande_petite(0.5, gt_bbox_dict, pred_bbox_dict,
                                                                       gt_category_dict)
pred_petite_freqs = utils.get_petite_frequency_per_img(pred_bbox_dict,gt_category_dict)
gt_petite_freqs = utils.get_petite_frequency_per_img(gt_bbox_dict, gt_category_dict)

COCO_mAP = utils.get_COCO_mAP(gt_bbox_dict, pred_bbox_dict, gt_category_dict)

#print("\nimage_id: ground truth petite frequency, predicted petite frequency\n")
print("\navg mean, std in percent freq error:\n")
percent_errors = []
for key in pred_petite_freqs:
    #print(key, gt_petite_freqs[key], pred_petite_freqs[key], abs(gt_petite_freqs[key]- pred_petite_freqs[key])*100)
    percent_errors.append(abs(gt_petite_freqs[key]- pred_petite_freqs[key])*100)

print(np.mean(percent_errors), np.std(percent_errors))

print("\n(avg): grande precision, grande recall, petite precision, petite recall: \n")
#print("\nimage_id (avg): grande precision, grande recall, petite precision, petite recall: \n")
avg_metrics_class = []
for key in precision_recall_categories.keys():
    # print(precision_recall_categories[key][0], precision_recall_categories[key][1],
    #       precision_recall_categories[key][2], precision_recall_categories[key][3])
    avg_metrics_class.append(precision_recall_categories[key])

print(np.mean(np.array(avg_metrics_class)[:,0]), np.mean(np.array(avg_metrics_class)[:,1]),
      np.mean(np.array(avg_metrics_class)[:,2]), np.mean(np.array(avg_metrics_class)[:,3]))

    #print(key, *precision_recall_categories[key])

print("\nCOCO mAP, mAP@0.5, mAP@0.75")
print(*COCO_mAP)
