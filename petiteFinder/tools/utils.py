import os
import json
import numpy as np

def save_coco_json(dest, images=None, annotations=None, licenses=None, categories=None, info=None):

    if info is None:
        info = []
    if images is None:
        images = []
    if annotations is None:
        annotations = []
    if licenses is None:
        licenses = []
    if categories is None:
        categories = []

    with open(dest, 'wt', encoding='UTF-8') as coco_output:
        json.dump({'images': images, 'annotations': annotations, 'licenses': licenses, 'categories': categories,
                   'info': info}, coco_output, indent=2, sort_keys=True)

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


