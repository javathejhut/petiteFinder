import os
import json
import numpy as np
from mean_average_precision import MetricBuilder
from typing import List

path_to_gt = os.path.normpath(os.getcwd() + os.sep + 'COCO_dataset/annotations/test.json')
path_to_pred = os.path.normpath(os.getcwd() + os.sep + "petiteFinder/runs/predict/exp/result.json")

gt_bbox_dict = {}  # key:img_id,value:list(bboxes)
pred_bbox_dict = {}

gt_grande_count = []
gt_petite_count = []

pred_grande_count = []
pred_petite_count = []

with open(path_to_gt, 'rt', encoding='UTF-8') as gt:
    gt_json = json.load(gt)
    gt_annotations = gt_json["annotations"]
    img_ids = [ele["id"] for ele in gt_json["images"]]

    # sahi doesn't preserve image_ids...
    id_to_index = {}
    for i, ID in enumerate(img_ids):
        id_to_index[ID] = i + 1

# construct gt dict containing bbox entries in format [xmin, ymin, xmax, ymax, class_id, difficult, crowd] per image ID
for imgID in img_ids:
    gt_bbox_dict[id_to_index[imgID]] = []

    grande_count = 0
    petite_count = 0
    for ann in gt_annotations:
        if int(ann["image_id"]) == int(imgID):
            gt_bbox_dict[id_to_index[imgID]].append([int(ann["bbox"][0]),
                                                     int(ann["bbox"][1]),
                                                     int(ann["bbox"][0] + ann["bbox"][2]),
                                                     int(ann["bbox"][1] + ann["bbox"][3]),
                                                     ann["category_id"] - 1,
                                                     0,
                                                     ann["iscrowd"]])
            if ann["category_id"] == 1:
                grande_count += 1
            elif ann["category_id"] == 2:
                petite_count += 1

    gt_grande_count.append(grande_count)
    gt_petite_count.append(petite_count)

# do a similar construction for predictions but with format [xmin, ymin, xmax, ymax, class_id, confidence]
with open(path_to_pred, 'rt', encoding='UTF-8') as pred:
    pred_json = json.load(pred)

for imgID in img_ids:
    pred_bbox_dict[id_to_index[imgID]] = []
    grande_count = 0
    petite_count = 0

    for ann in pred_json:
        if int(ann["image_id"]) == int(id_to_index[imgID]):
            pred_bbox_dict[id_to_index[imgID]].append([int(ann["bbox"][0]),
                                                       int(ann["bbox"][1]),
                                                       int(ann["bbox"][0] + ann["bbox"][2]),
                                                       int(ann["bbox"][1] + ann["bbox"][3]),
                                                       ann["category_id"],
                                                       ann["score"]])
            if ann["category_id"] == 0:
                grande_count += 1
            elif ann["category_id"] == 1:
                petite_count += 1

    pred_grande_count.append(grande_count)
    pred_petite_count.append(petite_count)

percent_errors = []
for i in range(len(gt_grande_count)):
    gt_petite_frac = float(gt_petite_count[i]) / (gt_petite_count[i] + gt_grande_count[i])
    pred_petite_frac = float(pred_petite_count[i]) / (pred_petite_count[i] + pred_grande_count[i])

    if gt_petite_frac > 0:
        print(gt_petite_frac, pred_petite_frac, 100 * abs(pred_petite_frac - gt_petite_frac) / gt_petite_frac)
        percent_errors.append(100 * abs(pred_petite_frac - gt_petite_frac) / gt_petite_frac)
    elif gt_petite_frac == 0 and pred_petite_frac == 0:
        print(gt_petite_frac, pred_petite_frac, 0)
        percent_errors.append(0)

# now iterate through keys and add to metric builder
metric_fn = MetricBuilder.build_evaluation_metric("map_2d", async_mode=False, num_classes=2)

for key in gt_bbox_dict.keys():
    metric_fn.add(np.array(pred_bbox_dict[key]), np.array(gt_bbox_dict[key]))

# compute metric COCO metric
print(f"COCO mAP @0.5: {metric_fn.value(iou_thresholds=0.5, mpolicy='soft')['mAP']}")
print(f"COCO mAP @0.75: {metric_fn.value(iou_thresholds=0.75, mpolicy='soft')['mAP']}")

print("avg, median, std percent error in petite frequency across 17 test images (%):",
      np.mean(percent_errors),
      np.median(percent_errors),
      np.std(percent_errors))
