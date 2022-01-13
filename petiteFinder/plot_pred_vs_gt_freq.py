import os
from tools import utils
import numpy as np
import matplotlib.pyplot as plt
import math

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
category_counts_g = utils.get_category_count_per_img(gt_bbox_dict, gt_category_dict, 'g')
category_counts_p = utils.get_category_count_per_img(gt_bbox_dict, gt_category_dict, 'p')

average_colony_per_plate = int(np.mean([category_counts_g[key] + category_counts_p[key]
                                        for key in category_counts_g.keys()]))

print(average_colony_per_plate)

precision_recall_categories = utils.get_precision_recall_grande_petite(0.5, gt_bbox_dict, pred_bbox_dict,
                                                                       gt_category_dict)
pred_petite_freqs = utils.get_petite_frequency_per_img(pred_bbox_dict, gt_category_dict)
gt_petite_freqs = utils.get_petite_frequency_per_img(gt_bbox_dict, gt_category_dict)

COCO_mAP = utils.get_COCO_mAP(gt_bbox_dict, pred_bbox_dict, gt_category_dict)

print("\nimage_id: ground truth petite frequency, predicted petite frequency\n")
percent_errors = []
for key in pred_petite_freqs:
    print(key, gt_petite_freqs[key], pred_petite_freqs[key], abs(gt_petite_freqs[key]- pred_petite_freqs[key])*100)
    percent_errors.append(abs(gt_petite_freqs[key]- pred_petite_freqs[key]))

# print(np.mean(percent_errors), np.std(percent_errors))
#
# print("\nimage_id: grande precision, grande recall, petite precision, petite recall: \n")
# for key in precision_recall_categories.keys():
#     print(key, *precision_recall_categories[key])
#
# print("\nCOCO mAP, mAP@0.5, mAP@0.75")
# print(*COCO_mAP)
fig = plt.figure(figsize=(11, 7))
pred_petite_frequency = [pred_petite_freqs[key] for key in pred_petite_freqs.keys()]
gt_petite_frequency = [gt_petite_freqs[key] for key in pred_petite_freqs.keys()]

size = 30
zipped_lists = zip(gt_petite_frequency, pred_petite_frequency)
sorted_pairs = sorted(zipped_lists)

tuples = zip(*sorted_pairs)
ground_truth, predicted = [list(tuple) for tuple in tuples]

binom_std_error = [math.sqrt((ground_truth[i]) * (1 - ground_truth[i]) / average_colony_per_plate)
                   for i in range(len(ground_truth))]

print(binom_std_error)
plt.xticks(fontsize=size)
plt.yticks(fontsize=size, ticks=[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8])
plt.fill_between(np.arange(len(ground_truth)),
                 np.array(ground_truth)-np.array(binom_std_error),
                 np.array(ground_truth) + np.array(binom_std_error), color='k', alpha=0.5,
                 label='Binomial sampling error')
plt.text(6,0.1, "prediction error (mean): %2.3f\n"
                "prediction error (std): %2.3f\n"%(np.mean(percent_errors), np.std(percent_errors)),
                size=size-10)
plt.plot(np.arange(len(ground_truth)), ground_truth, marker='o', c='black', label='Ground truth')
plt.plot(np.arange(len(predicted)), predicted, marker='o', c='red', label='Predicted')
plt.ylabel("Petite frequency per image", fontsize=size - 5)
plt.xlabel("Plate image in test set (sorted by frequency)", fontsize=size - 5)
plt.legend(fontsize=size - 10)
plt.savefig("pred_gt_petite_frequencies.png", dpi=600, bbox_inches="tight")
