import os
import json
import numpy as np
import pandas as pd
from sahi.utils.cv import visualize_object_predictions


def save_coco_json(dest, prefix, images=None, annotations=None, licenses=None, categories=None, info=None):
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

    with open(os.path.normpath(os.path.join(dest, prefix+"_predicted.json")) , 'wt', encoding='UTF-8') as coco_output:
        json.dump({'images': images, 'annotations': annotations, 'licenses': licenses, 'categories': categories,
                   'info': info}, coco_output, indent=2, sort_keys=True)


def save_freq_csv(coco_dict, dest, prefix):

    cat_dicts=[get_category_count_per_img(coco_dict, 'g'), get_category_count_per_img(coco_dict, 'p')]

    raw_df = pd.concat([pd.DataFrame(cat, index=[0]) for cat in cat_dicts], axis=0)
    complete_df = raw_df.T

    complete_df.index.name = 'filename'
    id_to_filename_map = {img_id: file_name for (img_id, file_name) in [[entry["id"], entry["file_name"]]
                                                                        for entry in coco_dict["images"]]}

    complete_df.index = complete_df.index.to_series().map(id_to_filename_map)
    complete_df.columns = ['grande_count', 'petite_count']

    complete_df = complete_df.assign(
        percent_petite=complete_df['petite_count'] / (complete_df['grande_count'] + complete_df['petite_count']))
    complete_df = complete_df.assign(
        total_count=(complete_df['grande_count'] + complete_df['petite_count']))

    complete_df.to_csv(os.path.normpath(os.path.join(dest, prefix+"_freq.csv")))

# def save_annotated_images()
#     output_dir = str(visual_dir / Path(relative_filepath).parent)
#     visualize_object_predictions(
#         np.ascontiguousarray(image_as_pil),
#         object_prediction_list=object_prediction_list,
#         rect_th=visual_bbox_thickness,
#         text_size=visual_text_size,
#         text_th=visual_text_thickness,
#         output_dir=output_dir,
#         file_name=filename_without_extension,
#         export_format=visual_export_format,
#     )

def get_category_count_per_img(coco_dict, category_name) -> dict:
    """
    Function for computing count of object category in image ('g' or 'p').

    Args:
        coco_dict (dict):
            standard coco json dict format

        category_name (str):
            'p' or 'g'

    Returns:
        count_per_img_dict (dict): key=image_id, value=count of category_name objects in image

    """

    count_per_img_dict = {}
    assert category_name in ['g', 'p'], "category not in ground truth category dict"

    img_ids = [entry["id"] for entry in coco_dict["images"]]
    annotations = [entry for entry in coco_dict["annotations"]]

    for img_id in img_ids:
        category_count = 0
        for ann in annotations:
            if ann["image_id"] == img_id:
                if ann["category_name"] == category_name:
                    category_count+=1
        count_per_img_dict[img_id] = category_count

    return count_per_img_dict
