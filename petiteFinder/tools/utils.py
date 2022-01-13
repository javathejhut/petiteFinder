import os
import json
import numpy as np
from mean_average_precision import MetricBuilder


def IOU(bbox1, bbox2):
    minr_1, minc_1, maxr_1, maxc_1 = bbox1
    minr_2, minc_2, maxr_2, maxc_2 = bbox2

    isOverlapped = (minc_1 <= maxc_2 and minc_2 <= maxc_1 and minr_1 <= maxr_2 and minr_2 <= maxr_1)

    if isOverlapped:
        left = max(minc_1, minc_2)
        right = min(maxc_1, maxc_2)
        top = min(maxr_1, maxr_2)
        bottom = max(minr_1, minr_2)

        intersect_area = abs(left - right) * abs(top - bottom)
        union = abs((maxr_1 - minr_1) * (maxc_1 - minc_1)) + abs((maxr_2 - minr_2) * (maxc_2 - minc_2)) - intersect_area

        return float(intersect_area) / union
    else:
        return 0.0


def get_precision_recall_grande_petite(IOU_threshold, gt_bboxes, pred_bboxes, gt_category_dict):
    # compute TP, FP, FN for precision and recall metrics per image

    precision_recall_g_p = {}  # output of form img_id: precision(grande), recall(grande), precision(petite),
    # recall(petite)

    for cat in gt_category_dict:
        if cat["name"] == 'g':
            grande_id = cat["id"]
        elif cat["name"] == 'p':
            petite_id = cat["id"]
        else:
            print("COCO CATEGORY MISMATCH")

    for image_id in gt_bboxes.keys():

        TP_p = 0
        TP_g = 0

        FP_p = 0
        FP_g = 0

        FN_p = 0
        FN_g = 0

        gt_grande_bboxes = [bbox[0:4] for bbox in gt_bboxes[image_id]
                            if bbox[4] == grande_id]
        gt_petite_bboxes = [bbox[0:4] for bbox in gt_bboxes[image_id]
                            if bbox[4] == petite_id]

        grande_bboxes = [bbox[0:4] for bbox in pred_bboxes[image_id]
                         if bbox[4] == grande_id]
        petite_bboxes = [bbox[0:4] for bbox in pred_bboxes[image_id]
                         if bbox[4] == petite_id]

        # grande TP FP calculations
        for g_pred in grande_bboxes:
            good_prediction = False
            for g_gt in gt_grande_bboxes:
                if IOU(g_pred, g_gt) > IOU_threshold:
                    TP_g += 1
                    good_prediction = True
                    break
            if not good_prediction:
                FP_g += 1

        # petite TP FP calculations
        for p_pred in petite_bboxes:
            good_prediction = False
            for p_gt in gt_petite_bboxes:
                if IOU(p_pred, p_gt) > IOU_threshold:
                    TP_p += 1
                    good_prediction = True
                    break
            if not good_prediction:
                FP_p += 1

        # FN calculations
        for g_gt in gt_grande_bboxes:
            good_prediction = False
            for g_pred in grande_bboxes:
                if IOU(g_pred, g_gt) > 0:
                    good_prediction = True
                    break
            if not good_prediction:
                FN_g += 1


        for p_gt in gt_petite_bboxes:
            good_prediction = False
            for p_pred in petite_bboxes:
                if IOU(p_pred, p_gt) > 0:
                    good_prediction = True
                    break
            if not good_prediction:
                FN_p += 1

        if TP_g > 0:
            precision_grande = float(TP_g) / (TP_g + FP_g)
            recall_grande = float(TP_g) / (TP_g + FN_g)
        else:
            if FN_g ==0:
                recall_grande = 1.0
            if FP_g==0:
                precision_grande = 1.0

        if TP_p > 0:

            precision_petite = float(TP_p) / (TP_p + FP_p)
            recall_petite = float(TP_p) / (TP_p + FN_p)

        else:
            if FN_p ==0:
                recall_petite = 1.0
            if FP_p==0:
                precision_petite = 1.0


        precision_recall_g_p[image_id] = [precision_grande, recall_grande, precision_petite, recall_petite]

    return precision_recall_g_p


def get_gt_category_dict(path_to_gt):
    with open(path_to_gt, 'rt', encoding='UTF-8') as gt:
        gt_json = json.load(gt)
        categories = gt_json["categories"]

        # index by zero instead of 1 (which is the labelme or labelme2coco default)
        for cat in categories:
            cat["id"] = cat["id"] - 1
    return categories


def get_gt_image_dict(path_to_gt):
    with open(path_to_gt, 'rt', encoding='UTF-8') as gt:
        gt_json = json.load(gt)
        images = gt_json["images"]
    return images


def get_gt_bboxes(path_to_gt):
    gt_bbox_dict = {}

    with open(path_to_gt, 'rt', encoding='UTF-8') as gt:
        gt_json = json.load(gt)
        gt_annotations = gt_json["annotations"]
        img_ids = [ele["id"] for ele in gt_json["images"]]

    # construct gt dict containing bbox entries in format [xmin, ymin, xmax, ymax, class_id, difficult, crowd]
    # per image ID
    for ID in img_ids:
        gt_bbox_dict[ID] = []

        for ann in gt_annotations:
            if int(ann["image_id"]) == int(ID):
                gt_bbox_dict[ID].append([int(ann["bbox"][0]),
                                         int(ann["bbox"][1]),
                                         int(ann["bbox"][0] + ann["bbox"][2]),
                                         int(ann["bbox"][1] + ann["bbox"][3]),
                                         ann["category_id"] - 1,
                                         0,
                                         ann["iscrowd"]])

    return gt_bbox_dict


def get_pred_bboxes_SAHI(path_to_pred, gt_category_dict, gt_img_dict):

    pred_bbox_dict = {}
    with open(path_to_pred, 'rt', encoding='UTF-8') as pred:
        pred_json = json.load(pred)

    # because sahi doesn't preserve image_ids... simply indexes by order in original json
    # sahi_imgid_to_gt_id = {}
    # for i, img in enumerate(gt_img_dict):
    #     sahi_imgid_to_gt_id[i + 1] = img["id"]

    # because sahi also doesn't preserve category ids
    sahi_cat_name_to_gt_id = {}
    for cat in gt_category_dict:
        sahi_cat_name_to_gt_id[cat["name"]] = cat["id"]

    gt_img_ids = [ele["id"] for ele in gt_img_dict]

    # do a similar construction for gt but for predictions with format [xmin, ymin, xmax, ymax, class_id, confidence]
    for imgID in gt_img_ids:
        pred_bbox_dict[imgID] = []

        for ann in pred_json:
            if int(ann["image_id"]) == int(imgID):
                pred_bbox_dict[imgID].append([int(ann["bbox"][0]),
                                              int(ann["bbox"][1]),
                                              int(ann["bbox"][0] + ann["bbox"][2]),
                                              int(ann["bbox"][1] + ann["bbox"][3]),
                                              sahi_cat_name_to_gt_id[ann["category_name"]],
                                              ann["score"]])
    return pred_bbox_dict


def get_petite_frequency_per_img(bbox_dict, gt_category_dict) -> dict:
    """
    Function for computing petite frequency in image.

    Args:
        bbox_dict (dict):
            key=image_id, value=[[xmin, ymin, xmax, ymax, class_id, difficult, crowd]...]

        gt_category_dict (dict):
            standard COCO categories dict format

    Returns:
        petite_freq_dict (dict): dict(key=image_id, value=float(petite frequency in image))

    """
    petite_freq_dict = {}
    for cat in gt_category_dict:
        if cat["name"] == 'g':
            grande_id = cat["id"]
        elif cat["name"] == 'p':
            petite_id = cat["id"]
        else:
            print("COCO CATEGORY MISMATCH")

    for img_id in bbox_dict.keys():
        grande_count = 0
        petite_count = 0
        for bbox in bbox_dict[img_id]:
            if bbox[4] == grande_id:
                grande_count += 1

            elif bbox[4] == petite_id:
                petite_count += 1

        petite_freq_dict[img_id] = float(petite_count) / (petite_count + grande_count)

    return petite_freq_dict


def get_category_count_per_img(bbox_dict, gt_category_dict, category_name) -> dict:
    """
    Function for computing count of object category in image ('g' or 'p').

    Args:
        bbox_dict (dict):
            key=image_id, value=[[xmin, ymin, xmax, ymax, class_id, difficult, crowd]...]

        gt_category_dict (dict):
            standard COCO categories dict format

        category_name (str):
            'p' or 'g'

    Returns:
        count_per_img_dict (dict): key=image_id, value=count of category_name objects in image

    """

    count_per_img_dict = {}
    assert category_name in [cat["name"] for cat in gt_category_dict], "category not in ground truth category dict"

    for cat in gt_category_dict:
        if cat["name"] == category_name:
            target_id = cat["id"]

    for img_id in bbox_dict.keys():
        target_cat_count = 0
        for bbox in bbox_dict[img_id]:
            if bbox[4] == target_id:
                target_cat_count += 1

        count_per_img_dict[img_id] = target_cat_count

    return count_per_img_dict


def get_COCO_mAP(gt_bbox_dict, pred_bbox_dict, gt_category_dict) -> dict:
    """
    Function for computing mean average precision (mAP) of Petite/Grande detection.

    Args:
        gt_bbox_dict (dict):
            key=image_id, value=[[xmin, ymin, xmax, ymax, class_id, difficult, crowd]...]


        pred_bbox_dict (dict):
            key=image_id, value=[[xmin, ymin, xmax, ymax, class_id, confidence]...]


        gt_category_dict (dict):
            standard COCO categories dict format

    Returns:
        to_return (list): [mAP@0.05:0.95, mAP@0.5, mAP@0.75]

    """

    metric_fn = MetricBuilder.build_evaluation_metric("map_2d", async_mode=False, num_classes=2)

    for key in gt_bbox_dict.keys():
        metric_fn.add(np.array(pred_bbox_dict[key]), np.array(gt_bbox_dict[key]))

    # compute metric COCO metrics
    mAP_total = metric_fn.value(iou_thresholds=np.arange(0.5, 0.95, 0.05), mpolicy='soft')['mAP']
    mAP_05 = metric_fn.value(iou_thresholds=0.5, mpolicy='soft')['mAP']
    mAP_075 = metric_fn.value(iou_thresholds=[0.75], mpolicy='soft')['mAP']

    for cat in gt_category_dict:
        if cat["name"] == 'g':
            grande_id = cat["id"]
        elif cat["name"] == 'p':
            petite_id = cat["id"]

    to_return = [mAP_total, mAP_05, mAP_075]

    return to_return
